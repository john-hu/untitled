# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import date
from itemadapter import ItemAdapter
from ..utils.files import append_to

from .storage import Storage


class RecipePipeline:
    def __init__(self, storage):
        self.__storage = Storage(storage)

    @classmethod
    def from_crawler(cls, crawler):
        storage = crawler.settings.get('storage', None)
        return cls(storage)

    def process_item(self, item, _spider):
        adapter = ItemAdapter(item)
        self.__storage.add_recipe_url(adapter['url'])
        return item


class RecipeResultPipeline:
    def __init__(self, storage):
        self.__storage = storage

    @classmethod
    def from_crawler(cls, crawler):
        storage = crawler.settings.get('storage', None)
        return cls(storage)

    def process_item(self, item, _spider):
        adapter = ItemAdapter(item)
        today_str = date.today().strftime('%Y%m%d')
        append_to(self.__storage, 'recipes', today_str, dict(adapter))
        return item
