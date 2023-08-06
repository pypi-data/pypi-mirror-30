from jutil.database import mysql_database_singleton, database_controller

from ScopusWp.extend import Config

from ScopusWp.scopus.config import DB_NAME

from sqlalchemy import Column, Integer, DATETIME, String, Text, BigInteger

from ScopusWp.scopus.data import ScopusAuthorProfile

import datetime
import json


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

    scopusID = Column(BigInteger, primary_key=True)
    description = Column(String(200))
    created = Column(DATETIME)


class AuthorProfile(BASE):

    __tablename__ = 'profile'

    authorID = Column(BigInteger, primary_key=True)
    first_name = Column(String(500))
    last_name = Column(String(500))
    updated = Column(String(500))
    h_index = Column(String(100))
    document_count = Column(Integer)
    citation_count = Column(Integer)
    publications = Column(Text)

    def to_scopus_author_profile(self):
        scopus_author_profile = ScopusAuthorProfile(
            self.authorID,
            self.first_name,
            self.last_name,
            self.h_index,
            self.citation_count,
            self.document_count,
            json.loads(self.publications)
        )
        return scopus_author_profile

    @staticmethod
    def from_scopus_author_profile(scopus_author_profile):
        author_profile = AuthorProfile(
            authorID=scopus_author_profile.id,
            first_name=scopus_author_profile.first_name,
            last_name=scopus_author_profile.last_name,
            updated=datetime.datetime.now(),
            h_index=scopus_author_profile.h_index,
            document_count=scopus_author_profile.document_count,
            citation_count=scopus_author_profile.citation_count,
            publications=json.dumps(scopus_author_profile.publications)
        )
        return author_profile


class DatabaseController(database_controller(ScopusMySQLDatabase)):

    def __init__(self):
        super().__init__()

    def get_blacklist(self):
        return list(map(
            lambda black_listing: int(black_listing.scopusID),
            self._select_all(BlackListing)
        ))

    def contains_profile(self, author_id):
        return list(self.session.query(AuthorProfile).filter(AuthorProfile.authorID == author_id)) != 0

    def get_profile(self, author_id):
        return self.session.query(AuthorProfile).get(author_id).to_scopus_author_profile()

    def add_profile(self, scopus_author_profile):
        author_profile = AuthorProfile.from_scopus_author_profile(scopus_author_profile)
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
