import argparse
import os
import time

from . import version
from .peeler import SpoonacularPeeler


def main():
    parser = argparse.ArgumentParser(f'Spoonacular API peeler, {version}')
    parser.add_argument('--api_key', type=str, required=True)
    parser.add_argument('--reconvert', type=str)
    parser.add_argument('--storage', type=str, default=os.path.join('peeler_output', 'spoonacular'))
    parser.add_argument('--count', type=int, default='1', help='number of requests')
    parser.add_argument('--request-delay', type=int, default='5', help='sleep between each request')
    args = parser.parse_args()
    peeler = SpoonacularPeeler(args.api_key, args.storage)
    if args.reconvert == 'yes':
        peeler.reconvert()
    else:
        for _ in range(args.count):
            peeler.fetch_one()
            time.sleep(args.request_delay)


if __name__ == '__main__':
    main()
