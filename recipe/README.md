# Running the services

## Cutting board (WIP)

### First start Apache Solr
We can run the Apache Solr in a docker:
```shell
docker pull solr:8.10
export PROJ_ROOT=`PWD`
mkdir -r $PROJ_ROOT/build/data
docker run -d -v "$PROJ_ROOT/build/data:/var/solr" -p 8983:8983 --name cutting_board solr:8.10
```

### Create `recipe` collection
```shell
docker exec -it cutting_board solr create -c recipe
```

Turn off the auto-create-fields
```shell
docker exec -it cutting_board solr config -c recipe -p 8983 -action set-user-property -property update.autoCreateFields -value false
```

Copy enum config to `recipe` data folder
```shell
cp doc/cutting_board/recipeEnum.xml build/data/data/recipe/
```

Loading the schema into Apache Solr
```shell
pip install -r requirement.txt
cd recipe
python manage.py runscript create_schema --script-args http://localhost:8983/ recipe
```

After that, you can check the http://localhost:8983/solr/#/recipe/schema to see the schemas. 

### Stop Apache Solr

```shell
docker exec -it cutting_board solr stop -p 8983
```

### Resume Apache Solr
```shell
docker start cutting_board
```

## Silver Plate

### First startup
Since we use django as our base framework, we have to run the migration to build the useless DB.
TODO [#14](https://github.com/john-hu/untitled/issues/14): we should remove it in the future.
```shell
python manage.py migrate
```

### Start the dev server
```shell
python manage.py runserver
```

### APIs
We already create 3 APIs for peeler to upload the recipes:
* GET /peeler/< path:id >: It gets the recipe doc with the recipe ID
* DELETE /peeler/< path:id >: It removes the recipe from the cutting board.
* POST /peeler/: It loads recipes to the cutting board. Limitations:
  * Request type: application/json
  * Payload type: Array of [recipe data model](../doc/recipe_json_schema/Recipe.json)
    * 400 return if failed
  * Maximum length of the whole payload: 10 MB
    * RequestDataTooBig thrown, TODO [#13](https://github.com/john-hu/untitled/issues/13): we should change this to API friendly.
  * Maximum count of recipes: 500
    * 400 return if failed

If you would like to test it, you can ask John Hu to get the postman collection.


## Docker

### Build the image

```shell
cd recipe
docker build -t silver_plate .
```

### Run the image

The following command:
1. starts a container with `silver_plate` image,
2. names the container as silver_plate, and
3. exposes the container port 8001 to host port 8001

```shell
docker run --name silver_plate -p 8001:8001 silver_plate
```

### Environment variables
This image requires the following env variables:
* SERVER_IDLE_TIMEOUT: server idle time out, the default is 120s, see [here](https://docs.gunicorn.org/en/stable/settings.html#timeout).
* SERVER_WORKERS: number of gunicorn worker, the default is 3, see [here](https://docs.gunicorn.org/en/stable/settings.html#timeout).
* CONNECTION_IDLE_TIMEOUT: keep alive timeout or idle timeout, the default is 90s, see [here](https://docs.gunicorn.org/en/stable/settings.html#timeout).
* PID_FILE: the PID file for gunicorn, the default is /opt/recipe/pid, see [here](https://docs.gunicorn.org/en/stable/settings.html#timeout).
* DEBUG: the flag to turn on django debug mode(setting `yes` to enable it), the default is `no`, see [here](https://docs.djangoproject.com/en/3.2/ref/settings/#debug).
* CUTTING_BOARD_URL: the cutting board URL, the default is `http://host.docker.internal:8983/solr/recipe`.
* PEELER_USERNAME: the basic auth username for peeler endpoints, the default is `peeler`.
* PEELER_PASSWORD: the basic auth password for peeler endpoints, the default is `123456`.
