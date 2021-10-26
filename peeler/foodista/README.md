# Foodista recipe peeler

It downloads recipes from Foodista.

Please note that the current implementation cannot support two instances running at the same time.

## Run it

```shell
python -m peeler.foodista [list|result]
```

## Options

* storage: the output storage. The default value of this is `peeler_output/spoonacular`. Two types of files will be output:
  * recipes.db: the recipe url list cache.
  * recipe_[yyyymmddHH].json: the converted recipe list.
* count: the count of requests would be made
* mode=list: to update the recipe urls from Foodista
* mode=result: to pick an unparsed url from recipes.db and parse it.

## Robots.txt limitation
According to [robots.txt](http://foodista.com/robots.txt), we shouldn't make the request to fast. The request delay is
fixed to 30 seconds. So, the maximum throughput of an hour is 120. It may be over a POST limitation of silver plate.
The suggested setting of `count` per hour is 100. 
