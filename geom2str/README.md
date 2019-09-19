# SPARQL --> writeGeomStr --> readGeomStr

## what is this for? 

This package can do the following things:  
  -  1. running a SPARQL query which e.g. finds all geometric representations within a graph.  
  -  2. run the recursive "create geometry" query with the results from 1 and write them to a specified file on the server   
  -  3. find your file on the server and send it back to you.

you can do this by sending http post requests. See examples in the file "callEndpoints.py"


## how to setup  

clone the repo and checkout the branch develop via  
`git fetch`
`git checkout develop`  

the docker compose file does have all information needed to set up a docker container which is available on Port 5011  
`docker-compose up`  

Use the python file "callEndpoints.py" as an example of how to use the Endpoints  
`python callEndpoints.py `



