# Scrapy settings for allrecipes project
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

SPIDER_MODULES = ['peeler.allrecipes.spiders']
NEWSPIDER_MODULE = 'peeler.allrecipes.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = f'RecipeSearchCrawler (version: {version})'

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'allrecipes.middlewares.AllrecipesSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'allrecipes.middlewares.AllrecipesDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy_utils.extensions.telnet.TelnetConsole': None,
#}
