from jutil.database import mysql_database_singleton, database_controller

from ScopusWp.extend import Config

from ScopusWp.scopus.config import DB_NAME

from sqlalchemy import Column, Integer, DATETIME, String, Text

from ScopusWp.scopus.data import ScopusAuthorProfile

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


class AuthorProfile(BASE):

    __tablename__ = 'profile'

    authorID = Column(Integer, primary_key=True)
    first_name = Column(String(500))
    last_name = Column(String(500))
    updated = Column(String(500))
    publications = Column(Text)


class DatabaseController(database_controller(ScopusMySQLDatabase)):

    def __init__(self):
        super().__init__()

    def get_blacklist(self):
        return list(map(
            lambda black_listing: int(black_listing.scopusID),
            self._select_all(BlackListing)
        ))

    def contains_profile(self, author_id):
        return len(self.session.query(AuthorProfile).get(author_id)) != 0

    def get_profile(self, author_id):
        return self.session.query(AuthorProfile).get(author_id).first()

    def add_profile(self, scopus_author_profile):
        author_profile = AuthorProfile(
            authorID=scopus_author_profile.id,
            first_name=scopus_author_profile.first_name,
            last_name=scopus_author_profile.last_name,
            updated=datetime.datetime.now()
        )
        self._add_author_profile(author_profile)

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

    def _add_author_profile(self, author_profile):
        self._add(
            AuthorProfile,
            author_profile,
            lambda x: AuthorProfile.authorID == x.authorID
        )
