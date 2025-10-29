from rdflib import Graph, Literal, Variable
from jinja2 import Environment, select_autoescape, FileSystemLoader
from fluent.runtime import FluentLocalization, FluentResourceLoader
from markdown import markdown

from queries import query_collection, query_content, query_tags

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
            {"code": "en", "url": "/en", "label": "english", "icon": "https://raw.githubusercontent.com/megoth/lenka/refs/heads/main/public/united-kingdom.png"},
            {"code": "no", "url": "/", "label": "norwegian", "icon": "https://raw.githubusercontent.com/megoth/lenka/refs/heads/main/public/norway.png"},
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


if __name__ == "__main__":
    build()
