Title:   Building a .NET client for reddit
Summary: Details the reddit client implementation in .NET that I've been working on
Author:  Jed Simson
Date:    July 04, 2021
Tags:    Reddit, API, Client, Project, C#, .NET, DotNet

## Background

I've been interested in the [reddit API](https://www.reddit.com/dev/api/oauth) for a while, as it is a site I interact with frequently and has a few interesting details in its implementation. 

In the past, I've used the [Python Reddit API Wrapper (PRAW)](https://praw.readthedocs.io/en/latest/) to create [an API for accessing saved reddit posts](https://github.com/JedS6391/reddit-saved-post-viewer-api), as well as numerous other quick scripts for analysing reddit data.

As a challenge to myself, I decided to build my own client library for interacting with reddit with the following goals:

- Built with .NET 5.0
- Simple, modern, asynchronous API
- Support for various authentication modes
- Modular structure with simple re-usable components

This post expands on the details behind the decisions made during implementation of the client, as well as some of the technical challenges faced.

## Implementation

### Designing a simple client API

The reddit API offers a wide range of functionality which could result in a complicated client class, if all the functions were available through a single entry-point. Taking inspiration from the PRAW API, the client API is split up into *interactors* responsible for specific high-level concepts e.g. subreddits, users, etc.

This has a number of benefits:

- The client API is logically grouped by the interactions one can have with reddit
- The API has a model for exposing functionality that is consistent, regardless of the specific interaction 
- The interactions can be split into individual *interactor* classes to simplify the code structure
- Functionality can be easily shared between interactors (e.g. voting on a submission or comment performs the same underlying API calls)

