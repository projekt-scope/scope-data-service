On first usage, create the network `scope-net` by running
```
docker network create scope-net
```
and create the volume `fuseki-db-data` by running
```
docker volume create fuseki-db-data
```

In development, start the database with the configuration `./Config.ttl` by
running
```
docker-compose up -d
```
In production, start it with the configuration that was copied into the image
when it was built by running
```
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d
```
Restart it by running
```
docker-compose restart
```
Stop it by running
```
docker-compose down
```
Rebuild the image by running
```
docker-compose build
```
Seed the dataset `scope` from the file `seed/dummy.ttl` by running
```
docker-compose run fuseki-db ./load.sh scope dummy.ttl
```
If the dataset `scope` existed, restart the database to make it find the new
data. Otherwise, on
[http://localhost:22630/manage.html](http://localhost:22630/manage.html)
click "add new dataset", specify `scope` as "Dataset name", and tick
"Persistent". For further information, see the section "Data loading" on
[Jena Fuseki 2 docker image](https://hub.docker.com/r/stain/jena-fuseki#data-loading).

The data itself is stored in the volume `fuseki-db-data`. To list its
contents run
```
docker run --rm -i -v=fuseki-db-data:/data busybox find /data
```
Alternatively, figure out its directory on the host machine by running
```
docker volume inspect fuseki-db-data --format '{{ .Mountpoint }}'
```
and inspect that directory directly. In either case, it is helpful to get
acquainted with [volumes](https://docs.docker.com/storage/volumes/), the command
[`docker volume`](https://docs.docker.com/engine/reference/commandline/volume/)
and its various child commands.
