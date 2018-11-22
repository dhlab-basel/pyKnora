from typing import List, Set, Dict, Tuple, Optional

import argparse
import json
import knora

parser = argparse.ArgumentParser()
parser.add_argument("server", help="URL of the Knora server")
parser.add_argument("-f", "--file", help="Input file in JSON format")
parser.add_argument("-u", "--user", help="Username for Knora")
parser.add_argument("-p", "--password", help="The password for login")
parser.add_argument("-n", "--nrows", type=int, help="number of records to get, -1 to get all")
parser.add_argument("-s", "--start", type=int, help="Start at record with given number")
args = parser.parse_args()

server = 'http://0.0.0.0:3333' if args.server is None else args.server
user = 'root@example.com' if args.user is None else args.user
password = 'test' if args.password is None else args.password
start = args.start
nrows = -1 if args.nrows is None else args.nrows


with open(args.file) as f:
    ontology = json.load(f)

#con = knora(server, user, password)
