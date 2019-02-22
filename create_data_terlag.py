import csv
import argparse
from pprint import pprint
from knora import KnoraError, knora, BulkImport



parser = argparse.ArgumentParser()
parser.add_argument("tabfile", help="path to tab separated data file")
parser.add_argument("-s", "--server", type=str, default="http://0.0.0.0:3333", help="URL of the Knora server")
parser.add_argument("-u", "--user", default="root@example.com", help="Username for Knora")
parser.add_argument("-p", "--password", default="test", help="The password for login")
parser.add_argument("-P", "--projectcode", required=True, help="Project short code")
parser.add_argument("-O", "--ontoname", required=True, help="Shortname of ontology")
parser.add_argument("-x", "--xml", default="data.xml", help="Name of bulk import XML-File")
parser.add_argument("--start", default="1", help="Start with given line")
parser.add_argument("--stop", default="all", help="End with given line ('all' reads all lines")

args = parser.parse_args()

con = knora(args.server, args.user, args.password)
schema = con.create_schema(args.projectcode, args.ontoname)

bulk = BulkImport(schema)

select_kreis = {
    "Territorialkreis 1": "tk1",
    "Territorialkreis 2": "tk2",
    "Territorialkreis 3": "tk3",
    "Territorialkreis 4": "tk4",
    "Territorialkreis 5": "tk5",
    "Territorialkreis 6": "tk6",
    "Territorialkreis 7": "tk7",
    "Territorialkreis 8": "tk8",
    "Territorialkreis 9a": "tk9a",
    "Territorialkreis 9b": "tk9b",
    "Territorialkreis 10": "tk10",
    "Territorialkreis 11": "tk11",
    "Territorialkreis 12": "tk12",
    "Territorialkreis Basel": "tkbasel",
    "Territorialkreis Genf": "tkgenf",
    "Territorialkreis Sargans": "tksargans",
    "nicht definiert": "tknd"
}

select_zahlenart = {
    'Zivilflüchlinge': 'zivil',
    'Militärflüchtlinge': 'militaer',
    'Französische Frauen und Kinder': 'franz',
    'Militärpersonal': 'milpers',
    'Flüchtlinge gesamt': 'gesamt',
    'Rückwanderer': 'rueck'
}

lagerfunktion = {
    'Auffanglager': 'auffanglager',
    'Quarantänelager': 'quarantaene',
    'Sammellager': 'sammellager',
    '(Grenz-)Desinfektionslager': 'desinfektionslager',
    'Militärquarantänelager': 'militaerlager',
    'Heimschaffungslager': 'heimschaffungslager',
    'Lager gesamt': 'gesamtlager',
    'andere': 'anderelager',
    'Gefängnis': 'gefaengnis',
    'Spital': 'spitallager',
    'Militärspital': 'militaerspitallager'
}

dates = []
lager = []
belegung_id = 0
with open(args.tabfile) as tsv:
    linecnt = 0
    old_lager_id = -1
    for line in csv.reader(tsv, dialect="excel", delimiter=';', quotechar='"'):
        linecnt = linecnt + 1
        print("Input line #" + str(linecnt))
        if linecnt == 1:  # We process the first line differently
            i = 9
            while i < len(line):
                print(line[i])
                tmp = line[i].split('.')
                if int(tmp[2]) < 100:
                    tmp[2] = '19' + tmp[2]
                datestr = "GREGORIAN:" + tmp[2] + '-' + tmp[1] + '-' + tmp[0]
                dates.append(datestr)
                i = i + 1
            continue
        if linecnt < int(args.start):
            continue
        if args.stop != "all" and linecnt > int(args.stop):
            continue
        lager_id = int(line[0])
        if lager_id != old_lager_id:  # we have a new lager, lets add it...
            old_lager_id = lager_id
            label = line[1]
            lagername = line[1]
            inKreis = select_kreis.get(line[3])
            if inKreis is None:
                raise KnoraError("inKreis unbekannt: " + line[3] + " Inputline: " + str(linecnt))
            if not line[6]:
                inBetrieb = "GREGORIAN:1900"
            else:
                tmp = line[6].split('-')
                ttmp1 = tmp[0].split('.')
                if int(ttmp1[2]) < 100:
                    ttmp1[2] = '19' + ttmp1[2]
                inBetrieb = "GREGORIAN:" + ttmp1[2] + '-' + ttmp1[1] + '-' + ttmp1[0]
            if len(tmp) > 1:
                ttmp2 = tmp[1].split('.')
                if int(ttmp2[2]) < 100:
                    ttmp2[2] = '19' + ttmp2[2]
                inBetrieb = inBetrieb + ':' + ttmp2[2] + '-' + ttmp2[1] + '-' + ttmp2[0]
            print(inBetrieb)
            bulk.add_resource(
                'lager',
                'LAGER_' + str(lager_id), label, {
                "lagername": lagername,
                "inKreis": inKreis,
                "inBetrieb": inBetrieb})

        for i in range(9,len(line)):
            label = "Belegung " + 'Datum'
            asFunction = lagerfunktion.get(line[4])
            if asFunction is None:
                raise KnoraError("Lagerfuntion unbekannt: " + line[4] + " Inputline: " + str(linecnt))
            zahlenart = select_zahlenart.get(line[5])
            periode = dates[i - 9]
            anzahl = line[i]
            if not anzahl:
                continue
            if anzahl == '*':
                continue
            inLager = lager_id
            bulk.add_resource('belegung', 'BELEGUNG_' + str(belegung_id), label, {'asFunction': asFunction,
                                                               'zahlenart': zahlenart,
                                                               'periode': periode,
                                                               'anzahl': anzahl,
                                                               'inLager': 'LAGER_' + str(inLager)})
            belegung_id = belegung_id + 1

bulk.write_xml(args.xml)


