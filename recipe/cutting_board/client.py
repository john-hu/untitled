import json
import re
from random import randint
from typing import List, TypedDict, Union

from pysolr import Solr, SolrError

from .utils import convert_solr_doc

SOLR_ESCAPE_RE = r'(")'
SOLR_ESCAPE_SUB = '\\\1'


class SearchHit(TypedDict):
    id: str
    data: dict


class RecipeSearchResult(TypedDict):
    query_time: int
    hits: int
    docs: List[SearchHit]
    error: Union[None, str]


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

    def random_recipe(self, count: int = 12):
        return self.search_recipe('*', page_size=count, sort=f'random_{randint(1, 100000)} desc')

    def search_recipe(self, query: str, page_index: int = 0, page_size: int = 36,
                      filters: list = None, sort: str = "description desc, instructions desc") -> RecipeSearchResult:
        escaped_query = re.sub(SOLR_ESCAPE_RE, SOLR_ESCAPE_SUB, query)
        try:
            solr_result = self.client.search(escaped_query, fl='id,_rawJSON_', start=page_index * page_size,
                                             rows=page_size, fq=filters if filters else [], sort=sort)
            return {'query_time': solr_result.qtime,
                    'hits': solr_result.hits,
                    'docs': [{'id': doc['id'], 'data': json.loads(doc['_rawJSON_'])} for doc in solr_result],
                    'error': None}
        except SolrError as ex:
            return {
                'query_time': 0,
                'hits': 0,
                'docs': [],
                'error': str(ex)
            }
