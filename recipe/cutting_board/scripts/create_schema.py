import json
from urllib import parse

import requests

FIELD_TYPES = {
    'dietenum': {
        'name': 'dietenum',
        'class': 'solr.EnumFieldType',
        'enumsConfig': 'recipeEnum.xml',
        'enumName': 'diet'
    }
}

FIELDS = {
    'id': {
        'name': 'id',
        'type': 'string',
        'multiValued': False,
        'indexed': True,
        'required': True,
        'stored': True
    },
    'categories': {
        'name': 'categories',
        'type': 'strings',
        'multiValued': True,
        'indexed': True,
        'required': True,
        'stored': False
    },
    'cookingMethod': {
        'name': 'cookingMethod',
        'type': 'strings',
        'multiValued': True,
        'indexed': True,
        'required': False,
        'stored': False
    },
    'cuisines': {
        'name': 'cuisines',
        'type': 'strings',
        'multiValued': True,
        'indexed': True,
        'required': False,
        'stored': False
    },
    'description': {
        'name': 'description',
        'type': 'text_general',
        'multiValued': False,
        'indexed': True,
        'required': False,
        'stored': True
    },
    'equipments': {
        'name': 'equipments',
        'type': 'strings',
        'multiValued': True,
        'indexed': True,
        'required': False,
        'stored': False
    },
    'ingredients': {
        'name': 'ingredients',
        'type': 'strings',
        'multiValued': True,
        'indexed': True,
        'required': True,
        'stored': False
    },
    'instructions': {
        'name': 'instructions',
        'type': 'strings',
        'multiValued': True,
        'indexed': True,
        'required': True,
        'stored': False
    },
    'ingredientsCount': {
        'name': 'ingredientsCount',
        'type': 'pint',
        'multiValued': False,
        'indexed': True,
        'required': False,
        'stored': False
    },
    'instructionsCount': {
        'name': 'instructionsCount',
        'type': 'pint',
        'multiValued': False,
        'indexed': True,
        'required': False,
        'stored': False
    },
    'keywords': {
        'name': 'keywords',
        'type': 'strings',
        'multiValued': True,
        'indexed': True,
        'required': False,
        'stored': False
    },
    'sourceSite': {
        'name': 'sourceSite',
        'type': 'string',
        'multiValued': False,
        'docValues': True,
        'indexed': True,
        'required': True,
        'stored': False
    },
    'suitableForDiet': {
        'name': 'suitableForDiet',
        'type': 'dietenum',
        'multiValued': True,
        'indexed': True,
        'required': False,
        'stored': False
    },
    'title': {
        'name': 'title',
        'type': 'text_general',
        'multiValued': False,
        'indexed': True,
        'required': True,
        'stored': True
    },
    'audios': {
        'name': 'audios',
        'type': 'boolean',
        'multiValued': False,
        'indexed': True,
        'required': False,
        'stored': False
    },
    'examples': {
        'name': 'examples',
        'type': 'boolean',
        'multiValued': False,
        'indexed': True,
        'required': False,
        'stored': False
    },
    'images': {
        'name': 'images',
        'type': 'boolean',
        'multiValued': False,
        'indexed': True,
        'required': False,
        'stored': False
    },
    'nutrition': {
        'name': 'nutrition',
        'type': 'boolean',
        'multiValued': False,
        'indexed': True,
        'required': False,
        'stored': False
    },
    'videos': {
        'name': 'videos',
        'type': 'boolean',
        'multiValued': False,
        'indexed': True,
        'required': False,
        'stored': False
    },
    'cookTime': {
        'name': 'cookTime',
        'type': 'pint',
        'multiValued': False,
        'indexed': True,
        'required': False,
        'stored': False
    },
    'prepTime': {
        'name': 'prepTime',
        'type': 'pint',
        'multiValued': False,
        'indexed': True,
        'required': False,
        'stored': False
    },
    'totalTime': {
        'name': 'totalTime',
        'type': 'pint',
        'multiValued': False,
        'indexed': True,
        'required': False,
        'stored': False
    },
    '_version_': {
        'name': '_version_',
        'type': 'plong',
        'multiValued': False,
        'indexed': False,
        'required': True,
        'stored': False
    },
    '_text_': {
        'name': '_text_',
        'type': 'text_general',
        'multiValued': True,
        'indexed': True,
        'required': False,
        'stored': False
    },
    '_rawJSON_': {
        'name': '_rawJSON_',
        'type': 'text_general',
        'multiValued': False,
        'indexed': False,
        'required': False,
        'stored': True
    }
}

# Some fields shouldn't be in the copied field:
# * id: we don't want the `http` or `https` to be indexed
COPY_FIELDS = [
    'categories',
    'cookingMethod',
    'cuisines',
    'description',
    'equipments',
    'ingredients',
    'instructions',
    'keywords',
    'suitableForDiet',
    'title'
]


