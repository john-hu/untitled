# General recipe peeler

It downloads recipes from whatever website.

Please note that the current implementation cannot support two instances running at the same time.

## Run it

### First bootstrap
We should give it a URL link for the first boostrap. It collects all anchors from the input url. And, the collect URL
must be at the same hostname name. After that, it will collect links from links of the parsed links.
```shell
python -m peeler.general --storage ./peeler_output/[whatever name] --init-url [whatever url]
```

For example:
```shell
python -m peeler.general --storage ./peeler_output/simplyrecipes --init-url "https://www.simplyrecipes.com/coco-morante-5091788"
```

### Following running, reading URLs from the first boostrap
```shell
python -m peeler.general --storage ./peeler_output/[whatever name]
```

## Options

* storage (required): the output storage. Two types of files will be output:
  * recipes.db: the recipe url list cache.
  * recipe_[yyyymmddHH].json: the converted recipe list.
* count: the count of requests would be made
* init-url: the first URL of this website