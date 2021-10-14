from pysolr import Solr


class Client:
    def __init__(self, cutting_board_url):
        self.client = Solr(cutting_board_url)

    def ping(self):
        return self.client.ping()

    def get_recipe(self, recipe_id: str):
        # TODO: escape id
        results = self.client.search(f'id:"{recipe_id}"')
        return {'recipe_id': recipe_id, 'num_of_found': len(results), 'docs': results.docs}
