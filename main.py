import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import FileResponse, PlainTextResponse
from rdflib import Graph

app = FastAPI()

g = Graph()
g.parse('src/data/communities.ttl')
g.parse('src/data/courses.ttl')

jsonld = g.serialize(format='json-ld',
                     context={"lenka": "https://lenka.no/#", "schema": "https://schema.org/",
                              "description": "schema:description", "name": "schema:name",
                              "url": "schema:url", })
rdfxml = g.serialize(format='xml')
turtle = g.serialize(format='turtle')


def read_response(request: Request, html_file: str):
    if request.headers.get("Accept") == "application/ld+json":
        return PlainTextResponse(jsonld, media_type="application/ld+json")
    if request.headers.get("Accept") == "application/rdf+xml":
        return PlainTextResponse(rdfxml, media_type="application/rdf+xml")
    if request.headers.get("Accept") == "text/turtle":
        return PlainTextResponse(turtle, media_type="text/turtle")
    return FileResponse(html_file)


@app.get("/")
def read_norwegian(request: Request):
    return read_response(request, html_file=".build/no.html")


@app.get("/en")
def read_english(request: Request):
    return read_response(request, html_file=".build/en.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
