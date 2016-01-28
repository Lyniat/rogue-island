import json
import os



def load_entities(path):
    for file in os.listdir(path):
        print file
        if not file.endswith('.json'):
            continue
        with open(path+"/"+file, 'r') as content_file:
            content = content_file.read()

        values = json.loads(content)

        print values
