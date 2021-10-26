# Spoonacular random recipe peeler

It downloads a random recipe from Spoonacular API.

Please note that the current implementation cannot support two instances running at the same time.

## Run it

```shell
python -m peeler.spoonacular --api_key [api-key]
```

## Options

* api_key: the API key obtained from [Spoonacular profile page](https://spoonacular.com/food-api/console#Profile). You may need to register a new account before setting it.
* reconvert: to reconvert the raw to recipe again, yes or no. The default value is `no`. Please note if you set this flag, this peeler will delete all recipe files and reconvert it again.  
* storage: the output storage. The default value of this is `peeler_output/spoonacular`. Two types of files will be output:
  * raw_[yyyyMMdd-HHmmss.tttttt].json: raw data from Spoonacular
  * recipe_[yyyyMMdd].json: the converted recipe list.
* count: the count of requests would be made
* request-delay: sleep between requests.

## Quota mechanism
Spoonacular limits 150 points per day. One request may consume 1.01 points. We introduce a quota secure mechanism. This
peeler will save the quota value from API response to a `quota.json` file who is stored at the same folder of recipe
files, peeler_output/spoonacular/quota.json in default.

The maximum limit is 120 points. The peeler raise an OverQuotaError with the used points if the API response over this value.
