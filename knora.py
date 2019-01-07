from typing import List, Set, Dict, Tuple, Optional

import requests
import json
import argparse
import urllib
import pprint

# TODO: recheck all the documentation of this file
"""
 Properties in knora-api:

 - :hasValue
 - :hasColor
 - :hasComment
 - :hasGeometry
 - :hasLinkTo
 - :isPartOf
 - :isRegionOf
 - :isAnnotationOf
 - :seqnum

 Classes in knora-api:

 - :Resource
 - :StillImageRepresentation
 - :TextRepresentation
 - :AudioRepresentation
 - :DDDRepresentation
 - :DocumentRepresentation
 - :MovingImageRepresentation
 - :Annotation -> :hasComment, :isAnnotationOf, :isAnnotationOfValue
 - :LinkObj -> :hasComment, :hasLinkTo, :hasLinkToValue
 - :LinkValue [reification node]
 - :Region -> :hasColor, :isRegionOf, :hasGeometry, :isRegionOfValue, :hasComment

 For lists:

 - :ListNode -> :hasSubListNode, :listNodePosition, :listNodeName, :isRootNode, :hasRootNode, :attachedToProject

 Values in knora-api:

 - :Value
 - :TextValue
 - :ColorValue
 - :DateValue
 - :DecimalValue
 - :GeomValue
 - :GeonameValue
 - :IntValue
 - :BooleanValue
 - :UriValue
 - :IntervalValue
 - :ListValue

 GUI elements

 - :Colorpicker
 - :Date
 - :Geometry
 - :Geonames
 - :Interval
 - :List
 - :Pulldown
 - :Radio
 - :Richtext
 - :Searchbox
 - :SimpleText
 - :Slider
 - :Spinbox
 - :Textarea
 - :Checkbox
 - :Fileupload

"""
class KnoraError(Exception):
    """Handles errors happening in this file"""
    # TODO: Implement this
    pass


