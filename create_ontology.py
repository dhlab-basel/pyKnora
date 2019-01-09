from typing import List, Set, Dict, Tuple, Optional
from pprint import pprint
import argparse
import json
from jsonschema import validate
from rdflib import Graph
from knora import KnoraError, knora


# parse the arguments of the command line
parser = argparse.ArgumentParser()
parser.add_argument("ontofile", help="path to ontology file")
parser.add_argument("-s", "--server", type=str, default="http://0.0.0.0:3333", help="URL of the Knora server")
parser.add_argument("-u", "--user", default="root@example.com", help="Username for Knora")
parser.add_argument("-p", "--password", default="test", help="The password for login")
parser.add_argument("-v", "--validate", action='store_true', help="Do only validation of JSON, no upload of the ontology")
parser.add_argument("-l", "--lists", action='store_true', help="Only create the lists")

args = parser.parse_args()


def list_creator(con: knora, proj_iri: str, list_iri: str, parent_iri: str, nodes: List[dict]):
    nodelist = []
    for node in nodes:
        node_id = con.create_list_node(
            name=node["name"],
            project_iri=proj_iri,
            labels=node["labels"],
            comments=node.get("comments"),
            parent_iri=parent_iri
        )
        if node.get('nodes') is not None:
            subnodelist = list_creator(con, proj_iri, list_iri, node_id, node['nodes'])
            nodelist.append({node["name"]: {"id": node_id, 'nodes': subnodelist}})
        else:
            nodelist.append({node["name"]: {"id": node_id}})
    return nodelist


def create_template(con: knora, shortcode: str, shortname: str):
    turtle = con.get_ontology_graph(shortcode, shortname)
    g = Graph()
    g.parse(format='n3', data=turtle)
    sparql="""
    SELECT ?res ?prop ?otype ?guiele ?attr ?card ?cardval
    WHERE {
        ?res a owl:Class .
        ?res rdfs:subClassOf ?restriction .
        ?restriction a owl:Restriction .
        ?restriction owl:onProperty ?prop .
        ?restriction ?card ?cardval .
        ?prop a owl:ObjectProperty .
        ?prop knora-api:objectType ?otype .
        ?prop salsah-gui:guiElement ?guiele .
        OPTIONAL { ?prop salsah-gui:guiAttribute ?attr } .
        FILTER(?card = owl:cardinality || ?card = owl:maxCardinality || ?card = owl:minCardinality)
    }
    ORDER BY ?res
    """
    qres = g.query(sparql)

    resources = []
    resclass = ''
    tmp = None
    for row in qres:
        nresclass = row.res.toPython()
        if (resclass != nresclass):
            if tmp is not None:
                resources.append(gaga)
            resclass = nresclass
            gaga = {"res_id": resclass, "props": {}}
        tmp["props"][row.prop.toPython()] = {
            "otype": row.otype.toPython(),
            "guiele": row.guiele.toPython(),
            "attr": row.attr.toPython() if row.attr is not None else None,
            "card": row.card.toPython(),
            "cardval": row.cardval.toPython()
       }
    resources.append(tmp)

    pprint(resources)


# let's read the schema for the ontology definition
if args.lists:
    with open('knora-schema-lists.json') as s:
        schema = json.load(s)
else:
    with open('knora-schema.json') as s:
        schema = json.load(s)

# read the ontology definition
with open(args.ontofile) as f:
    ontology = json.load(f)

# validate the ontology definition in order to be sure that it is correct
validate(ontology, schema)
print("Ontology is syntactically correct and passed validation!")

#if validate:
#    exit(0)

# create the knora connection object
con = knora(args.server, args.user, args.password, ontology.get("prefixes"))

# create_template(con, ontology["project"]["shortcode"], ontology["project"]["ontology"]["name"])
# exit(0)

if not args.lists:
    # create or update the project
    try:
        project = con.get_project(ontology["project"]["shortcode"])
    except KnoraError as err:
        proj_iri = con.create_project(
            shortcode=ontology["project"]["shortcode"],
            shortname=ontology["project"]["shortname"],
            longname=ontology["project"]["longname"],
            descriptions=ontology["project"]["descriptions"],
            keywords=ontology["project"]["keywords"]
        )
        print("New project created: IRI: " + proj_iri)
    else:
        print("Updating existing project!")
        print("Old project data:")
        pprint(project)
        proj_iri = con.update_project(
            shortcode=ontology["project"]["shortcode"],
            shortname=ontology["project"]["shortname"],
            longname=ontology["project"]["longname"],
            descriptions=ontology["project"]["descriptions"],
            keywords=ontology["project"]["keywords"]
        )
    project = con.get_project(ontology["project"]["shortcode"])
    print("New project data:")
    pprint(project)
