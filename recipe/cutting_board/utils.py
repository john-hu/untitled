import json


SOLR_DOC_VERSION = 1


def convert_solr_doc(recipe: dict):
    # total fields: 23

    # 13 fields: required fields, boolean fields, number fields.
    solr_doc = {
        'id': recipe['id'],
        'categories': recipe['categories'],
        'ingredients': [ingredient['name'] for ingredient in recipe['ingredients']],
        'instructions': [instruction['text'] for instruction in recipe['instructions']],
        'title': recipe['title'],
        'sourceSite': recipe['sourceSite'],
        'audios': len(recipe.get('audios', [])) > 0,
        'images': len(recipe.get('images', [])) > 0,
        'videos': len(recipe.get('videos', [])) > 0,
        'examples': len(recipe.get('examples', [])) > 0,
        'ingredientsCount': len(recipe['ingredients']),
        'instructionsCount': len(recipe['instructions']),
        'nutrition': 'nutrition' in recipe,
        '_rawJSON_': json.dumps(recipe)
    }
    # conditional 10 fields
    if 'cookingMethod' in recipe:
        solr_doc['cookingMethod'] = recipe['cookingMethod']
    if 'cuisines' in recipe:
        solr_doc['cuisines'] = recipe['cuisines']
    if 'description' in recipe:
        solr_doc['description'] = recipe['description']
    if 'equipments' in recipe:
        solr_doc['equipments'] = recipe['equipments']
    if 'keywords' in recipe:
        solr_doc['keywords'] = recipe['keywords']
    if 'suitableForDiet' in recipe:
        solr_doc['suitableForDiet'] = recipe['suitableForDiet']
    if 'cookTime' in recipe:
        solr_doc['cookTime'] = recipe['cookTime']
    if 'prepTime' in recipe:
        solr_doc['prepTime'] = recipe['prepTime']
    if 'totalTile' in recipe:
        solr_doc['totalTile'] = recipe['totalTile']
    return solr_doc
