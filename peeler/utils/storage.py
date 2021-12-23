import logging
import os
import sqlite3
from enum import Enum
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class ParseState(Enum):
    NEW = 0
    PARSING = 1
    PARSED = 2
    WRONG_DATA = 3


class Storage:
    def __init__(self, storage):
        self.__storage = storage
        # the sqlite3 may be shared among two processes. We should close it asap.
        self.__db_file = os.path.join(self.__storage, 'recipes.db')
        self.__ensure_db()

    def __ensure_db(self) -> None:
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
        logger.info('Recipe database inited')

    def add_recipe_url(self, url: str) -> None:
        conn = sqlite3.connect(self.__db_file)
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO RECIPES_LIST(url) VALUES(:url);', {'url': url})
        cursor.close()
        conn.commit()
        conn.close()

    def has_recipe_url(self, url: str) -> bool:
        conn = sqlite3.connect(self.__db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT COUNT(*) FROM RECIPES_LIST WHERE url = :url;', {'url': url})
            return cursor.fetchone()[0]
        finally:
            cursor.close()
            conn.close()

    def lock_recipe_urls(self, count: int) -> List[str]:
        conn = sqlite3.connect(self.__db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT url FROM RECIPES_LIST WHERE parse_state = 0 LIMIT :count', {'count': count})
            all_urls = cursor.fetchall()
            cursor.executemany('UPDATE RECIPES_LIST SET parse_state = 1 WHERE url = ?', all_urls)
            conn.commit()
            return [url[0] for url in all_urls]
        finally:
            cursor.close()
            conn.close()

    def unlock_recipe_url(self, url: str) -> None:
        conn = sqlite3.connect(self.__db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE RECIPES_LIST SET parse_state = 0 WHERE parse_state = 1 AND url = :url', {'url': url})
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def mark_finished(self, url: str) -> None:
        self.mark_as(url, ParseState.PARSED)

    def mark_as(self, url: str, state: ParseState) -> None:
        if state not in [ParseState.PARSED, ParseState.WRONG_DATA]:
            return
        conn = sqlite3.connect(self.__db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE RECIPES_LIST SET parse_state = :state WHERE parse_state = 1 AND url = :url',
                           {'url': url, 'state': state.value})
            conn.commit()
        finally:
            cursor.close()
            conn.close()
