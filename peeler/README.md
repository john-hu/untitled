# Peeler

## Install dependencies 
```shell
pip install -r requirement.txt
```

## Run a peeler
```shell
python -m peeler.[peeler_name]
```

## Peeler user agent
We named our peelers as `RecipeSearchCrawler`. It should run with the following user agent:
```
RecipeSearchCrawler (version: {version})
```

### Auto uploading while peeling
We already support the auto uploader at the base peeler. While emitting a RecipeItem, the
`RecipeResultPipeline` calls uploader for auto uploading. To enable that, please set the
following environment variables:
```shell
AUTO_UPLOADER_ENABLED=yes
AUTO_UPLOADER_ENDPOINT=https://wiseipes.com
AUTO_UPLOADER_USERNAME=peeler
AUTO_UPLOADER_PASSWORD=<peeler password>
```

## Upload peeled result to silver plate

```shell
python -m peeler.utils.uploader \
       --endpoint https://wiseipes.com \
       --username peeler \
       --password 123456 \
       --mode pull_merge \
       [json file]
```

Arguments:
* `--endpoint`: the endpoint of silver plate, http://localhost:8001 for local.
* `--username`: the basic auth username
* `--password`: the basic auth password
* `--mode`: the upload mode, `pull_merge` or `push_all`.
  * `pull_merge`: It tries to download the data from silver plate, merge the old data with the new data and upload it back.
  * `push_all`: It just push the whole json file to the silver plate.
