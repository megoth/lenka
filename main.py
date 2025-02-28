import uvicorn
from fastapi import FastAPI
from rdflib import Graph
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.staticfiles import StaticFiles

from build import serialize_html

app = FastAPI()

g = Graph()
g.parse('src/data/applications.ttl')
g.parse('src/data/for-beginners.ttl')
g.parse('src/data/communities.ttl')
g.parse('src/data/courses.ttl')
g.parse('src/data/data-catalogs.ttl')
g.parse('src/data/reading-materials.ttl')
g.parse('src/data/tags.ttl')

jsonld = g.serialize(format='json-ld',
                     context={"lenka": "https://lenka.no#", "schema": "https://schema.org/",
                              "description": "schema:description", "name": "schema:name",
                              "url": "schema:url", "keywords": "schema:keywords" })
rdfxml = g.serialize(format='xml')
turtle = g.serialize(format='turtle')

html_no = serialize_html("no", g, jsonld=jsonld, turtle=turtle, rdfxml=rdfxml)
html_en = serialize_html("en", g, jsonld=jsonld, turtle=turtle, rdfxml=rdfxml)


def read_response(request: Request, html: str):
    if request.headers.get("Accept") == "application/ld+json":
        return PlainTextResponse(jsonld, media_type="application/ld+json")
    if request.headers.get("Accept") == "application/rdf+xml":
        return PlainTextResponse(rdfxml, media_type="application/rdf+xml")
    if request.headers.get("Accept") == "text/turtle":
        return PlainTextResponse(turtle, media_type="text/turtle")
    return PlainTextResponse(html, media_type="text/html")


@app.get("/")
def read_norwegian(request: Request):
    return read_response(request, html_no)


@app.get("/en")
def read_english(request: Request):
    return read_response(request, html_en)


app.mount("/", StaticFiles(directory="./public"), name="public")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
