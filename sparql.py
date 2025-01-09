import yaml
import random
from SPARQLWrapper import SPARQLWrapper, JSON

# Load questions from the YAML file
def load_questions():
    with open("conf.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config["questions"]

# Fetch all bands from YAGO
#def get_all(type):
#    sparql = SPARQLWrapper("https://yago-knowledge.org/sparql/query")
#    sparql.setReturnFormat(JSON)
#    sparql.setQuery("""
#        PREFIX schema: <http://schema.org/>
#        PREFIX yago: <http://yago-knowledge.org/resource/>
#        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#        SELECT DISTINCT ?band 
#        WHERE {
#            ?band a schema:MusicGroup .
#            ?person schema:memberOf ?band .
#        }
#    """
#    )
#
#    response = sparql.queryAndConvert()
#    bands = [result["band"]["value"] for result in response["results"]["bindings"]]
#    print(bands)
#    return bands

def get_all(tpe, prop):
    sparql = SPARQLWrapper("https://yago-knowledge.org/sparql/query")
    sparql.setReturnFormat(JSON)
    print(tpe, prop)
    #extra = ""
    #if len(tpe > 1):
    #    for i in range(1, len(tpe)):
    #        extra += f"UNION{{?thing a yago:{tpe[i]} . }}"
    sparql.setQuery(f"""
        PREFIX schema: <http://schema.org/>
        PREFIX yago: <http://yago-knowledge.org/resource/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?thing
        WHERE {{
            ?thing a {tpe} .
        }}
    """
    )

    response = sparql.queryAndConvert()
    things = [result["thing"]["value"] for result in response["results"]["bindings"]]
    filtered = [s for s in things if ("u0028" or "u0029") not in s]
    print(filtered)
    return filtered

def get_query(question, entity):
    if "How many band members" in question:
        return f"""
            PREFIX schema: <http://schema.org/>
            PREFIX yago: <http://yago-knowledge.org/resource/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT (COUNT(DISTINCT ?thing) AS ?count) 
            WHERE {{
                ?thing schema:memberOf yago:{entity} .
            }}
        """
    elif "Can you name a band member" in question:
        return f"""
            PREFIX schema: <http://schema.org/>
            PREFIX yago: <http://yago-knowledge.org/resource/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?thing
            WHERE {{
                ?thing schema:memberOf yago:{entity} . 
            }}
        LIMIT 10
        """
    elif "Who is the leader of" in question:
        return f"""
            PREFIX schema: <http://schema.org/>
            PREFIX yago: <http://yago-knowledge.org/resource/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?thing
            WHERE {{
                yago:{entity} schema:leader ?thing . 
            }}
        LIMIT 1
        """
    elif "What is the capital of" in question:
        return f"""
            PREFIX schema: <http://schema.org/>
            PREFIX yago: <http://yago-knowledge.org/resource/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?thing
            WHERE {{
                yago:{entity} yago:capital ?thing . 
            }}
        LIMIT 1
        """
    

# Formulate a question about the selected band and fetch the answer
def get_answer():

    questions = load_questions()
    question = random.choice(questions)

    q_text = question["text"]
    q_type = question["type"]
    q_property = question["property"]

    print(q_text, q_type, q_property)

    entities = get_all(q_type, q_property)

    results = []
    while not results:
        entity = random.choice(entities)
        entity = entity.split('/')[-1]
        print(entity)

        sparql = SPARQLWrapper("https://yago-knowledge.org/sparql/query")
        sparql.setReturnFormat(JSON)

        formulated_question = q_text.replace("?", entity.replace("_", " ")) + "?"
        print(formulated_question)

        q = get_query(q_text, entity)
        print(q)
        sparql.setQuery(q)
        response = sparql.queryAndConvert()
        results = response["results"]["bindings"]

    print(response)
    print(results)

    if "count" in results[0]:
        return f"{results[0]['count']['value']} members", formulated_question

    things = [result["thing"]["value"].split('/')[-1].replace("_", " ") for result in results]
    return things, formulated_question