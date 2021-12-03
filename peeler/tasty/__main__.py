import argparse
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from . import version


def main():
    parser = argparse.ArgumentParser(f'Tasty Website peeler, {version}')
    parser.add_argument(
        '--storage',
        type=str,
        default=os.path.join(
            'peeler_output',
            'tasty'))
    parser.add_argument(
        '--count',
        type=int,
        default=2,
        help='number of requests')
    parser.add_argument('--log-file', type=str, help='the log output file')
    parser.add_argument(
        'mode',
        type=str,
        default='list',
        choices=[
            'list',
            'result'])
    args = parser.parse_args()

    os.environ['SCRAPY_SETTINGS_MODULE'] = 'peeler.tasty.settings'
    scrapy_settings = get_project_settings()
    scrapy_settings['storage'] = args.storage
    scrapy_settings['peel_count'] = args.count
    if args.log_file:
        scrapy_settings['LOG_FILE'] = args.log_file
    os.makedirs(args.storage, exist_ok=True)
    process = CrawlerProcess(scrapy_settings)
    process.crawl('recipe_list' if args.mode ==
                  'list' else 'recipe_result', domain='tasty.co')
    process.start()


if __name__ == '__main__':
    main()
