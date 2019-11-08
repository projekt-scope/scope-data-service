



Invoke-WebRequest -Uri http://10.200.29.203:22631/upload -Body ((@{"File1" = Get-Content -Raw C:\Users\SprengerWen\scope\graph-based-geometry-description\examples\GeomGraphZ3Komplett.ttl}) | ConvertTo-Json) -Method POST -ContentType "application/json"



(Invoke-WebRequest -Uri http://10.200.29.203:22631/sparql  -Body ((@{SparqlString="SELECT ?g ?s ?p ?o WHERE {{ ?s ?p ?o }UNION{ GRAPH ?g { ?s ?p ?o } } }"}) | ConvertTo-Json) -ContentType "application/json" -Method POST).Content



(Invoke-WebRequest -Uri http://10.200.29.203:22631/delete  -Body ((@{SparqlString="DELETE WHERE {GRAPH ?g {?s ?p ?o }}"}) | ConvertTo-Json) -ContentType "application/json" -Method POST).Content



