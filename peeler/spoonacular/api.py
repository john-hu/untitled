from urllib import parse

import requests

BASE_URL = 'https://api.spoonacular.com'
RANDOM_PATH = '/recipes/random'


class SpoonacularAPI:
    def __init__(self, api_key):
        self.__api_key = api_key
        self.used_quote = 0

    def random_recipe(self):
        url = parse.urljoin(BASE_URL, f'{RANDOM_PATH}?apiKey={self.__api_key}&number=1')
        source = requests.get(url)
        assert source.status_code == 200, f'unable to fetch random recipe: {source.text}'
        self.used_quote = float(source.headers['X-API-Quota-Used'])
        recipes = source.json().get('recipes', [])
        assert recipes, f'empty recipe found: {source.text}'
        return recipes[0]
