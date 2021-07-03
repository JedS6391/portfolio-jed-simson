Title:   Building a .NET client for reddit
Summary: Details the reddit client implementation in .NET that I've been working on
Author:  Jed Simson
Date:    July 04, 2021
Tags:    Reddit, API, Client, Project, C#, .NET, DotNet

## Background

I've been interested in the [reddit API](https://www.reddit.com/dev/api/oauth) for a while, as it is a site I interact with frequently and has a few interesting details in its implementation. 

In the past, I've used the [Python Reddit API Wrapper (PRAW)](https://praw.readthedocs.io/en/latest/) to create [an API for accessing saved reddit posts](https://github.com/JedS6391/reddit-saved-post-viewer-api), as well as numerous other quick scripts for analysing reddit data.

As a challenge to myself, I decided to build my own client library for interacting with reddit in .NET with the following goals:

- Simple, modern, asynchronous API
- Support for various authentication modes
- Modular structure with simple re-usable components

This post expands on the details behind the decisions made during implementation of the client, as well as some of the technical challenges faced.

## Implementation

### Designing a simple client API

### Asynchronous-first API

### Polymorphic deserialization with `System.Text.Json`

## Samples

Below are a few samples of common interactions that the client exposes.

### Retrieving subreddit submissions

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

### Retrieving subscribed subreddits

```cs
MeInteractor me = client.Me();

IAsyncEnumerable<SubredditDetails> mySubreddits = me.GetSubredditsAsync();
        
await foreach (SubredditDetails subreddit in mySubreddits)
{            
    // Do something with subreddit
    ...
}
```

### Retrieving saved submissions/comments

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

### Voting on a submission/comment

> **Warning**: Votes must be cast by a human (see the [reddit API documentation](https://www.reddit.com/dev/api/oauth#POST_api_vote) for details).

```cs
// Obtain submission details e.g. by getting the submissions in a subreddit
SubmissionDetails submissionDetails = ...;

// Get an interactor for the submission
SubmissionInteractor submission = submissionDetails.Interact(client);

// There are equivalent methods for downvote/unvote.
await submission.UpvoteAsync();
```

### Navigating a comment thread

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

The first version of this client is now available on [Nuget](https://www.nuget.org/packages/Reddit.NET.Client), with the full source code available on [GitHub](https://github.com/JedS6391/Reddit.NET).


