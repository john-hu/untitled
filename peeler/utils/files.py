import json
import os


def append_to(storage, prefix, name, record):
    filename = os.path.join(storage, f'{prefix}_{name}.json')
    if os.path.isfile(filename):
        action = 'append'
        with open(filename, 'r') as fp:
            output = json.load(fp)
    else:
        action = 'write'
        output = []
    output.append(record)
    with open(filename, 'w') as fp:
        json.dump(output, fp)
    print(f'{action} {prefix} to {filename}')
