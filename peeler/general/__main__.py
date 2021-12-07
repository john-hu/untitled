import argparse
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from . import version


def main():
    parser = argparse.ArgumentParser(f'General peeler, {version}')
    parser.add_argument('--storage', type=str, required=True)
    parser.add_argument('--count', type=int, default=2, help='number of requests')
    parser.add_argument('--log-file', type=str, help='the log output file')
    parser.add_argument('--init-url', type=str, help='the first url to build the url list')
    args = parser.parse_args()

    os.environ['SCRAPY_SETTINGS_MODULE'] = 'peeler.general.settings'
    scrapy_settings = get_project_settings()
    scrapy_settings['storage'] = args.storage
    scrapy_settings['peel_count'] = args.count
    scrapy_settings['init_url'] = args.init_url
    if args.log_file:
        scrapy_settings['LOG_FILE'] = args.log_file
    os.makedirs(args.storage, exist_ok=True)
    process = CrawlerProcess(scrapy_settings)
    process.crawl('general_result')
    process.start()


if __name__ == '__main__':
    main()
