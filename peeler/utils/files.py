import json
import os


def append_to(storage, prefix, name, record):
    filename = os.path.join(storage, f'{prefix}_{name}.json')
    if os.path.isfile(filename):
        print(f'append {prefix} to {filename}')
        with open(filename, 'r') as fp:
            output = json.load(fp)
    else:
        print(f'write {prefix} to {filename}')
        output = []
    output.append(record)
    with open(filename, 'w') as fp:
        json.dump(output, fp)
    print(f'save {prefix} done')