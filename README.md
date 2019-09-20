# SCOPE data service

Data service for RDF-based BIM representation including geometry.

## Installation

Docker is required. Start each microservice (fuseki-app, fuseki-db, geom2str, occvis-app, render-app, revit-app) with docker-compose up.
Add a dataset named "data" to the fuseki database via the graphical user interface on IP:22630. 

## Test run

Database content can be created via Autodesk Revit 2019 and RevitPythonShell. Copy/paste the script readRevit.py located in the client folder to the interactive RevitPythonShell and run the script.

The script will create a file called Revit-ProjectName.ttl on your desktop. "ProjectName" is the project name from your Revit project. This name can be set or changed in Revit via Manage -- Project Information -- Other. Resulting examples are already available in the client folder.

In the client folder, run the following script: `python test_run.py YourRevitProjectName`, with YourRevitProjectName being a string representing the project name. With the already existing example, the command is: `python test_run.py SimpleExample`.

The script should create a web service that can be called via http://Your_IP_number:22634/TS, with the docker server as the IP number.   

## Description

The SCOPE data service allows to create, store and visualize complex geometrical information with the help of the open-source geometry kernel openCASCADE. It consists of an Autodesk Revit 2019 exporter based on RevitPythonShell and a small GUI for visualizing the 3D geometry and its RDF graph representation. It uses the OCC ontology published at w3id.org/occ.


## ToDo
- [x] Directly export Revit information into the Fuseki database


## Acknowledgments

The code development is done within the German research project SCOPE (www.projekt-scope.de), funded by the Federal Ministry for Economic Affairs and Energy.


## Contact persons

- Christian Nothstein +49 711 7883 8978
- Tim Huyeng +49 6151 16-21333
- Dr. Wendelin Sprenger +49 711 7883 8692

