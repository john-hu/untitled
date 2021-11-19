import json
import requests
from urllib import parse
from argparse import ArgumentParser


class Uploader:
    def __init__(self, endpoint: str, username: str, password: str):
        self.__endpoint = parse.urljoin(endpoint, 'peeler/')
        self.__auth = (username, password)

    def pull_and_merge(self, recipe):
        get_endpoint = f'{self.__endpoint}{recipe["id"]}'
        print(get_endpoint)
        old_data = requests.get(get_endpoint, auth=self.__auth)
        if old_data.status_code == 200 and len(old_data.json()['docs']) > 0:
            final_data = old_data.json()['docs'][0]
            final_data.update(recipe)
            print('POST merged to server')
        else:
            final_data = recipe
            print('POST new data to server')
        result = requests.post(self.__endpoint, data=json.dumps([final_data]), auth=self.__auth)
        print(f'result: {result.status_code}, {result.text} for {recipe["id"]}')

    def upload(self, file: str, mode: str = 'pull_merge'):
        if mode == 'pull_merge':
            with open(file, 'r') as fp:
                recipes = json.load(fp)
            if not recipes and not isinstance(recipes, list):
                return

            for recipe in recipes:
                self.pull_and_merge(recipe)
        elif mode == 'push_all':
            with open(file, 'r') as fp:
                print('POST the whole file to server')
                headers = {'content-type': 'application/json'}
                result = requests.post(self.__endpoint, data=fp, auth=self.__auth, headers=headers)
                print(f'result: {result.status_code}, {result.text}')
        else:
            assert False, f'unsupported mode {mode}'


def run():
    parser = ArgumentParser(f'peeler data to silver plate uploader')
    parser.add_argument('--endpoint', type=str, required=True,
                        help='the endpoint of silver plate, like: http://localhost:8081')
    parser.add_argument('--username', type=str, required=True, help='basic auth username')
    parser.add_argument('--password', type=str, required=True, help='basic auth password')
    parser.add_argument('--mode', type=str, default='pull_merge', choices=['pull_merge', 'push_all'])
    parser.add_argument('file', type=str)
    args = parser.parse_args()
    Uploader(args.endpoint, args.username, args.password).upload(args.file, args.mode)


if __name__ == '__main__':
    run()