def ensure_diet_enum(all_types, update_url):
    # ensure diet enum
    print('check diet enum.')
    for field_type in all_types:
        if field_type['name'] == 'dietenum':
            print('diet enum existed.')
            return
    payload = {'add-field-type': FIELD_TYPES['dietenum']}
    create_result = requests.post(update_url, data=json.dumps(payload))
    assert create_result.status_code == 200, f'create diet enum failed: {create_result.text}'


def should_replace(field1, field2):
    assert field1['name'] == field2[
        'name'], f'inconsistent field name, unable to compare: {field1["name"]}, {field2["name"]}'
    if field1.get('type', None) != field2.get('type', None):
        return True
    elif field1.get('multiValued', None) != field2.get('multiValued', None):
        return True
    elif field1.get('indexed', None) != field2.get('indexed', None):
        return True
    elif field1.get('required', None) != field2.get('required', None):
        return True
    elif field1.get('stored', None) != field2.get('stored', None):
        return True
    elif field1.get('docValues', None) != field2.get('docValues', None):
        return True
    elif field1.get('termVectors', None) != field2.get('termVectors', None):
        return True
    else:
        return False


def ensure_all_fields(all_fields, update_url):
    missing_fields = dict(FIELDS)
    print('remove useless fields')
    for field in all_fields:
        if field['name'] not in missing_fields:
            print(f'delete {field["name"]}')
            payload = {'delete-field': {'name': field['name']}}
            delete_result = requests.post(update_url, data=json.dumps(payload))
            assert delete_result.status_code == 200, f'delete field {field["name"]} failed: {delete_result.text}'
        elif should_replace(field, missing_fields[field['name']]):
            print(f'replace {field["name"]}')
            payload = {'replace-field': missing_fields[field['name']]}
            replace_result = requests.post(update_url, data=json.dumps(payload))
            assert replace_result.status_code == 200, f'replace field {field["name"]} failed: {replace_result.text}'
            del missing_fields[field['name']]
        else:
            print(f'keep {field["name"]}')
            del missing_fields[field['name']]
    print('add missing fields')
    for (key, definition) in missing_fields.items():
        print(f'add {key}')
        payload = {'add-field': definition}
        add_result = requests.post(update_url, data=json.dumps(payload))
        assert add_result.status_code == 200, f'add field {key} failed: {add_result.text}'


def ensure_all_copies(all_copies, update_url):
    # make a shallow clone for finding useless, existing and missing
    missing_copies = list(COPY_FIELDS)
    delete_list = []
    for copy_field in all_copies:
        # in our cases, we only copy fields to _text_ field for full-text search
        if copy_field['dest'] != '_text_':
            print(f'delete copy field to {copy_field["dest"]}')
            delete_list.append({'source': copy_field['source'], 'dest': copy_field['dest']})
        elif copy_field['source'] in missing_copies:
            # the field is already in missing_copies, pop it out.
            print(f'keep copy field {copy_field["source"]}')
            missing_copies.remove(copy_field['source'])
        else:
            print(f'delete copy field from {copy_field["source"]}')
            delete_list.append({'source': copy_field['source'], 'dest': copy_field['dest']})
    print('add missing copy fields')
    create_list = [{'source': source, 'dest': '_text_'} for source in missing_copies]
    payload = {
        'delete-copy-field': delete_list,
        'add-copy-field': create_list
    }
    execute_result = requests.post(update_url, data=json.dumps(payload))
    assert execute_result.status_code == 200, f'update copy fields failed: {execute_result.text}'


def print_all_fields(list_url):
    fields_resp = requests.get(list_url)
    assert fields_resp.status_code == 200, 'unable to list fields'
    all_schema = fields_resp.json()['schema']
    all_fields = all_schema['fields']
    print('All fields------------------------------------------------------')
    for field in all_fields:
        attr = ' '
        if 'multiValued' in field and field['multiValued']:
            attr += 'M'
        if 'indexed' in field and field['indexed']:
            attr += 'I'
        if 'required' in field and field['required']:
            attr += 'R'
        if 'stored' in field and field['stored']:
            attr += 'S'
        print(f'{field["name"]}: {field["type"]}{attr}')
    print('----------------------------------------------------------------')
    return all_fields, all_schema["fieldTypes"], all_schema["copyFields"]


def run(*args):
    assert len(args) >= 2, '{base_url} {collection}'
    base_url = args[0]
    collection = args[1]
    # all urls
    list_url = parse.urljoin(base_url, f'solr/{collection}/schema')
    update_url = parse.urljoin(base_url, f'solr/{collection}/schema')
    # list fields
    all_fields, all_types, all_copies = print_all_fields(list_url)
    # check and create diet enum
    ensure_diet_enum(all_types, update_url)
    # check and create all fields
    ensure_all_fields(all_fields, update_url)
    # check and create copy fields
    ensure_all_copies(all_copies, update_url)
    # dump it again
    print_all_fields(list_url)
