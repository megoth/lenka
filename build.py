from rdflib import Graph

def build():
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
    from fluent.runtime import FluentLocalization, FluentResourceLoader

    env = Environment(
        loader=FileSystemLoader(searchpath="src/templates"),
        autoescape=select_autoescape()
    )
    template = env.get_template("index.html")
    loader = FluentResourceLoader("src/localizations/{locale}")

    def serialize_html(lang: str):
        l10n = FluentLocalization([lang], ["main.ftl"], loader)
        with open(f".build/{lang}.html", "w") as f:
            f.write(template.render(lang=lang, l10n=l10n))


    serialize_html("en")
    serialize_html("no")

    print("Build complete")


if __name__ == "__main__":
    build()
