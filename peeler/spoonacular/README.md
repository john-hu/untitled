# Spoonacular random recipe peeler

It downloads a random recipe from Spoonacular API.

## Run it

```shell
python -m peeler.spoonacular --api_key [api-key]
```

## Options

* api_key: the API key obtained from [Spoonacular profile page](https://spoonacular.com/food-api/console#Profile). You may need to register a new account before setting it.
* reconvert: to reconvert the raw to recipe again, yes or no. The default value is `no`. Please note if you set this flag, this peeler will delete all recipe files and reconvert it again.  
* storage: the output storage. The default value of this is `peeler_output/spoonacular`. Two types of files will be output:
  * raw_[yyyyMMdd-HHmmss.tttttt].json: raw data from Spoonacular
  * recipe_[yyyy_week].json: the converted recipe list.
