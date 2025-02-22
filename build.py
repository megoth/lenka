from rdflib import Graph

g = Graph()
g.parse('src/data/communities.ttl')
g.parse('src/data/courses.ttl')
g.serialize(destination='.build/data.ttl', format='turtle')
g.serialize(destination='.build/data.xml', format='xml')
g.serialize(destination='.build/data.json', format='json-ld', context={
    "lenka": "https://lenka.no/#",
    "schema": "https://schema.org/",
    "description": "schema:description",
    "name": "schema:name",
    "url": "schema:url",
})
