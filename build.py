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

def query(rdf_class: str):
    return f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX schema: <https://schema.org/>
        
        SELECT ?id ?type ?name ?description ?url (GROUP_CONCAT(DISTINCT ?tag; SEPARATOR=";") AS ?tags)
        WHERE {{
            ?id rdf:type {rdf_class} .
            ?id rdf:type ?type .
            ?id schema:name ?name .  
            ?id schema:description ?description .  
            ?id schema:url ?url .  
            ?id schema:keywords ?tag .
        }}
        GROUP BY ?id
        """


def serialize_html(lang: str, graph: Graph):
    l10n = FluentLocalization([lang], ["main.ftl"], loader)
    bindings = {Variable("language"): Literal(lang)}
    communities = graph.query(query("schema:Organization"), initBindings=bindings)
    courses = graph.query(query("schema:Course"), initBindings=bindings)
    data_catalogs = graph.query(query("schema:DataCatalog"), initBindings=bindings)
    readings = graph.query(query("schema:CreativeWork"), initBindings=bindings)
    applications = graph.query(query("schema:SoftwareApplication"), initBindings=bindings)
    tags = {}
    for tag in graph.query("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX schema: <https://schema.org/>
        
        SELECT ?id ?name ?type
        WHERE {
            ?id rdf:type schema:DefinedTerm .
            ?id rdf:type ?type .
            ?id schema:name ?name .  
            FILTER( lang(?name) = 'en' || langMatches(lang(?name), ?language) )
        }
        """, initBindings=bindings):
        tags[str(tag.get("id"))] = tag

    return template.render(
        applications=applications,
        communities=communities,
        courses=courses,
        data_catalogs=data_catalogs,
        l10n=l10n,
        lang=lang,
        markdown=markdown,
        readings=readings,
        tags=tags,
    )


def build_html(lang: str, graph: Graph):
    with open(f".build/{lang}.html", "w") as f:
        f.write(serialize_html(lang, graph))


def build():
    g = Graph()
    g.parse('src/data/communities.ttl')
    g.parse('src/data/courses.ttl')

    g.serialize(destination='.build/data.ttl', format='turtle')
    g.serialize(destination='.build/data.xml', format='xml')
    g.serialize(destination='.build/data.json', format='json-ld', context={
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