See the [`Interactions` namespace](https://github.com/JedS6391/Reddit.NET/tree/master/src/Reddit.NET.Client/Interactions) to see how interactors are implemented.

### Asynchronous-first API

One of the main goals of the project was to design an API that made it clear where asynchronous operations (i.e. HTTP requests) occur. The [.NET async programming model](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/async/task-asynchronous-programming-model) makes this easy by utilising the `Task` or `Task<T>` abstractions where appropriate.

The client exposes paginated data through the [`IAsyncEnumerable<T>` abstraction](https://docs.microsoft.com/en-us/dotnet/api/system.collections.generic.iasyncenumerable-1?view=net-5.0). This is intended to make it transparent that enumerating the paginated data is an async operation, as HTTP requests may be made to retrieve more data as necessary.

See the [`ListingEnumerable` class](https://github.com/JedS6391/Reddit.NET/blob/master/src/Reddit.NET.Client/Models/Public/Abstract/ListingEnumerable.cs) for more details on how the client uses `IAsyncEnumerable<T>`.

### Polymorphic deserialization with `System.Text.Json`

Some reddit API endpoints return arrays of data that may be of varying types (e.g. an array of submission *and* comment objects). The actual object type can be determined by the `kind` property of the `Thing` returned by the API:

```json
// Submission 
{
    "kind": "t3",
    "data": {
        ...
    }
}

// Comment
{
    "kind": "t1",
    "data": {
        ...
    }
}
```

One approach for deserializing this kind of data would be to define an interface which the types implement, then deserialize to that interface:

```cs
// The container used by reddit API objects
class Thing<TData>
{
    string Kind { get; }
    TData Data { get; }
}

// Defines properties shared between submissions and comments
interface IUserContent
{
}

class SubmissionData : IUserContent
{
    ...
}

class Comment : IUserContent
{
    ...
}

// An array of submission and comment things
var json = "...";

var things = JsonSerializer.Deserialize<IEnumerable<Thing<IUserContent>>>(json);
```

However, the `System.Text.Json` assembly [does not support polymorphic deserialization](https://docs.microsoft.com/en-us/dotnet/standard/serialization/system-text-json-converters-how-to?pivots=dotnet-5-0#support-polymorphic-deserialization) so we need to employ the use of a custom `JsonConverterFactory` implementation.

The `ThingJsonConverterFactory` class handles this by first determining whether the data type of the thing matches a set of known concrete types or it should be converted dynamically:

```cs
Type dataType = typeToConvert.GetGenericArguments().First();

if (s_concreteThingTypes.TryGetValue(dataType, out Type thingType))
{
    // We know there is a concrete implementation for this type of thing so use that.
    // This path will be used for a conversion of a type such as IThing<Comment.Details> or IThing<Submission.Details>.
    return (JsonConverter) Activator.CreateInstance(
        typeof(ConcreteTypeThingJsonConverter<,>).MakeGenericType(
            new Type[] { dataType, thingType }),
        BindingFlags.Instance | BindingFlags.Public,
        binder: null,
        args: Array.Empty<object>(),
        culture: null);
}

// There is no concrete implementation for this data type, so we need to dynamically convert each value.
// This path will be used for a conversion of a type such as IThing<IUserContent> or IThing<IVoteable>.
// It must be ensured that any values processed can be cast to IThing<TData>.
return (JsonConverter) Activator.CreateInstance(
    typeof(DynamicTypeThingJsonConverter<>).MakeGenericType(
        new Type[] { dataType }),
    BindingFlags.Instance | BindingFlags.Public,
    binder: null,
    args: Array.Empty<object>(),
    culture: null);
```

The `ConcreteTypeThingJsonConverter<TData, TThing>` class simply deserializes to a specific thing type so I won't go into that, but the `DynamicTypeThingJsonConverter<TData>` class is a bit more interesting. The first step is to parse the JSON to determine the value of the `kind` property:

```cs
Utf8JsonReader readerCopy = reader;

if (!JsonDocument.TryParseValue(ref readerCopy, out JsonDocument document))
{
    throw new JsonException("Unable to parse JSON document.");
}

if (document.RootElement.ValueKind != JsonValueKind.Object)
{
    throw new JsonException($"Unexpected JSON value kind during dynamic conversion. Expected '{JsonValueKind.Object}' but was '{document.RootElement.ValueKind}'");
}

if (!document.RootElement.TryGetProperty("kind", out JsonElement kindPropertyElement))
{
    throw new JsonException("Unable to find 'kind' property in JSON data.");
}

var kind = kindPropertyElement.GetString();
```

With the value of the `kind` property, the converter can then resolve the appropriate concrete type, deserialize to that type, and cast to the instance as `IThing<TData>`:

```cs
Type type = kind switch
{
    Constants.Kind.Comment => typeof(Comment),
    Constants.Kind.User => typeof(User),
    Constants.Kind.Submission => typeof(Submission),
    Constants.Kind.Message => typeof(Message),
    Constants.Kind.Subreddit => typeof(Subreddit),
    Constants.Kind.MoreComments => typeof(MoreComments),
    _ => throw new JsonException($"Unsupported thing kind '{kind}'."),
};

object thing = JsonSerializer.Deserialize(ref reader, type, options);

if (thing is not IThing<TData>)
{
    throw new JsonException($"Unable to cast thing with type '{thing.GetType().FullName}' to '{typeof(IThing<TData>).FullName}'.");
}

return thing as IThing<TData>;
```

The full implementation of `ThingJsonConverterFactory` can be found on [GitHub](https://github.com/JedS6391/Reddit.NET/blob/master/src/Reddit.NET.Client/Models/Internal/Json/ThingJsonConverterFactory.cs).

## Samples

Below are a few samples of common interactions that the client exposes.

#### Retrieving subreddit submissions

```cs
SubredditInteractor askReddit = client.Subreddit("askreddit");

IAsyncEnumerable<SubmissionDetails> fiftyNewSubmissions = askReddit.GetSubmissionsAsync(builder => 
    builder
        .WithSort(SubredditSubmissionSort.New)
        .WithMaximumItems(50));
        
await foreach (SubmissionDetails submission in fiftyNewSubmissions)
{
    // Do something with submission
    ...
}
```

#### Retrieving subscribed subreddits

```cs
MeInteractor me = client.Me();

IAsyncEnumerable<SubredditDetails> mySubreddits = me.GetSubredditsAsync();
        
await foreach (SubredditDetails subreddit in mySubreddits)
{            
    // Do something with subreddit
    ...
}
```

#### Retrieving saved submissions/comments

```cs
MeInteractor me = client.Me(); 

IAsyncEnumerable<UserContentDetails> savedHistory = me.GetHistoryAsync(builder =>
    builder
        .WithType(UserHistoryType.Saved)                    
        .WithMaximumItems(100));

await foreach (UserContentDetails content in savedHistory)
{
    // Saved history can contain both submissions and comments.
    switch (content)
    {
        case CommentDetails comment:
            // Do something with comment
            ...
            break;

        case SubmissionDetails submission:
            // Do something with submission
            ...        
            break;
    }    
}
```

#### Voting on a submission/comment

> **Warning**: Votes must be cast by a human (see the [reddit API documentation](https://www.reddit.com/dev/api/oauth#POST_api_vote) for details).

```cs
// Obtain submission details e.g. by getting the submissions in a subreddit
SubmissionDetails submissionDetails = ...;

// Get an interactor for the submission
SubmissionInteractor submission = submissionDetails.Interact(client);

// There are equivalent methods for downvote/unvote.
await submission.UpvoteAsync();
```

#### Navigating a comment thread

```cs
// Obtain a submission interactor e.g. by getting the submissions in a subreddit
SubmissionInteractor submission = ...;

CommentThreadNavigator comments = await submission.GetCommentsAsync(sort: SubmissionsCommentSort.Top);

// Navigate the replies of each top level thread on the submission
foreach (CommentThread topLevelThread in comments)
{
    foreach (CommentThread replyThread in topLevelThread.Replies)
    {
        // Do something with reply thread     
    }
}
```

## Wrapping up

The first version of this client is now available on [Nuget](https://www.nuget.org/packages/Reddit.NET.Client), with the full source code available on [GitHub](https://github.com/JedS6391/Reddit.NET). Documentation can be viewed [here](https://jeds6391.github.io/Reddit.NET/).

This project has been a good learning exercise in building a modern .NET library, making use of some of the newer framework offerings (like `IAsyncEnumerable<T>` and `System.Text.Json`). I've also put together a set of [GitHub actions](https://docs.github.com/en/actions) to automatically build, test and deploy the project.