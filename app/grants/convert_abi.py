import json
from pprint import pprint

with open('abi_v1.json') as json_file:
    abi = json.load(json_file)
    print(abi['abi'])

with open('abi_v1.py', 'w') as python_file:
    pprint(abi['abi'], stream=python_file)
