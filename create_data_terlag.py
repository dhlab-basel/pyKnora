import csv
import argparse
from pprint import pprint
from lxml import etree


data = {
    "lager": {
        "lagername": {
            "pos: 1"
        },
        "inKreis": {
            "pos": 3
        },
        "inBetrieb": {
            "pos": 6
        }
    },
    "belegung": {
        "asFunction": {
            "pos": 4
        },
        "zahlenart": {
            "pos": 5
        }

    }
}



class Lager:
    def __init__(self, id: str, label, lagername: str, inKreis: str, inBetrieb: str):
        self.lagername = lagername
        self.inKreis = inKreis
        self.inBetries = inBetrieb

    def toXml(self):
        return

class Belegung:
    def __init__(self, id: str, label: str, anzahl: int, lager: str):

parser = argparse.ArgumentParser()
parser.add_argument("tabfile", help="path to tab separated data file")
parser.add_argument("-l", "--lists", type=str, help="URL of the Knora server")
# parser.add_argument("-u", "--user", default="root@example.com", help="Username for Knora")
# parser.add_argument("-p", "--password", default="test", help="The password for login")

args = parser.parse_args()

# read list data
with open(args.list) as f:
    lists = json.load(f)

dates = []
lager = []
with open(args.tabfile, encoding="ISO-8859-1") as tsv:
    linecnt = 1
    for line in csv.reader(tsv, dialect="excel-tab"):
        if linecnt == 1:
            i = 9
            while i < len(line):
                tmp = line[i].split('.')
                datestr = "GREGORIAN:19" + tmp[2] + '-' + tmp[1] + '-' + tmp[0]
                dates.append(datestr)
                i = i + 1
            continue
        id = int(line[0])
        label = line[1]
        lagername = line[1]
        switcher = {
            "Territorialkreis 1": lists["kreis"]["nodes"]["tk1"]["id"],
            "Territorialkreis 2": lists["kreis"]["nodes"]["tk1"]["id"],
            "Territorialkreis 3": lists["kreis"]["nodes"]["tk1"]["id"],
            "Territorialkreis 4": lists["kreis"]["nodes"]["tk1"]["id"],
            "Territorialkreis 5": lists["kreis"]["nodes"]["tk1"]["id"],
            "Territorialkreis 6": lists["kreis"]["nodes"]["tk1"]["id"],
            "Territorialkreis 7": lists["kreis"]["nodes"]["tk1"]["id"],
            "Territorialkreis 8": lists["kreis"]["nodes"]["tk1"]["id"],
            "Territorialkreis 9a": lists["kreis"]["nodes"]["tk1"]["id"],
            "Territorialkreis 9b": lists["kreis"]["nodes"]["tk1"]["id"],
            "Territorialkreis Basel": lists["kreis"]["nodes"]["tkbasel"]["id"],
            "Territorialkreis Genf": lists["kreis"]["nodes"]["tkgenf"]["id"],
            "Territorialkreis Sargans": lists["kreis"]["nodes"]["tksargans"]["id"],
            "nicht definiert": lists["kreis"]["nodes"]["tknd"]["id"]
        }
        inKreis = line[3]
        tmp = line[6].split('-')
        ttmp1 = tmp[0].split('.')
        inBetrieb = "GREGORIAN:" + ttmp1[2] + '-' + ttmp1[1] + '-' + ttmp1[0]
        if len(tmp) > 1:
            ttmp2 = tmp[1].split('.')
            inBetrieb = inBetrieb + ':' + ttmp2[2] + '-' + ttmp2[1] + '-' + ttmp2[0]
        lager.append(Lager(label=label, lagername=lagername, inKreis=inKreis, inBetrieb=inBetrieb))

root = etree.XML('''\
<?xml version="1.0" encoding="UTF-8"?>
<knoraXmlImport:resources
    xmlns="http://api.knora.org/ontology/0801/biblio/xml-import/v1#"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://api.knora.org/ontology/0801/biblio/xml-import/v1# p0808-terlag.xsd"
    xmlns:p0808-terlag="http://api.knora.org/ontology/0801/biblio/xml-import/v1#"
    xmlns:knoraXmlImport="http://api.knora.org/ontology/knoraXmlImport/v1#">...
''')
xmlstr = etree.tostring(root, method='text', encoding="UTF-8")
print(xmlstr)
