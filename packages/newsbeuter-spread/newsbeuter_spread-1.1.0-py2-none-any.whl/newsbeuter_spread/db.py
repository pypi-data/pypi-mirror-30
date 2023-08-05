import os
import sqlite3
from os.path import expanduser, join

from newsbeuter_spread.item import Item


DATABASE_PATH = os.environ.get('NEWSBEUTER_CACHE_PATH', join(expanduser('~'), '.newsbeuter', 'cache.db'))
QUERY_UNREAD = """SELECT id, title, datetime(pubDate, 'unixepoch'), url, content, author
        FROM rss_item WHERE unread = 1 ORDER BY pubDate"""
QUERY_READ = "UPDATE rss_item SET unread = 0 WHERE id = '{}'"


class DB:
    def __init__(self):
        self.connection = sqlite3.connect(DATABASE_PATH)

    def execute(self, statement):
        cursor = self.connection.cursor()
        cursor.execute(statement)
        return cursor

    def get_unread(self):
        items = self.execute(QUERY_UNREAD).fetchall()
        for id, title, pub_date, url, content, author in items:
            yield Item(title=title, pub_date=pub_date, url=url, content=content, id=id, author=author)

    def mark_read(self, id):
        self.execute(QUERY_READ.format(id))
        self.connection.commit()
