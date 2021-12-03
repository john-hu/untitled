# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
from datetime import datetime

from ..utils.files import append_to
from ..utils.storage import Storage
from ..utils.uploader import Uploader

from .items import RecipeItem, RecipeURLItem

logger = logging.getLogger(__name__)


class RecipeURLPipeline:
    def __init__(self, storage):
        self.__storage = Storage(storage)

    @classmethod
    def from_crawler(cls, crawler):
        storage = crawler.settings.get('storage', None)
        return cls(storage)

    def process_item(self, item: RecipeURLItem, _spider):
        if isinstance(item, RecipeURLItem):
            self.__storage.add_recipe_url(item.url)
        return item


class RecipeResultPipeline:
    def __init__(self, storage):
        self.__storage = storage

    @classmethod
    def from_crawler(cls, crawler):
        storage = crawler.settings.get('storage', None)
        return cls(storage)

    def process_item(self, item: RecipeItem, spider):
        if isinstance(item, RecipeItem):
            now_str = datetime.now().strftime('%Y%m%d%H')
            append_to(self.__storage, 'recipes', now_str, item.to_dict())
            if spider.settings.get('AUTO_UPLOADER_ENABLED') \
                    and spider.settings.get('AUTO_UPLOADER_ENDPOINT') \
                    and spider.settings.get('AUTO_UPLOADER_USERNAME') \
                    and spider.settings.get('AUTO_UPLOADER_PASSWORD'):
                logger.info(f'upload item to {item.id} to silver plate')
                uploader = Uploader(spider.settings.get('AUTO_UPLOADER_ENDPOINT'),
                                    spider.settings.get(
                                        'AUTO_UPLOADER_USERNAME'),
                                    spider.settings.get('AUTO_UPLOADER_PASSWORD'))
                uploader.pull_and_merge(item.to_dict())
        return item
