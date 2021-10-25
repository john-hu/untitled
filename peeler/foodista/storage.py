import logging
import os
import sqlite3
from enum import Enum


logger = logging.getLogger(__name__)


class ParseState(Enum):
    NEW = 0
    PARSING = 1
    PARSED = 2


class Storage:
    def __init__(self, storage):
        logger.info(f'Open database at {storage}')
        self.__conn = sqlite3.connect(os.path.join(storage, 'recipes.db'))
        self.__ensure_db()

    def __del__(self):
        if self.__conn:
            self.__conn.close()

    def __ensure_db(self):
        cursor = self.__conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS RECIPES_LIST (
                url text PRIMARY KEY,
                parse_state integer DEFAULT 0
            );
        ''')
        cursor.close()
        self.__conn.commit()

    def add_recipe_url(self, url):
        cursor = self.__conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO RECIPES_LIST(url) VALUES(:url);', {'url': url})
        cursor.close()
        self.__conn.commit()
