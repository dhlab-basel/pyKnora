# pyKnora
This library consists of
- ```knora.py``` Python modules for accessing Knora using the API (ontology creation, data import/export etc.)
- ```create_ontology.py``` A program to create an ontology out of a simple JSON description

## JSON ontology definition format

The JSON file contains a first object an object with the ```prefixes``` for
external ontologies that are being used, followed by the definition of
the project wic h includes all resources and properties:

### Prefixes

```json
{
  "prefixes": {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dcterms": "http://purl.org/dc/terms/"
  },
  "project": {…},
  
}
```

### Project data
The project definitions requires

- _"shortcode"_: A hexadecimal string in the range between "0000" and "FFFF" uniquely identifying the project. 
- _"shortname"_: A short name (string)
- a _"longname"_: A longer string giving the full name for the project
- _descriptions_: Strings describing the projects content. These
  descriptions can be supplied in several languages (currently _"en"_, _"de"_, _"fr"_ and _"it"_ are supported).
  The descriptions have to be given as JSON object with the language as key
  and the description as value. At least one description in one language is required.
- _keywords_: An array of keywords describing the project.
- _lists_: The definition of flat or hierarchical list (thesauri, controlled vocabularies)
- _ontology_: The definition of the data model (ontology)

This a project definition lokks like follows:
  
```json
"project": {
   "shortcode": "0809",
   "shortname": "tesex"
   "longname": "Test Example",
   "descriptions": {
     "en": "This is a simple example project with no value.",
     "de": "Dies ist ein einfaches, wertloses Beispielproject"
   }
   "keywords": ["example", "senseless"],
   "lists": […],
   "ontology": {…}
}
```

### Lists
A List consists of a root node identifing the list and an array of subnodes.
Each subnode may contain again subnodes (hierarchical list).
A node has the following elements:

- _name_: Name of the node. Should be unique for the given list
- _labels_: Language dependent labels
- _comments_: language dependent comments (optional)
- _nodes_: Array of subnodes (optional – leave out if there are no subnodes)

The _lists_ object contains an array of lists. Here an example:

```json
    "lists": [
      {
        "name": "orgtpye",
        "labels": { "de": "Organisationsart", "en": "Organization Type" },
        "nodes": [
          {
            "name": "business",
            "labels": { "en": "Commerce", "de": "Handel" },
            "comments": { "en": "no comment", "de": "kein Kommentar" },
            "nodes": [
              {
                "name": "transport",
                "labels": { "en": "Transportation", "de": "Transport" }
              },
              {
                "name": "finances",
                "labels": { "en": "Finances", "de": "Finanzen" }
              }
            ]
          },
          {
            "name": "society",
            "labels": { "en": "Society", "de": "Gesellschaft" }
          }
        ]
      }
    ]
```
the _lists_ element is optional.

## Ontology

The _ontology_ object contains the definition of the data model. The ontology has
the following elemens:

- _name_: The name of the ontology. This has to be a CNAME conformant name that can be use as prefix!
- _label_: Human readable and understandable name of the ontology
- _resources_: Array defining the resources (entities) of the data model

```json
    "ontology": {
      "name": "teimp",
      "label": "Test import ontology",
      "resources": […]
    }
```

### Resources
The resource classes are the primary entities of the data model. A resource class
is a template for the representation of a real object that is represented in
the DaSCh database. A resource class defines properties (aka _data fields_). For each of
these properties a data type as well as the cardinality have to defined.

A resource consists of the following definitions:

- _name_: A name for the resource
- _label_: The string displayed of the resource is being accessed
- _super_: A resource class is always derived from an other resource. The
  most generic resource class Knora offers is _"Resource"_. The following
  parent predefined resources are provided by knora:
  - _Resource_:
  - _StillImageRepresentation_:
  - _TextRepresentation_:
  - _AudioRepresentation_:
  - _DDDRepresentation_:
  - _DocumentRepresentation_:
  - _MovingImageRepresentation_:
  - _Annotation_:
  - _LinkObj_:
  - _Region_:
  
  However, a resource my be derived from a resource class in another ontology within the same project or
  from another resource class in the same ontology. In this case the reference
  has to have the form _prefix_:_resourceclassname_.
- _labels_: Language dependent, human readable names
- _comments_: Language dependend comments (optional)
- _properties_: Array of property definition for this resource class.

Example:

```json
     "resources": [
        {
          "name": "person",
          "super": "Resource",
          "labels": { "en": "Person", "de": "Person" },
          "comments": {
            "en": "Represents a human being",
            "de": "Repräsentiert eine Person/Menschen"
          },
          "properties": […]
        }
```

#### Properties
Properties are the definition of the data fields a resource class may or must have.
The properties object has the following fields:

- _name_: A name for the property
- _super_: A property has to be derived from at least one base property. The most generic base property
  Knora offers is _hasValue_. In addition the property may by als a subproperty of
  properties defined in external ontologies. In this case the qualified name including
  the prefix has to be given.
  The following base properties are definied by Knora:
  - _hasValue_:
  - _hasLinkTo_:
  - _hasColor_:
  - _hasComment_:
  - _hasGeometry_:
  - _isPartOf_:
  - _isRegionOf_:
  - _isAnnotationOf_:
  - _seqnum_:
  
- _object_: The "object" defines the type of the value that the property will store.
  The following object types are allowed:
  - _TextValue_:
  - _ColorValue_:
  - _DateValue_:
  - _DecimalValue_:
  - _GeomValue_:
  - _GeonameValue_:
  - _IntValue_:
  - _BooleanValue_:
  - _UriValue_:
  - _IntervalValue_:
  - _ListValue_: 
- _labels_:
- _gui_element_:
- _gui_attributes_:
- _cardinality_:
