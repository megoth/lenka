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

from jinja2 import Environment, select_autoescape, FileSystemLoader

env = Environment(
    loader=FileSystemLoader(searchpath="src/templates"),
    autoescape=select_autoescape()
)


def serialize_html(lang: str, body: str):
    template = env.get_template("index.html")
    with open(f".build/{lang}.html", "w") as f:
        f.write(template.render(lang=lang, body=body))


serialize_html("en", "Hello World!")
serialize_html("no", "Hei verden!")
