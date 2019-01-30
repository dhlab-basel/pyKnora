import argparse
import json
import csv
from unidecode import unidecode

parser = argparse.ArgumentParser()

parser.add_argument("csvfile", help="Path to CSV file (input)")
parser.add_argument("jsonfile", help="Path to JSON file (output")

args = parser.parse_args()

functions = []


with open(args.csvfile, mode="r", encoding='utf-8-sig') as csvfile:
    linecnt = 0
    for line in csv.reader(csvfile, delimiter=';', quotechar='"'):
        linecnt += 1
        if line[1]:
            function = {}
            function["name"] = "PF_" + line[0]
            function["labels"] = {"de": line[1]}
            print(line[1])
            functions.append(function)


with open(args.jsonfile, 'w', encoding="utf-8") as outfile:
    json.dump(functions, outfile, indent=3, separators=(',', ': '), ensure_ascii=False)

exit(0)