class knora:
    """
    Class to interface with Knora API
    """

    def __init__(self, server, user, password):
        """
        Constructor requiring the server address, the user and password of KNORA
        :param server: Adress of the server, e.g http://data.dasch.swiss
        :param user: Username for Knora e.g., root@example.com
        :param password: The password, e.g. test
        """
        self.server = server
        self.user = user
        self.password = password

    def on_api_error(self, res):
        """
        Method to check for any API errors
        :param res: The input to check, usually JSON format
        :return: Possible KnoraError that is being raised
        """
        if 'error' in res:
            raise KnoraError("KNORA-ERROR: API error: " + res.error)

    def get_existing_projects(self):
        """Returns a list of existing projects

        :return: List of existing projects
        """

        req = requests.get(self.server + '/admin/projects', auth=(self.user, self.password))
        self.on_api_error(req)
        result = req.json()

        if not 'projects' in result:
            raise KnoraError("KNORA-ERROR:\n Request got no projects!")
        else:
            return list(map(lambda a: a['id'], result['projects']))

    def get_project(self, project_iri: str):
            """Returns a list of existing projects

            :return: List of existing projects
            """

            url = self.server + '/admin/projects/' + urllib.parse.quote_plus(project_iri)
            pprint.pprint(url)
            req = requests.get(url, auth=(self.user, self.password))
            self.on_api_error(req)
            result = req.json()
            return result['project']


    def project_exists(self, proj_iri):
        """Checks if a given project exists

        :return: Boolean
        """

        projects = self.get_existing_projects()
        return proj_iri in projects

    def create_project(
            self,
            shortcode: str,
            shortname: str,
            longname: str,
            description: Dict[str, str],
            keywords: List[str],
            logo: Optional[str] = None) -> str:
        """
        Create a new project

        :param shortcode: Dedicated shortcode of project
        :param shortname: Short name of the project (e.g acronym)
        :param longname: Long name of project
        :param description: Dict of the form {lang: descr, …} for the description of the project
        :param keywords: List of keywords
        :param logo: Link to the project logo [default: None]
        :return: Project IRI
        """

        description = list(map(lambda p: {"language": p[0], "value": p[1]}, description.items()))

        project = {
            "shortname": shortname,
            "shortcode": shortcode,
            "longname": longname,
            "description": description,
            "keywords": keywords,
            "logo": logo,
            "status": True,
            "selfjoin": False
        }

        jsondata = json.dumps(project)

        req = requests.post(self.server + "/admin/projects",
                            headers={'Content-Type': 'application/json; charset=UTF-8'},
                            data=jsondata,
                            auth=(self.user, self.password))
        self.on_api_error(req)

        res = req.json()
        print("---RESULT OF PROJECT CREATION----")
        pprint.pprint(res)
        print("==================================")
        return res["project"]["id"]

    def get_existing_ontologies(self):
        """

        :return: Returns the metadata of all existing ontologies on v2/ontologies
        """

        req = requests.get(self.server + '/v2/ontologies/metadata', auth=(self.user, self.password))
        result = req.json()

        if not '@graph' in result:
            raise KnoraError("KNORA-ERROR:\n Request got no graph!")
        else:
            names = list(map(lambda a: a['@id'], result['@graph']))
            return names

    def ontology_exists(self, onto_iri: str):
        """
        Checks if an ontology exists
        :param onto_iri: The possible ontology iri
        :return: boolean
        """

        ontos = self.get_existing_ontologies()

        return onto_iri in ontos

    def get_ontology_lastmoddate(self, onto_iri: str):
        """
        Retrieves the lastModificationDate of a Ontology

        :param onto_iri: The ontology to retrieve the lastModificationDate from.
        :return: The lastModificationDate if it exists. Else, this method returns a dict with (id, None). If the ontology does not exist, it return None.
        """

        req = requests.get(self.server + '/v2/ontologies/metadata', auth=(self.user, self.password))
        result = req.json()

        all_ontos = {}

        for onto in result['@graph']:
            if 'knora-api:lastModificationDate' in onto:
                all_ontos.__setitem__(onto['@id'], onto['knora-api:lastModificationDate'])
            else :
                all_ontos.__setitem__(onto['@id'], None)

        return all_ontos[onto_iri]

    def create_ontology(self,
                        onto_name: str,
                        project_iri: str,
                        label: str) -> Dict[str, str]:
        """
        Create a new ontology

        :param onto_name: Name of the omntology
        :param project_iri: IRI of the project
        :param label: A label property for this ontology
        :return: Dict with "onto_iri" and "last_onto_date"
        """
        
        ontology = {
            "knora-api:ontologyName": onto_name,
            "knora-api:attachedToProject": {
                "@id": project_iri
            },
            "rdfs:label": label,
            "@context": {
                "rdfs": 'http://www.w3.org/2000/01/rdf-schema#',
                "knora-api": 'http://api.knora.org/ontology/knora-api/v2#'
            }
        }

        jsondata = json.dumps(ontology)

        req = requests.post(self.server + "/v2/ontologies",
                            headers={'Content-Type': 'application/json; charset=UTF-8'},
                            data=jsondata,
                            auth=(self.user, self.password))

        self.on_api_error(req)

        res = req.json()
        print("---RESULT OF ONTOLOGY CREATION----")
        pprint.pprint(res)
        print("==================================")
        #TODO: return also ontology name
        return {"onto_iri": res['@id'], "last_onto_date": res['knora-api:lastModificationDate']}

    def delete_ontology(self, onto_iri: str, last_onto_date = None):
        """
        A method to delete an ontology from /v2/ontologies 
        :param onto_iri: The ontology to delete
        :param last_onto_date: the lastModificationDate of an ontology. None by default
        :return: 
        """"" #TODO: add return documentation
        url = self.server + "/v2/ontologies/" + urllib.parse.quote_plus(onto_iri)
        pprint.pprint(url)
        req = requests.delete(url,
                              params={"lastModificationDate": last_onto_date},
                              auth=(self.user, self.password))
        self.on_api_error(req)
        res = req.json()
        print("---RESULT OF ONTOLOGY DELETION----")
        pprint.pprint(res)
        print("==================================")
        return req

    def create_res_class(self,
                         onto_iri: str,
                         onto_name: str,
                         last_onto_date: str,
                         class_name: str,
                         super_class: List[str],
                         labels: Dict[str, str],
                         comments: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Creates a knora resource class

        :param onto_iri: IRI of the ontology
        :param onto_name: Name of the ontology
        :param last_onto_date: Last modification date as returned by last call
        :param class_name: Name of the class to be created
        :param super_class: List of super classes
        :param labels: Dict with labels in the form { lang: labeltext }
        :param comments: Dict with comments in the form { lang: commenttext }
        :return: Dict with "class_iri" and "last_onto_date"
        """

        #
        # using map and iterable to get the proper format
        #
        labels = list(map(lambda p: {"@language": p[0], "@value": p[1]}, labels.items()))

        if not comments:
            comments = {"en": "none"}

        #
        # using map and iterable to get the proper format
        #
        comments = list(map(lambda p: {"@language": p[0], "@value": p[1]}, comments.items()))

        res_class = {
            "@id": onto_iri,
            "@type": "owl:Ontology",
            "knora-api:lastModificationDate": last_onto_date,
            "@graph": [{
                "@id": onto_name + ":" + class_name,
                "@type": "owl:Class",
                "rdfs:label": labels,
                "rdfs:comment": comments,
                "rdfs:subClassOf": {
                    "@id": super_class
                }
            }],
            "@context": {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                onto_name: onto_iri + "#"
            }
        }

        jsondata = json.dumps(res_class, indent=3, separators=(',', ': '))

        print(jsondata)
        req = requests.post(self.server + "/v2/ontologies/classes",
                            headers={'Content-Type': 'application/json; charset=UTF-8'},
                            data=jsondata,
                            auth=(self.user, self.password))
        self.on_api_error(req)

        res = req.json()

        print("---RESULT OF CLASS CREATION----")
        pprint.pprint(res)
        print("=================================")

        return {"class_iri": res['@graph'][0]['@id'], "last_onto_date": res['knora-api:lastModificationDate']}

    def create_property(
            self,
            onto_iri: str,
            onto_name: str,
            last_onto_date: str,
            prop_name: str,
            super_props: List[str],
            labels: Dict[str, str],
            gui_element: str,
            gui_attributes: List[str] = None,
            subject: Optional[str] = None,
            object: Optional[str] = None,
            comments: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Create a Knora property

        :param onto_iri: IRI of the ontology
        :param onto_name: Name of the Ontology (prefix)
        :param last_onto_date: Last modification date as returned by last call
        :param prop_name: Name of the property
        :param super_props: List of super-properties
        :param labels: Dict with labels in the form { lang: labeltext }
        :param gui_element: Valid GUI-Element
        :param gui_attributes: Valid GUI-Attributes (or None
        :param subject: Full name (prefix:name) of subject resource class
        :param object: Full name (prefix:name) of object resource class
        :param comments: Dict with comments in the form { lang: commenttext }
        :return: Dict with "prop_iri" and "last_onto_date" keys
        """
        #
        # using map and iterable to get the proper format
        #
        labels = list(map(lambda p: {"@language": p[0], "@value": p[1]}, labels.items()))


        if not comments:
            comments = {"en": "none"}

        #
        # using map and iterable to get the proper format
        #
        comments = list(map(lambda p: {"@language": p[0], "@value": p[1]}, comments.items()))

        #
        # using map and iterable to get the proper format
        #
        super_props = list(map(lambda x: {"@id": x}, super_props))

        propdata = {
            "@id": onto_name + ":" + prop_name,
            "@type": "owl:ObjectProperty",
            "rdfs:label": labels,
            "rdfs:comment": comments,
            "rdfs:subPropertyOf": super_props,
            "salsah-gui:guiElement": {
                "@id": gui_element
            }
        }
        if subject:
            propdata["knora-api:subjectType"] = {
                "@id": subject
            }

        if object:
            propdata["knora-api:objectType"] = {
                "@id": object
            }
        if gui_attributes:
            propdata["salsah-gui:guiAttribute"] = gui_attributes

        property = {
            "@id": onto_iri,
            "@type": "owl:Ontology",
            "knora-api:lastModificationDate": last_onto_date,
            "@graph": [
                propdata
            ],
            "@context": {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
                "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#",
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "dcterms": "http://purl.org/dc/terms/",
                onto_name: onto_iri + "#"
            }
        }

        jsondata = json.dumps(property, indent=3, separators=(',', ': '))

        print(jsondata)

        req = requests.post(self.server + "/v2/ontologies/properties",
                            headers={'Content-Type': 'application/json; charset=UTF-8'},
                            data=jsondata,
                            auth=(self.user, self.password))
        self.on_api_error(req)

        res = req.json()

        print("---RESULT OF PROPERTY CREATION----")
        pprint.pprint(res)
        print("=================================")

        return {"prop_iri": res['@graph'][0]['@id'], "last_onto_date": res['knora-api:lastModificationDate']}

    def create_cardinality(
            self,
            onto_iri: str,
            onto_name: str,
            last_onto_date: str,
            class_iri: str,
            prop_iri: str,
            occurrence: str
    ) -> Dict[str, str]:
        """Add a property with a given cardinality to a class

        :param onto_iri: IRI of the ontology
        :param onto_name: Name of the ontology (prefix)
        :param last_onto_date: Last modification date as returned by last call
        :param class_iri: IRI of the class to which the property will be added
        :param prop_iri: IRI of the property that should be added
        :param occurrence: Occurrence: "1", "0-1", "0-n" or "1-n"
        :return: Dict with "last_onto_date" key
        """
        switcher = {
            "1": ("owl:cardinality", 1),
            "0-1": ("owl:maxCardinality", 1),
            "0-n": ("owl:minCardinality", 0),
            "1-n": ("owl:minCardinality", 1)
        }
        occurrence = switcher.get(occurrence)
        if not occurrence:
            KnoraError("KNORA-ERROR:\n Invalid occurrence!")

        cardinality = {
            "@id": onto_iri,
            "@type": "owl:Ontology",
            "knora-api:lastModificationDate": last_onto_date,
            "@graph": [{
                "@id": class_iri,
                "@type": "owl:Class",
                "rdfs:subClassOf": {
                    "@type": "owl:Restriction",
                    occurrence[0]: occurrence[1],
                    "owl:onProperty": {
                        "@id": prop_iri
                    }
                }
            }],
            "@context": {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                onto_name: onto_iri + "#"
            }
        }

        jsondata = json.dumps(cardinality, indent=3, separators=(',', ': '))

        print(jsondata)

        req = requests.post(self.server + "/v2/ontologies/cardinalities",
                            headers={'Content-Type': 'application/json; charset=UTF-8'},
                            data=jsondata,
                            auth=(self.user, self.password))
        self.on_api_error(req)

        res = req.json()

        print("---RESULT OF CARDINALIY CREATION----")
        pprint.pprint(res)
        print("=================================")

        return {"last_onto_date": res["knora-api:lastModificationDate"]}

    def create_list_node(self,
                         project_iri: str,
                         labels: Dict[str, str],
                         comments: Dict[str, str],
                         name: Optional[str] = None,
                         parent_iri: Optional[str] = None) -> str:
        """
        Creates a new list node. If there is no parent, a root node is created

        :param project_iri: IRI of the project
        :param labels: Dict in the form {lang: label, …} giving the label(s)
        :param comments: Dict in the form {lang: comment, …} giving the comment(s)
        :param name: Name of the list node
        :param parent_iri: None for root node (or omit), otherwise IRI of parent node
        :return: IRI of list node
        """

        #
        # using map and iterable to get the proper format
        #
        labels = list(map(lambda p: {"language": p[0], "value": p[1]}, labels.items()))

        #
        # using map and iterable to get the proper format
        #
        comments = list(map(lambda p: {"language": p[0], "value": p[1]}, comments.items()))

        listnode = {
            "projectIri": project_iri,
            "labels": labels,
            "comments": comments
        }

        if name:
            listnode["name"] = name

        if parent_iri:
            listnode["parentNodeIri"] = parent_iri

        jsondata = json.dumps(listnode, indent=3, separators=(',', ': '))

        print(jsondata)

        req = requests.post(self.server + "/admin/lists",
                            headers={'Content-Type': 'application/json; charset=UTF-8'},
                            data=jsondata,
                            auth=(self.user, self.password))
        self.on_api_error(req)

        res = req.json()

        print("---RESULT OF LIST NODE CREATION----")
        pprint.pprint(res)
        print("=================================")

        return res["list"]["listinfo"]["id"]


parser = argparse.ArgumentParser()
parser.add_argument("server", help="URL of the Knora server")
parser.add_argument("-u", "--user", help="Username for Knora")
parser.add_argument("-p", "--password", help="The password for login")
parser.add_argument("-n", "--nrows", type=int, help="number of records to get, -1 to get all")
parser.add_argument("-s", "--start", type=int, help="Start at record with given number")
args = parser.parse_args()

user = 'root@example.com' if args.user is None else args.user
password = 'test' if args.password is None else args.password
start = args.start
nrows = -1 if args.nrows is None else args.nrows


con = Knora(args.server, user, password)

p = con.get_existing_projects()

pprint.pprint(p)

pp = con.get_project(p[1])
pprint.pprint(pp)

# proj_iri = con.create_project(
#     shortcode="1011",
#     shortname="TdK",
#     longname="Tal der Könige",
#     description={"en": "Excavation in the Valley of the Kings", "de": "Ausgrabungen im Tal der Könige"},
#     keywords=("archaeology", "excavation")
# )
#
#
# node1 = con.create_list_node(proj_iri, {"en": "ROOT"}, {"en": "This is the root node"}, "RootNode")
# subnode1 = con.create_list_node(proj_iri, {"en": "SUB1"}, {"en": "This is the sub node 1"}, "SubNode1", node1)
# subnode2 = con.create_list_node(proj_iri, {"en": "SUB2"}, {"en": "This is the sub node 2"}, "SubNode2", node1)
# subnode3 = con.create_list_node(proj_iri, {"en": "SUB3"}, {"en": "This is the sub node 3"}, "SubNode3", node1)
#
#
# result = con.create_ontology(
#     onto_name="tdk",
#     project_iri=proj_iri,
#     label="Tal der Könige")
# onto_iri = result["onto_iri"]
# last_onto_date = result["last_onto_date"]
#
# labels = {
#     "en": "Study Materials / Findings",
#     "de": "SM / Fund"
# }
# result = con.create_res_class(
#     onto_iri=onto_iri,
#     onto_name="tdk",
#     last_onto_date=last_onto_date,
#     class_name="SMFund",
#     super_class="knora-api:Resource",
#     labels=labels
# )
# last_onto_date = result["last_onto_date"]
#
# result = con.create_property(
#     onto_iri=onto_iri,
#     onto_name="tdk",
#     last_onto_date=last_onto_date,
#     prop_name="smAreal",
#     super_props=["knora-api:hasValue"],
#     labels={"de": "Areal", "en": "area"},
#     gui_element="salsah-gui:SimpleText",
#     gui_attributes=["size=12", "maxlength=32"],
#     subject="tdk:SMFund",
#     object="knora-api:TextValue"
# )
# last_onto_date = result["last_onto_date"]
# prop_iri = result["prop_iri"]
#
# result=con.create_cardinality(
#             onto_iri=onto_iri,
#             onto_name="tdk",
#             last_onto_date=last_onto_date,
#             class_iri="tdk:SMFund",
#             prop_iri=prop_iri,
#             occurrence="0-1"
# )
# last_onto_date = result["last_onto_date"]
#
# last_onto_date = con.get_ontology_lastmoddate(onto_iri)
# con.delete_ontology(onto_iri, last_onto_date)
#
#
#
