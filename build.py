from rdflib import Graph, Literal, Variable
from jinja2 import Environment, select_autoescape, FileSystemLoader
from fluent.runtime import FluentLocalization, FluentResourceLoader
from markdown import markdown

env = Environment(
    loader=FileSystemLoader(searchpath="src/templates"),
    autoescape=select_autoescape()
)
template = env.get_template("index.html")
loader = FluentResourceLoader("src/localizations/{locale}")


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


def serialize_html(lang: str, graph: Graph, *args, **kwargs):
    l10n = FluentLocalization([lang], ["main.ftl"], loader)

    bindings = {Variable("language"): Literal(lang)}
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
            {"list": communities, "single": "community", "plural": "communities"},
            {"list": courses, "single": "course", "plural": "courses"},
            {"list": data_catalogs, "single": "data-catalog", "plural": "data-catalogs"},
            {"list": reading_materials, "single": "reading-material", "plural": "reading-materials"},
            {"list": applications, "single": "application", "plural": "applications"},
        ],
        l10n=l10n,
        lang=lang,
        markdown=markdown,
        serializations=[serialization for serialization in [
            {"label": "JSON-LD", "text": jsonld, "code": "json"} if jsonld else None,
            {"label": "Turtle", "text": turtle, "code": "turtle"} if turtle else None,
            {"label": "RDF/XML", "text": rdfxml, "code": "xml"} if rdfxml else None
        ] if serialization is not None],
        tags=tags,
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
