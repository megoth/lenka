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
