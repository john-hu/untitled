# Tasty recipe peeler

It downloads recipes from Tasty.

Please note that the current implementation cannot support two instances running at the same time.

## Run it

```shell
python -m peeler.testy [list|result]
```

## Options

* storage: the output storage. The default value of this is `peeler_output/tasty`. Two types of files will be output:
  * recipes.db: the recipe url list cache.
  * recipe_[yyyymmddHH].json: the converted recipe list.
* count: the count of requests would be made
* mode=list: to update the recipe urls from Foodista
* mode=result: to pick an unparsed url from recipes.db and parse it.
