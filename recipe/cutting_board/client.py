import json
import re
from typing import List

from pysolr import Solr

from .utils import convert_solr_doc

SOLR_ESCAPE_RE = r'(")'
SOLR_ESCAPE_SUB = '\\\1'


class Client:
    def __init__(self, cutting_board_url):
        self.client = Solr(cutting_board_url)

    def ping(self):
        return self.client.ping()

    def get_recipe(self, recipe_id: str) -> dict:
        escaped_id = re.sub(SOLR_ESCAPE_RE, SOLR_ESCAPE_SUB, recipe_id)
        q = f'id:"{escaped_id}"'
        results = self.client.search(q)
        return {'recipe_id': recipe_id, 'num_of_found': len(results),
                'docs': [json.loads(doc['_rawJSON_']) for doc in results.docs]}

    def delete_recipe(self, recipe_id: str) -> None:
        self.client.delete(id=recipe_id, commit=True)

    def add_recipe(self, docs: List[dict]) -> None:
        self.client.add([convert_solr_doc(doc) for doc in docs], commit=True)
