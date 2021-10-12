# Recipe Search Engine
We would like to provide a recipe search service to our users. They can find recipes fastly, precisely, and easily.

## Competence Questions
* What can I cook with a set of materials or equipments?
* What are the recipes for a diet person?
* What can I cook with a keyword?
* What can I cook in a short time?

## System modules

```
 |--------|    |--------|    |--------------|    |---------------|
 |  USER  |--->| NGINX  |--->| Silver Plate |--->| Cutting Board |
 |--------|    |--------|    |--------------|    |---------------|
                                  ^
                                  |
                                  |
                             |----------|
                             |  Peeler  |
                             |----------|

```

### Peeler - Recipe parsers
Peeler is a web crawler to convert data in a web page to [recipe data model](./recipe_json_schema/Recipe.json). Once a file is parsed, it calls the recipe maintenance endpoint to upload a recipe data.

### Silver Plate -  Recipe search service
The recipe search service is a django web server. It serves two endpoints:

1. Recipe search engine: the main endpoint for our users to find the recipes.
   * Auth: none
2. Recipe maintenance: the maintenance endpoint for the site managers to upload/download/reindex the recipe data models.
   * Auth: HTTP Basic Auth

We should also deploy a nginx between users and django server for future scaling up.

### Cutting Board - Apache Solr search engine
The raw recipe data model payloads are stored at the search engine.

#### The indexes
|field|type| copy to text | store|
|-----|----|--------------| ---- |
|categories|terms|yes|no|
|cookingMethod|terms|yes|no|
|cuisines|terms|yes|no|
|description|string|yes|no|
|equipments|terms|yes|no|
|id|id|yes|yes|
|ingredients|terms|yes|no|
|ingredientCount|integer|no|no|
|instructions|string|yes|no|
|instructionCount|integer|no|no|
|keywords|terms|yes|no|
|suitableForDiet|enum|yes|no|
|title|string|yes|no|
|audios|boolean, has or not|no|no|
|cookTime|integer in sec|no|no|
|examples|boolean, has or not|no|no|
|images|boolean, has or not|no|no|
|nutrition|boolean, has or not|no|no|
|prepTime|integer in sec|no|no|
|totalTime|integer in sec|no|no|
|videos|boolean, has or not|no|no|
|_version_ (special)|long, version of doc|no|no|
|_text_ (special)|string, for full text search|no|no|

#### The store fields
|field|type|store|
|-----|----|-----|
|_rawJSON_ (special)|string, raw data|yes|
