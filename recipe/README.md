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

Loading the schema into Apache Solr
```shell
pip install -r recipe-requirement.txt
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
