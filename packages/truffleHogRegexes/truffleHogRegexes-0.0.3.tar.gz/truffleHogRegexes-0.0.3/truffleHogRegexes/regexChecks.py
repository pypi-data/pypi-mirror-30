import re
import json

with open("regexes.json", 'r') as f:
    regexes = json.loads(f.read())

for key in regexes:
    regexes[key] = re.compile(regexes[key])
    print regexes[key].pattern

