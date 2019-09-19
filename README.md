### Data service for RDF-based BIM representation including geometry ("SCOPE data service")

# Install
Docker is required. Start each microservice (fuseki-app, fuseki-db, geom2str, occvis-app, render-app, revit-app) with docker-compose up.
Add a dataset named "data" to the fuseki database via the graphical user interface on IP:22630 

### Test run

 - Export revit geometry information with the interactive revit python shell. Therefore use the "readRevit.py"-script which is located in the /client folder  

 - The revit-.ttl is now on your desktop. The file name structure is "Revit_YourRevitProjectName.ttl" --> **YourRevitProjectName** is the project name from your Revit Project. Set or change it in Revit via manage-->projectinformation-->other. There is an example which can be used for testing with the name `REVIT_SimpleExample.ttl`  

 - Start the required microservices  

 - In services/client: run  `python test_run.py **YourRevitProjectName**`. With our example: `python test_run.py SimpleExample`  

 - The script should create a web service that can be called via http://Your_IP_number:22634/TS, with the docker server as the IP_number.   


### Description

The SCOPE data service allows to create, store and visualize complex geometrical information with the help of the open-source geometry kernel openCASCADE. It consists of an Autodesk Revit 2019 exporter based on RevitPythonShell and a small GUI for visualizing the 3D geometry and its RDF graph representation.

For the RevitPythonShell export procedure, a manual step is required. After the installation of RevitPythonShell (https://github.com/architecture-building-systems/revitpythonshell/releases/download/2018.09.19/2018.09.19_Setup_RevitPythonShell_2019.exe), the code "readRevit.py" in the folder services/revit-app has to be copied to the RevitPythonShell interface. Running the code will create a TTL file that has to be stored locally and is read by the test_run.py script.


### ToDo
- [x] Directly export Revit information into the Fuseki database


## Contact persons

- Christian Nothstein +49 711 7883 8978
- Tim Huyeng +49 6151 16-21333
- Dr. Wendelin Sprenger +49 711 7883 8692

