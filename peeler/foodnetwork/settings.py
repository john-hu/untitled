# Scrapy settings for foodnetwork project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# noinspection PyUnresolvedReferences
from ..scrapy_utils.base_scrapy_settings import *

SPIDER_MODULES = ['peeler.foodnetwork.spiders']
NEWSPIDER_MODULE = 'peeler.foodnetwork.spiders'


ROBOTSTXT_OBEY = False

# We have to use a fake user agent because we have to disable the
# robots.txt rules from uk-api.loma-cms.com
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.50'

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'foodnetwork.middlewares.FoodistaSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'foodnetwork.middlewares.FoodistaDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy_utils.extensions.telnet.TelnetConsole': None,
# }
