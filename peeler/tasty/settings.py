# Scrapy settings for tasty project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# noinspection PyUnresolvedReferences
from ..scrapy_utils.base_scrapy_settings import *
from . import version

SPIDER_MODULES = ['peeler.tasty.spiders']
NEWSPIDER_MODULE = 'peeler.tasty.spiders'


ROBOTSTXT_OBEY = True

# We have to use a fake user agent because we have to disable the robots.txt rules from uk-api.loma-cms.com
USER_AGENT = f'RecipeSearchCrawler (version: {version})'

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'tasty.middlewares.FoodistaSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'tasty.middlewares.FoodistaDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy_utils.extensions.telnet.TelnetConsole': None,
#}
