# Allrecipes recipe peeler

It downloads recipes from Allrecipes.

Please note that the current implementation cannot support two instances running at the same time.

## Run it

```shell
python -m peeler.allrecipes [list|result]
```

## Options

* storage: the output storage. The default value of this is `peeler_output/allrecipes`.
Two types of files will be output:
  * recipes.db: the recipe url list cache.
  * recipe_[yyyymmddHH].json: the converted recipe list.
* count: the count of requests would be made
* mode=list: to update the recipe urls from Allrecipes
* mode=result: to pick an unparsed url from recipes.db and parse it.

## Robots.txt limitation
According to [robots.txt](https://www.allrecipes.com/robots.txt),
we shouldn't make the request to fast. The request delay is fixed to 1 seconds. So,the maximum throughput of an hour
is 3600.
