import json
from pprint import pprint

with open("js.txt", "r") as file:
    e = json.loads(file.read())

pprint(e, indent=2)
