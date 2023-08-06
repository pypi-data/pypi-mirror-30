
import argparse
import re
import sys

import yaml
import json

with open(sys.argv[1], "r") as encstream:
    for doc in yaml.load_all(encstream):
        print(json.dumps(doc))
