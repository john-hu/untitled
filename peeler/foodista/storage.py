import json
import logging
import os
import sqlite3
from enum import Enum
from pathlib import Path


logger = logging.getLogger(__name__)


class ParseState(Enum):
    NEW = 0
    PARSING = 1
    PARSED = 2


class Storage:
    def __init__(self, storage):
        self.__storage = storage
        # the sqlite3 may be shared among two processes. We should close it asap.
        self.__db_file = os.path.join(self.__storage, 'recipes.db')
        logger.info(f'Open database at {self.__db_file}')
        self.__ensure_db()

    def __ensure_db(self):
        flag_file = os.path.join(self.__storage, 'db_inited.flag')
        if os.path.exists(flag_file):
            return
        conn = sqlite3.connect(self.__db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS RECIPES_LIST (
                url text PRIMARY KEY,
                parse_state integer DEFAULT 0
            );
        ''')
        Path(flag_file).touch()
        cursor.close()
        conn.commit()
        conn.close()
        logger.info(f'Recipe database inited')

    def add_recipe_url(self, url):
        conn = sqlite3.connect(self.__db_file)
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO RECIPES_LIST(url) VALUES(:url);', {'url': url})
        cursor.close()
        conn.commit()
        conn.close()
