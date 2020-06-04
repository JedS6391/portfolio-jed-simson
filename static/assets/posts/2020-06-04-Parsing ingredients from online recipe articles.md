Title:   Parsing ingredients from online recipe articles
Summary: Details the project I've been working on to extract recipe ingredients from online articles
Author:  Jed Simson
Date:    June 04, 2020
Tags:    Parsing, Parser combinators, Recipes, Ingredients, Project, C#, .NET

## Background

Recently, I've been working on a web application to manage recipes that my partner and I have collected. The application provides forms to enter the recipe metadata as well as the ingredients that comprise the recipe. 

To ease the process of copying recipes into system, I started to investigate whether it would be possible to extract the details of a recipe from the website where it is listed. This post will detail the process involved in building the functionality to import recipes, including extracting the raw data and parsing into a useable format.

## Extracting recipe content

In starting the process, I wished to discover if there was a common format that recipe sites adhere to. I quickly found that to help improve the ranking of a site with a recipe on it in Google search results, sites can provide metadata as detailed in the [Google search documentation](https://developers.google.com/search/docs/data-types/recipe).

The documentation describes that a website can add a `script` tag, with the `application/ld+json` type containing metadata about the recipe. This is great, as it means the data is in an easily consumable format. I decided to out-of-scope sites that don't adhere to this format for now.

<pre>
<code class="json">{
    "@context": "https://schema.org/",
    "@type": "Recipe",
    "name": "Party Coffee Cake",
    "image": [
    "https://example.com/photos/1x1/photo.jpg",
    "https://example.com/photos/4x3/photo.jpg",
    "https://example.com/photos/16x9/photo.jpg"
    ],
    "author": {
    "@type": "Person",
    "name": "Mary Stone"
    },
    "datePublished": "2018-03-10",
    "description": "This coffee cake is awesome and perfect for parties.",
    "prepTime": "PT20M",
    "cookTime": "PT30M",
    "totalTime": "PT50M",
    "keywords": "cake for a party, coffee",
    "recipeYield": "10",
    "recipeCategory": "Dessert",
    "recipeCuisine": "American",
    "nutrition": {
    "@type": "NutritionInformation",
    "calories": "270 calories"
    },
    "recipeIngredient": [
    "2 cups of flour",
    "3/4 cup white sugar",
    "2 teaspoons baking powder",
    "1/2 teaspoon salt",
    "1/2 cup butter",
    "2 eggs",
    "3/4 cup milk"
    ],
    ...
}</code>
</pre>

The algorithm I devised for extracting this content is as follows:

1. Fetch the HTML content of the page at a specified url
2. Parse the HMTL
3. Extract the `<script type="application/ld+json">` if any
4. Build a JSON object from the content of the tag
5. Extract relevant properties (e.g. `name`, `recipeIngredients`)
6. Build a recipe object for persistence in the system

The implementation of this process in the application can be found [here](https://github.com/JedS6391/RecipeManager.Server/blob/feature/recipe-import/RecipeManager.Core/Features/Recipes/Services/RecipeImporterService.cs). There is some extra complexity in the implementation, as the import process is run by a background worker as a result of reading a message from a queue, but the general approach remains the same.

## Parsing recipe ingredients

### Approach

With the recipe metadata extracted, now came the task of parsing the recipe ingredients. I found that there is a huge amount of variety in how people that share recipes structure their ingredients which made it a non-trivial process. 

I debated using a machine learning approach -- training a classifier to learn the structure of ingredients -- but I decided against it as it seemed like overkill for this project.

Instead I decided to use a [parser combinator](https://en.wikipedia.org/wiki/Parser_combinator) based approach. The general idea is that ingredient strings can be broken down into a set of tokens. For example, the ingredient *1 cup flour* can be tokenized as `{amount} {unit} {ingredient}`. This template structures serves as the basis for the parser.

Once we have a template definition for an ingredient string (e.g. `{amount} {unit} {ingredient}`), we can break this down into a set of parsing functions (token readers). The template definition above can be thought of as the following set of token readers:

- Read an amount token
- Read a space
- Read a unit token
- Read a space
- Read an ingredient token

Armed with a set of template definition (which describe the sequence of token readers), we can create a parser that will try to match against each template definition provided to it. 

### Library demonstration

So far this post has been a bit hand-wavey, so to cement these ideas a bit further, here's an example of the library I built for parsing ingredients in action:

<pre>
<code class="csharp">// Token readers are responsible for reading a component from an 
// ingredient string into a token (e.g. cup -> UnitToken("cup")).
// Each token reader will map to a token type.
var tokenReaders = new ITokenReader[] 
{
    // {amount}
    new AmountTokenReader(),
    // {unit}
    new UnitTokenReader(),
    // {ingredient}
    new IngredientTokenReader()
};

// Sanitization rules provided a way to pre-process the raw 
// ingredient string before parsing occurs.
var sanitizationRules = new ISanitizationRule[]
{
    new RemoveExtraneousSpacesRule()
};

var parser = IngredientParser
    .Builder
    .New
    .WithTemplateDefinitions("{amount} {unit} {ingredient}")
    // Token reader factory is responsible for providing a token
    // reader for each token in the template definition
    .WithTokenReaderFactory(new TokenReaderFactory(tokenReaders))
    // Stop parsing when the first full match is found
    .WithParserStrategy(new FirstFullMatchParserStrategy())
    .WithSanitizationRules(sanitizationRules)
    .Build();

if (parser.TryParseIngredient("1 cup flour", out var parseResult))
{
    // The result can be inspected when parsing succeeds
    var amount = parseResult.Amount;
    var unit = parseResult.Unit;
    var ingredient = parseResult.Ingredient;
}
</code>
</pre>

## Wrapping up

I have tested the ingredient parser out on a number of websites and the results seem to be fairly promising. Sometimes the parser will fail to match an ingredient, primarily due to the inconsistency of ingredient strings in recipe articles. But for the majority of ingredients, it is able to get a successful parse result.

If you are interested in using the library, the full source code can be found on [my Github](https://github.com/JedS6391/RecipeIngredientParser), along with tests and examples.