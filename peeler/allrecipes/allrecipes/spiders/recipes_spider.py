import re
import scrapy_utils
import requests
from bs4 import BeautifulSoup
import unicodedata

BASE_URL = 'https://www.allrecipes.com/sitemap'


def parse_sitemap():
    r = requests.get(f'{BASE_URL}.xml')
    sp = BeautifulSoup(r.text, 'lxml')
    links = sp.find_all('loc')
    recipes = []
    for link in links:
        if link.text.split('/')[-3] == 'recipe':
            print(link.text)
            r1 = requests.get(link.text)
            sp1 = BeautifulSoup(r1.text, 'lxml')
            recipe_links = sp1.find_all('loc')
            for recipe_link in recipe_links:
                recipes.append(recipe_link.text)
    return recipes


def regex(rule, response):
    if isinstance(response, str):
        m = re.search(rule, response)
        if m:
            return m.group(0)
        else:
            return response
    return response


def convert_number(message):
    if message is None:
        return 0
    elif message == "":
        return 0
    else:
        try:
            return float(unicodedata.numeric(message))
        except TypeError:
            return int(message)


class RecipesSpider(scrapy_utils.Spider):
    name = "recipes"
    start_urls = parse_sitemap()

    @staticmethod
    def retrieve_recipe_info(message):
        path = f"//div[@class='recipe-meta-item-header'][contains(text(), '{message}')]/following-sibling::div[1]/text()"
        return path

    @staticmethod
    def retrieve_ingredient_info(response):
        info_aggs = []
        for ingredient_info in response.css('.ingredients-item'):
            info_agg = {
                "name": ingredient_info.css('.checkbox-list-input').xpath('@data-ingredient').get(),
                "size": {
                    "number": convert_number(
                        ingredient_info.css('.checkbox-list-input').xpath('@data-quantity').get()),
                    "unit": ingredient_info.css('.checkbox-list-input').xpath('@data-unit').get()
                }
            }
            info_aggs.append(info_agg)
        return info_aggs

    @staticmethod
    def retrieve_step_info(response):
        info_aggs = []
        for step_info in response.css('.subcontainer.instructions-section-item'):
            info_agg = {
                "id": regex(r'\d', step_info.css('.checkbox-list-text::text').get()),
                "equipments": [],
                "language": response.css('html').xpath('@lang').get(),
                "text": step_info.css('p::text').get()
            }
            info_aggs.append(info_agg)
        return info_aggs

    def parse(self, response):
        data = {"authors": ["John Hu", "Francis Zhuang"],
                "categories": response.css('.breadcrumbs__title::text')[2].get(), "cookTime": convert_number(
                regex(r'\d+', response.xpath(self.retrieve_recipe_info("cook:")).extract_first())),
                "description": response.xpath("//meta[@name='description']/@content").extract_first(),
                "language": response.css('html').xpath('@lang').get(),
                "keywords": [response.xpath("//h1/text()").get()],
                "id": response.xpath("//link[@rel='canonical']/@href").extract_first(),
                "mainLink": response.xpath("//link[@rel='canonical']/@href").extract_first(),
                "images": [response.css('.recipe-review-image-wrapper noscript img').xpath('@src').get(0)],
                "sourceSite": response.xpath("//meta[@property='og:site_name']/@content").extract_first(),
                "title": response.xpath("//h1/text()").get(), "servingSize": {
                "number": convert_number(
                    regex(r'\d+', response.xpath(self.retrieve_recipe_info("Servings:")).extract_first())
                ),
                "unit": "people"
            }, "ingredients": self.retrieve_ingredient_info(response),
                "instructions": self.retrieve_step_info(response)}
        yield data
