import scrapy
import requests
from bs4 import BeautifulSoup


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


class RecipesSpider(scrapy.Spider):
    name = "recipes"
    start_urls = parse_sitemap()

    def parse(self, response):
        yield {
            "title": response.css('h1::text').get(),
            "ingredients": response.css('.ingredients-item-name::text').get()
        }

