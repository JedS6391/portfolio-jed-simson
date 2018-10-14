Title:   LGP - Asynchronous Training using Kotlin Coroutines
Summary: Details about the implementation of asynchronous training in the LGP system using Kotlin coroutines
Author:  Jed Simson
Date:    October 14, 2018
Tags:    LGP, Kotlin, Coroutines, Asynchronous, Training, Async

## Background

During my undergraduate studies at the University of Waikato, I built a [system](https://github.com/JedS6391/LGP/tree/master) for performing Linear Genetic Programming (LGP). The system was developed to offer an open-source implementation of LGP and was submitted as my Honours project.

LGP is a paradigm of genetic programming that employs a representation of linearly sequenced instructions in automatically generated programs. A population of imperative style programs are trained on a particular dataset and the best resulting program can be used as a predictor for the problem at hand.

The system performs well overall, but one issue that had always bugged me was that training was performed synchronously and would block until completion, meaning it was difficult to communicate progress of the training process back to the initiator --- a useful functionality for a machine learning library to have.

For example, if the library was to be used in the context of a GUI, the implementation would have no way to indicate progress and would have to wait until the training was complete.

## Solution

The system is built with [Kotlin](https://kotlinlang.org/), which is nearing its 1.3 release where the [coroutine API](https://kotlinlang.org/docs/reference/coroutines/coroutines-guide.html) will move from experimental to stable. This is exciting news as coroutines are a useful building block for modelling asynchronous computation --- exactly what I wanted in the LGP system!

The LGP system offers the concept of a `Trainer` which given some `EvolutionModel` (a particular evolutionary algorithm) and an `Environment` in which to perform evolution, will encapsulate the task of actually performing training.

There are two built-in implementations of this abstract class --- `SequentialTrainer` and `DistributedTrainer`. `SequentialTrainer` as the name suggests, is capable of training a given number of models sequentially (i.e. a model is trained, and then the next for some number of runs). `DistributedTrainer` extends upon this and will train each model in its own thread to increase the throughput of training. 

The solution I decided upon was to add an additional function to a `Trainer` which would return a `TrainingJob`, which represents the training computation performed by the `Trainer`. The usage would be something like:

<pre>
<code class="kotlin">val runner = DistributedTrainer(environment, model, runs = 2)

// We use runBlocking so that we have a CoroutineContext 
// for the async training to be performed in.
return runBlocking {
	val job = runner.trainAsync(dataset)

	// The training coroutine(s) can communicate progress to which
	//  we can subscribe callback function(s).
   job.subscribeToUpdates { println("training progress = ${it.progress}") }

	// Wait until training is done. When the trainer needs to 
	// communicate back to us, the training process will be suspended.
	// Alternatively, we could perform other computations here.
   val result = job.result()
}</code>
</pre>

The new `trainAsync` function has the signature:

<pre>
<code class="kotlin">abstract suspend fun trainAsync(dataset: Dataset&lt;TProgram&gt;): TrainingJob&lt;TProgram, TMessage&gt;</code>
</pre>

So, how does this work behind the scenes?

## Implementation

### SequentialTrainer

The `SequentialTrainer` implementation is less complicated than the `DistributedTrainer` as it launches a single coroutine that performs all training.

Here, there are two main requirements that I wanted to fulfil:

1. Training can be executed while the initiator continues to perform other computation.
2. The training process can communicate back to the initiator using messages. For the built-in trainers, the focus is communicating progress.

The first step was relatively simple --- we can just run the existing training computation in a coroutine using Kotlin's `async` builder:

<pre>
<code class="kotlin">val job = GlobalScope.async {
	// Training process here...
	
	// Return the result once everything is done.
	TrainingResult(results, models)
}</code>
</pre>

The `async` builder will return a `Deferred<TrainingResult>`, which essentially means a `TrainingResult` that will be given once the asynchronous computation is completed, whenever that may be.

Step two is a little trickier. Kotlin's `ConflatedBroadcastChannel` allows a sender to communicate to multiple receivers that have subscribed to the channel. Using this channel, the training coroutine (step 1) can communicate to the initiator like so:

<pre>
<code class="kotlin">// ProgressUpdate is our message type, a simple data class left out for brevity.
val progressChannel = ConflatedBroadcastChannel&lt;ProgressUpdate&lt;TProgram&gt;&gt;()

val job = GlobalScope.async {
	// Training process here...
	
	// Communicate messages to the initiator
	progressChannel.send(
		ProgressUpdate(progress, result)
	)
	
	// Return the result once everything is done.
	TrainingResult(results, models)
}

// Subscribe to the channel
val subscription = progressChannel.openSubscription()

// Launch a seperate coroutine for handling messages

GlobalScope.launch {
	subscription.consumeEach(callback)
}</code>
</pre>

To break down what's going on here:

- The training coroutine will send progress update messages to the channel.
- The training initiator launches a coroutine that will listen to the broadcast channel while it is open and consume any messages received.

This logic is implemented in the `SequentialTrainingJob` class to simplify some of these operations, but the core logic remains the same.

### DistributedTrainer

The fundamental concept behind the asynchronous training remains the same as for the `SequentialTrainer`, but there a few more complexities to take care of:

- We need to launch multiple training process as their own coroutines, to prevent training being performed sequentially.
- The training processes need to coordinate progress messages so that the progress received is correct (e.g. not out-of-order).

As before, step one isn't too complicated. The `DistributedTrainer` essentially makes `n` copies of the model given (where `n` is the number of runs to perform) and trains each independently. We simply launch multiple coroutines which perform their own training process:

<pre>
<code class="kotlin">val jobs = this.models.mapIndexed { run, model ->
	// Perform the training process...
}</code>
</pre>

The only real difference here is that there are multiple jobs (coroutines) --- one for each model being trained.

The second step is slightly tricker in this scenario as there are multiple training coroutines that want to send updates to the progress channel. However, we need to ensure that the progress is calculated correctly. To remove this burden from the training process (i.e. we don't want to be managing locks, etc), we use the built in `actor` implementation. 

The idea here is that there is a single actor which the training processes send messages to. It is the actors responsibility to maintain state about the current progress and update its internal state as messages from the training processes comes in. Each time a message is received by the actor, it will forward the message on the broadcast channel similarly to in the sequential implementation. To simplify the details, the actor is encapsulated in a class:

<pre>
<code class="kotlin">private class TrainingProgressUpdateActor<TProgram>(
    private val totalRuns: Int,
    private val progressChannel: ConflatedBroadcastChannel&lt;ProgressUpdate&lt;TProgram&gt;&gt;
) {
    private var completedTrainers = 0
    // The progress that all trainers share. 
    // Any updates should be broadcast on the progress channel.
    private var progress = 0.0

    suspend fun onReceive(message: ProgressUpdate&lt;TProgram&gt;) {
        // Basically, we ignore the progress value in the message for any 
        // legitimate updates and let the actor control the progress.
        this.completedTrainers = if (message.result != null) {
            this.completedTrainers + 1
        } else {
            this.completedTrainers
        }

        this.progress = (completedTrainers.toDouble() / this.totalRuns.toDouble()) * 100.0

        // Let any subscribers know about the new update.
        this.progressChannel.send(
            ProgressUpdate(progress, message.result)
        )
    }
}</code>
</pre>

<pre>
<code class="kotlin">val progressChannel = ConflatedBroadcastChannel&lt;ProgressUpdate&lt;TProgram&gt;&gt;()

// Our actor will manage the training progress state.
val progressActor = GlobalScope.actor&lt;ProgressUpdate&lt;TProgram&gt;&gt; {
    with (TrainingProgressUpdateActor(this@DistributedTrainer.runs, progressChannel)) {
        consumeEach { message ->
            onReceive(message)
        }
    }
}

val jobs = this.models.mapIndexed { run, model ->
	// Perform the training process...
	
	// Send a progress update. The actor manages progress, so
	// the value sent is arbitrary.
	progressActor.send(
		ProgressUpdate(Double.MIN_VALUE, result)
	)
}

// Subscribe to the channel.
// Any messages received will be sent from the actor.
val subscription = progressChannel.openSubscription()

// Launch a seperate coroutine for handling messages
GlobalScope.launch {
	subscription.consumeEach(callback)
}</code>
</pre>

Instead of leaving the trainers to compute their own progress, we move that responsibility to the actor which is better situated to track the current progress. It keeps state about how many of the training coroutines have completed and this can be used to compute an overall progress metric.

## Conclusion

While this post gives the implementation details, the actual implementation differs slightly to make the API more streamlined and simplify the codebase, however the general concept remains the same.

The Kotlin coroutine API deliberately provides low-level primitives so that it is up to the user to decide how they are used to structure asynchronous computation. This worked really well in my case as I could easily achieve the outcome I wanted, but abstract the details in the way that best worked for *this* system and API design.

Feel free to check out my [LGP implementation](https://github.com/JedS6391/LGP/tree/master) or the [documentation](https://lgp.jedsimson.co.nz/api/html/lgp.core.evolution.training/index.html) of the training APIs for more information!