else:
    project = con.get_project(ontology["project"]["shortcode"])
    proj_iri = project["id"]

# now let's create the lists
lists = ontology["project"].get('lists')
listrootnodes = {}
if lists is not None:
    for rootnode in lists:
        rootnode_iri = con.create_list_node(
            project_iri=proj_iri,
            name=rootnode['name'],
            labels=rootnode['labels'],
            comments=rootnode.get('comments')
        )
        listnodes = list_creator(con, proj_iri, rootnode_iri, rootnode_iri, rootnode['nodes'])
        listrootnodes[rootnode['name']] = {
            "id": rootnode_iri,
            "nodes": listnodes
        }


with open('lists.json', 'w', encoding="utf-8") as fp:
    json.dump(listrootnodes, fp, indent=3, sort_keys=True)

if args.lists:
    print("The definitions of the node-id's can be found in \"lists.json\"!")
    exit(0)

# now we start creating the ontology
# first we assemble the ontology IRI
onto_iri = args.server + "/ontology/" + ontology["project"]["shortcode"]\
           + "/" + ontology["project"]["ontology"]["name"] + "/v2"

# test, if the ontolgy already exists. if so, let's delete it!
ontos = con.get_project_ontologies(ontology["project"]["shortcode"])
if ontos is not None:
    for onto in ontos:
        if onto['iri'] == onto_iri:
            con.delete_ontology(onto_iri, onto['moddate'])
onto_data = con.create_ontology(
    onto_name=ontology["project"]["ontology"]["name"],
    project_iri=proj_iri,
    label=ontology["project"]["ontology"]["label"]
)

onto_iri = onto_data['onto_iri']
last_onto_date = onto_data['last_onto_date']

# let's create the resources
resource_ids = {}

for resource in ontology["project"]["ontology"]["resources"]:
    result = con.create_res_class(
        onto_iri=onto_iri,
        onto_name=ontology["project"]["ontology"]["name"],
        last_onto_date=last_onto_date,
        class_name=resource["name"],
        super_class=resource["super"] if ':' in resource["super"] else "knora-api:" + resource["super"],
        labels=resource["labels"]
    )
    last_onto_date = result["last_onto_date"]
    resource_ids[resource["name"]] = result["class_iri"]

pprint(resource_ids)

# let's create the properties
property_ids = {}
for resource in ontology["project"]["ontology"]["resources"]:
    for prop in resource["properties"]:
        guiattrs = prop.get("gui_attributes")
        if guiattrs is not None:
            new_guiattrs = []
            for guiattr in guiattrs:
                parts = guiattr.split("=")
                if parts[0] == "hlist":
                    new_guiattrs.append("hlist=<" + listrootnodes[parts[1]]["id"] + ">")
                else:
                    new_guiattrs.append(guiattr)
            guiattrs = new_guiattrs
            super_props = list(map(lambda a: a if ':' in a else "knora-api:" + a, prop["super"]))
            if prop.get("object") is not None:
                object = prop["object"] if ':' in prop["object"] else "knora-api:" + prop["object"]
            else:
                object = None
        result = con.create_property(
            onto_iri=onto_iri,
            onto_name=ontology["project"]["ontology"]["name"],
            last_onto_date=last_onto_date,
            prop_name=prop["name"],
            super_props=super_props,
            labels=prop["labels"],
            gui_element="salsah-gui:" + prop["gui_element"],
            gui_attributes=guiattrs,
            subject=prop.get("subject"),
            object=object,
            comments=prop.get("comments")
        )
        last_onto_date = result["last_onto_date"]
        property_ids[prop["name"]] = result['prop_iri']

# add the cardinalities
for resource in ontology["project"]["ontology"]["resources"]:
    for prop in resource["properties"]:
        print("=======>" + prop["name"] + "...")

        result = con.create_cardinality(
            onto_iri=onto_iri,
            onto_name=ontology["project"]["ontology"]["name"],
            last_onto_date=last_onto_date,
            class_iri=ontology["project"]["ontology"]["name"] + ':' + resource["name"],
            prop_iri=ontology["project"]["ontology"]["name"] + ':' + prop["name"],
            occurrence=prop["cardinality"]
        )
        last_onto_date = result["last_onto_date"]


