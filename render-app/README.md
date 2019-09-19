Simple Render with pythonocc0.18.2 and flask

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

# Install
Everything is done inside the docker file.

## Starting
Go into `docker` folder and execute `docker-compose up --build` 
You need the other services like 
* fuseki-db
* fuseki-app
* geom2str

You can change the urls from these services in the .env file.

The geometry which you want to render, needs to be on the fuseki-db in a named graph.

TODO more details!

## Idea
Use the existing pythonocc threejs render in an own service where it will generate the shapes from an ttl file or an url where a ttl is stored. 

### ToDo


## Contact person

### TUDa
- Tim Huyeng +49 6151 16-21333

