import uvicorn
from fluent.runtime import FluentLocalization, FluentResourceLoader
from jinja2 import Environment, select_autoescape, FileSystemLoader
from fastapi import FastAPI
from markdown import markdown
from rdflib import Graph, Literal, Variable
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.staticfiles import StaticFiles

def query_collection(collection_id: str):
    return f"""
        PREFIX lenka: <https://lenka.no#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX schema: <https://schema.org/>

        SELECT DISTINCT ?id ?type ?name ?description ?url
        WHERE {{
            lenka:{collection_id} schema:hasPart ?id .
            ?id rdf:type ?type .
            ?id schema:name ?name .
            ?id schema:description ?description .
            ?id schema:url ?url .
        }}
        GROUP BY ?id
        """


def query_content(rdf_class: str):
    return f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX schema: <https://schema.org/>

        SELECT * WHERE {{
            {{
                SELECT ?id ?type ?name ?description ?url (GROUP_CONCAT(DISTINCT ?tag; SEPARATOR=";") AS ?tags)
                WHERE {{
                    ?id rdf:type {rdf_class} .
                    ?id rdf:type ?type .
                    ?id schema:name ?name .
                    ?id schema:description ?description .
                    ?id schema:url ?url .
                    ?id schema:keywords ?tag .
                    FILTER(langMatches(lang(?description), ?language))
                }}
                GROUP BY ?id
            }}
            UNION
            {{
                SELECT ?id ?type ?name ?description ?url (GROUP_CONCAT(DISTINCT ?tag; SEPARATOR=";") AS ?tags)
                WHERE {{
                    ?id rdf:type {rdf_class} .
                    ?id rdf:type ?type .
                    ?id schema:name ?name .
                    ?id schema:description ?description .
                    ?id schema:url ?url .
                    ?id schema:keywords ?tag .
                    FILTER(lang(?description) = "en" && not exists {{
                        ?id schema:description ?description2
                        FILTER(langMatches(lang(?description2), ?language))
                    }})
                }}
                GROUP BY ?id
            }}
        }}
        ORDER BY ASC(?id)
        """


def query_tags():
    return """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX schema: <https://schema.org/>

        SELECT ?id ?name ?type
        WHERE {
            ?id rdf:type schema:DefinedTerm .
            ?id rdf:type ?type .
            ?id schema:name ?name .
            FILTER( lang(?name) = "en" || langMatches(lang(?name), ?language) )
        }
        """

env = Environment(
    loader=FileSystemLoader(searchpath="src/templates"),
    autoescape=select_autoescape()
)
template = env.get_template("index.html")
loader = FluentResourceLoader("src/localizations/{locale}")


def serialize_html(lang: str, graph: Graph, *args, **kwargs):
    l10n = FluentLocalization([lang], ["main.ftl"], loader)

    bindings = {Variable("language"): Literal(lang)}
    intro = graph.query(query_collection('intro-to-linked-data'))
    communities = graph.query(query_content("schema:Organization"), initBindings=bindings)
    courses = graph.query(query_content("schema:Course"), initBindings=bindings)
    data_catalogs = graph.query(query_content("schema:DataCatalog"), initBindings=bindings)
    reading_materials = graph.query(query_content("schema:CreativeWork"), initBindings=bindings)
    applications = graph.query(query_content("schema:SoftwareApplication"), initBindings=bindings)
    tags = {str(tag.get("id")): tag for tag in graph.query(query_tags(), initBindings=bindings)}

    jsonld = kwargs.get("jsonld", None)
    turtle = kwargs.get("turtle", None)
    rdfxml = kwargs.get("rdfxml", None)

    return template.render(
        indexes=[
            {"list": intro, "id": "intro-to-linked-data"},
            {"list": communities, "id": "communities"},
            {"list": courses, "id": "courses"},
            {"list": data_catalogs, "id": "data-catalogs"},
            {"list": reading_materials, "id": "reading-materials"},
            {"list": applications, "id": "applications"},
        ],
        l10n=l10n,
        lang=lang,
        languages=[language for language in [
            {"code": "en", "url": "/en", "label": "english", "icon": "/united-kingdom.png"},
            {"code": "no", "url": "/", "label": "norwegian", "icon": "/norway.png"},
        ] if language.get("code") is not lang],
        markdown=markdown,
        serializations=[serialization for serialization in [
            {"label": "JSON-LD", "text": jsonld, "code": "json", "format": "application/ld+json"} if jsonld else None,
            {"label": "Turtle", "text": turtle, "code": "turtle", "format": "text/turtle"} if turtle else None,
            {"label": "RDF/XML", "text": rdfxml, "code": "xml", "format": "application/rdf+xml"} if rdfxml else None
        ] if serialization is not None],
        tags=tags,
        url="/" if lang == "no" else f"/{lang}"
    )


def build_html(lang: str, graph: Graph):
    with open(f".build/{lang}.html", "w") as f:
        f.write(serialize_html(lang, graph))


def build():
    g = Graph()
    g.parse("src/data/communities.ttl")
    g.parse("src/data/courses.ttl")

    g.serialize(destination=".build/data.ttl", format="turtle")
    g.serialize(destination=".build/data.xml", format="xml")
    g.serialize(destination=".build/data.json", format="json-ld", context={
        "lenka": "https://lenka.no#",
        "schema": "https://schema.org/",
        "description": "schema:description",
        "name": "schema:name",
        "url": "schema:url",
    })

    build_html("en", g)
    build_html("no", g)

    print("Build complete")

app = FastAPI()

g = Graph()
g.parse('src/data/applications.ttl')
g.parse('src/data/communities.ttl')
g.parse('src/data/courses.ttl')
g.parse('src/data/data-catalogs.ttl')
g.parse('src/data/introductory-resources.ttl')
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


# UNCOMMENT THIS WHEN YOU NEED TO INCLUDE STATIC FILES LOCALLY
# app.mount("/", StaticFiles(directory="./public"), name="public")

if __name__ == "__main__":
    uvicorn.run("index:app", host="0.0.0.0", port=8000, reload=True)
