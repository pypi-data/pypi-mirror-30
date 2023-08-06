from jutil.database import mysql_database_singleton, database_controller

from ScopusWp.extend import Config

from ScopusWp.scopus.config import DB_NAME

from sqlalchemy import Column, Integer, DATETIME, String

import datetime


class ScopusMySQLDatabase(mysql_database_singleton(
    Config.get_instance()['MYSQL']['username'],
    Config.get_instance()['MYSQL']['password'],
    Config.get_instance()['MYSQL']['host'],
    DB_NAME
)):
    pass


BASE = ScopusMySQLDatabase.get_base()


class BlackListing(BASE):

    __tablename__ = 'blacklist'

    scopusID = Column(Integer, primary_key=True)
    description = Column(String(200))
    created = Column(DATETIME)


class DatabaseController(database_controller(ScopusMySQLDatabase)):

    def __init__(self):
        super(self).__init__()

    def get_blacklist(self):
        return list(map(
            lambda black_listing: int(black_listing.scopusID),
            self._select_all(BlackListing)
        ))

    def add_blacklist(self, scopus_id, description=''):
        black_listing = BlackListing(
            scopusID=scopus_id,
            description=description,
            created=datetime.datetime.now()
        )
        self._add_blacklisting(black_listing)

    def _add_blacklisting(self, black_listing):
        self._add(
            BlackListing,
            black_listing,
            lambda x: BlackListing.scopusID == x.scopusID
        )
