# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime
from ..utils.files import append_to

from .items import RecipeItem, RecipeURLItem
from .storage import Storage


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

    def process_item(self, item: RecipeItem, _spider):
        if isinstance(item, RecipeItem):
            now_str = datetime.now().strftime('%Y%m%d%H')
            append_to(self.__storage, 'recipes', now_str, item.to_dict())
        return item
