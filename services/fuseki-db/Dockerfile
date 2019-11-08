FROM stain/jena-fuseki:3.10.0

# Note that the working directory `.` is `/jena-fuseki`. For details
# see https://hub.docker.com/r/stain/jena-fuseki/dockerfile

COPY Config.ttl .

EXPOSE 3030
CMD ["./fuseki-server", "--config", "Config.ttl"]
