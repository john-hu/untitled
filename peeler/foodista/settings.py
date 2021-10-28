# Scrapy settings for foodista project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# noinspection PyUnresolvedReferences
from ..utils.base_scrapy_settings import *
from . import version

SPIDER_MODULES = ['peeler.foodista.spiders']
NEWSPIDER_MODULE = 'peeler.foodista.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = f'RecipeSearchCrawler (version: {version})'

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'foodista.middlewares.FoodistaSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'foodista.middlewares.FoodistaDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'peeler.foodista.pipelines.RecipeURLPipeline': 300,
   'peeler.foodista.pipelines.RecipeResultPipeline': 300,
}
