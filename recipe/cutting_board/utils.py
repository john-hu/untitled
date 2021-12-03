import json

SOLR_DOC_VERSION = 1


def convert_solr_doc(recipe: dict):
    # total fields: 23

    # 9 fields: required fields, boolean fields, number fields.
    solr_doc = {
        'id': recipe['id'],
        'categories': recipe['categories'],
        'title': recipe['title'],
        'sourceSite': recipe['sourceSite'],
        'audios': len(recipe.get('audios')) > 0 if recipe.get('audios') else False,
        'images': len(recipe.get('images')) > 0 if recipe.get('images') else False,
        'videos': len(recipe.get('videos')) > 0 if recipe.get('videos') else False,
        'examples': len(recipe.get('examples')) > 0 if recipe.get('examples') else False,
        'nutrition': True if recipe.get('nutrition') else False,
        '_rawJSON_': json.dumps(recipe)
    }
    # conditional 14 fields
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
    # parsed or raw
    if recipe.get('ingredients'):
        solr_doc['ingredients'] = [ingredient['name']
                                   for ingredient in recipe['ingredients']]
        solr_doc['ingredientsCount'] = len(recipe['ingredients'])
    else:
        solr_doc['ingredients'] = recipe['ingredientsRaw']
        solr_doc['ingredientsCount'] = len(recipe['ingredientsRaw'])
    if recipe.get('instructions'):
        solr_doc['instructions'] = [instruction['text']
                                    for instruction in recipe['instructions']]
        solr_doc['instructionsCount'] = len(recipe['instructions'])
    else:
        solr_doc['instructions'] = recipe['instructionsRaw']
        solr_doc['instructionsCount'] = len(recipe['instructionsRaw'])
    return solr_doc
