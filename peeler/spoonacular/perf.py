import os
import sqlite3
from enum import Enum, auto


class PerfType(Enum):
    FETCH = auto()
    FETCH_ERROR = auto()
    PARSE = auto()
    PARSE_ERROR = auto()
    SUCCESSFUL = auto()


SQL_STATEMENTS = {
    'DAILY_PERF': {
        'CREATE': '''
            CREATE TABLE IF NOT EXISTS DAILY_PERF (
                date_str text PRIMARY KEY,
                fetch_count integer DEFAULT 0,
                fetch_error integer DEFAULT 0,
                parse_count integer DEFAULT 0,
                parse_error integer DEFAULT 0,
                duplicated_count integer DEFAULT 0,
                success_count integer DEFAULT 0
            );
        ''',
        'UPSERT': lambda field: f'''
            INSERT INTO DAILY_PERF(date_str, {field}) VALUES(:date_str, 1) ON CONFLICT(date_str)
                DO UPDATE SET {field} = {field} + 1 WHERE date_str = :date_str;
        '''
    },
    'FETCHED_ID': {
        'CREATE': '''
            CREATE TABLE IF NOT EXISTS FETCHED (
                id text PRIMARY KEY,
                duplicated_count integer DEFAULT 0
            );
        ''',
        'EXIST': 'SELECT id FROM FETCHED WHERE id = :id',
        'UPSERT': '''
            INSERT INTO FETCHED(id) VALUES(:id) ON CONFLICT(id)
                DO UPDATE SET duplicated_count = duplicated_count + 1 WHERE id = :id;
        '''
    }
}


class PerfInspector:
    def __init__(self, storage):
        self.__db = sqlite3.connect(os.path.join(storage, 'perf.db'))
        self.__check_structure()

    def __del__(self):
        self.__db.close()

    def __check_structure(self) -> None:
        cursor = self.__db.cursor()
        try:
            cursor.execute('SELECT count(*) FROM DAILY_PERF')
            cursor.execute('SELECT count(*) FROM FETCHED')
        except sqlite3.OperationalError:
            cursor.execute(SQL_STATEMENTS['DAILY_PERF']['CREATE'])
            cursor.execute(SQL_STATEMENTS['FETCHED_ID']['CREATE'])
        self.__db.commit()
        cursor.close()

    def log(self, perf_type: PerfType, date_str: str,
            data_id: str = None) -> None:
        cursor = self.__db.cursor()
        daily_pref_upsert = SQL_STATEMENTS['DAILY_PERF']['UPSERT']
        fetched_cache = SQL_STATEMENTS['FETCHED_ID']['UPSERT']
        exist_check = SQL_STATEMENTS['FETCHED_ID']['EXIST']
        if perf_type == PerfType.FETCH:
            cursor.execute(
                daily_pref_upsert('fetch_count'), {
                    'date_str': date_str})
        elif perf_type == PerfType.FETCH_ERROR:
            cursor.execute(
                daily_pref_upsert('fetch_error'), {
                    'date_str': date_str})
        elif perf_type == PerfType.PARSE:
            cursor.execute(
                daily_pref_upsert('parse_count'), {
                    'date_str': date_str})
        elif perf_type == PerfType.PARSE_ERROR:
            cursor.execute(
                daily_pref_upsert('parse_error'), {
                    'date_str': date_str})
        elif perf_type == PerfType.SUCCESSFUL:
            # try to query the cache row
            cursor.execute(exist_check, {'id': data_id})
            if cursor.fetchone():
                # an existing row means duplication.
                cursor.execute(
                    daily_pref_upsert('duplicated_count'), {
                        'date_str': date_str})
            # record rest.
            cursor.execute(
                daily_pref_upsert('success_count'), {
                    'date_str': date_str})
            cursor.execute(fetched_cache, {'id': data_id})
        self.__db.commit()
        cursor.close()
