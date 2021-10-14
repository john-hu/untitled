import argparse

from . import version
from .peeler import SpoonacularPeeler


def main():
    parser = argparse.ArgumentParser(f'Spoonacular API peeler, {version}')
    parser.add_argument('--api_key', type=str, required=True)
    parser.add_argument('--reconvert', type=str)
    parser.add_argument('--storage', type=str, default='peeler_output/spoonacular')
    args = parser.parse_args()
    peeler = SpoonacularPeeler(args.api_key, args.storage)
    if args.reconvert == 'yes':
        peeler.reconvert()
    else:
        peeler.fetch_one()


if __name__ == '__main__':
    main()
