from ScopusWp.config import PATH, PROJECT_PATH

from ScopusWp.scopus.data import ScopusAuthorObservation

import os
import json
import configparser

#############
#  CLASSES  #
#############


class AuthorObservationInterface:

    def get_observation(self, author):
        raise NotImplementedError()

    def contains_author(self, author):
        raise NotImplementedError()

    def values(self):
        raise NotImplementedError()

    def keys(self):
        raise NotImplementedError()

    def __getitem__(self, item):
        raise NotImplementedError()

    def __contains__(self, item):
        raise NotImplementedError()

###############
# Controllers #
###############


class ScopusObservationController:

    def __init__(self):

        self.author_observation_model = AuthorObservationModel()

    def get_author_keywords(self, author):
        author_observation = self.author_observation_model[int(author)]  # type: ScopusAuthorObservation
        return author_observation.keywords

    def all_observations(self):
        return self.author_observation_model.values()

    def all_observed_ids(self):
        return self.author_observation_model.keys()

    def get_publication_keywords(self, publication):
        keywords = []
        author_observation_id_set = set(map(lambda x: int(x), self.author_observation_model.keys()))
        publication_author_id_set = set(map(lambda x: int(x), publication.authors))

        publication_observed_authors = list(publication_author_id_set.intersection(author_observation_id_set))
        # Going through all the authors of the publication and adding all the keywords of each observed author found
        for author in publication_observed_authors:
            author_keywords = self.get_author_keywords(author)
            difference = list(set(author_keywords) - set(keywords))
            keywords += difference
        return keywords

    def supports_publication(self, publication):
        """
        Returns the boolean value if the passed ScopusPublication is supported by the observation system, which means
        that at least one of its authors at the time of writing the publication had a affiliation, that is 7
        specifically whitelisted in the authors.ini configuration file for the observation.

        :param publication: ScopusPublication object to be checked
        :return: bool
        """
        for author in publication.authors:
            author_id = int(author)
            if author_id in self.author_observation_model.keys():
                author_observation = self.author_observation_model[author_id]  # type: ScopusAuthorObservation
                is_whitelist = author_observation.whitelist_contains_any(author.affiliations)
                # If the publication setting with author and affiliation is in at least one whitelist true can be
                # returned
                if is_whitelist:
                    return True

        # There is no instant False return for blacklist, because a potential whitelist entry of another author has
        # more priority, than a blacklist entry.
        # False is only returned in case True was not already returned due to a whitelisting
        return False

    def filter(self, publication_list):
        whitelist_publications = []
        blacklist_publications = []
        remaining_publications = []

        for publication in publication_list:
            _is_blacklist = False
            _is_whitelist = False
            # Checking the affiliations for all the authors
            for author in publication.authors:
                author_id = int(author.id)
                if author_id in self.author_observation_model.keys():
                    author_observation = self.author_observation_model[author_id] # type: ScopusAuthorObservation
                    _is_whitelist = author_observation.whitelist_contains_any(author.affiliations)
                    # If there was a blacklist found it would be overwritten with the next author, like this a TRUE
                    # will be preserved until the end of the loop
                    if not _is_blacklist:
                        _is_blacklist = author_observation.blacklist_contains_any(author.affiliations)

                    # In the case of whitelist, the publication will be added instantly, but for blacklist it is
                    # decided after all authors have been iterated
                    if _is_whitelist:
                        whitelist_publications.append(publication)
                        break

            if _is_blacklist:
                blacklist_publications.append(publication)
            else:
                remaining_publications.append(publication)

        return whitelist_publications, blacklist_publications, remaining_publications



############
#  Models  #
############


class AuthorObservationModel:

    def __init__(self):
        self.path_string = PROJECT_PATH + '/scopus/authors.ini'
        self.config = configparser.ConfigParser()
        self.config.read(self.path_string)

        self.dict, self.author_observations = self.load()

    def __contains__(self, item):
        self.contains_author(item)

    def __getitem__(self, item):
        return self.get_observation(item)

    def get_observation(self, author):
        return self.dict[int(author)]

    def contains_author(self, author):

        return int(author) in self.keys()

    def keys(self):
        return list(self.dict.keys())

    def values(self):
        return self.author_observations

    def load(self):
        content_dict = {}
        author_observation_list = []
        for section in self.config.keys():
            if section == 'DEFAULT':
                continue

            sub_dict = dict(self.config[section])

            # Getting the author observation
            author_observation = self._get_author_observation(sub_dict)
            author_observation_list.append(author_observation)
            # Adding a reference to the same author observation to all the author ids in the list
            for author_id in author_observation.ids:
                content_dict[int(author_id)] = author_observation

        return content_dict, author_observation_list

    @staticmethod
    def _get_author_observation(sub_dict):

        scopus_ids_json_string = sub_dict['ids']
        scopus_ids = json.loads(scopus_ids_json_string)

        keywords_json_string = sub_dict['keywords']
        keywords = json.loads(keywords_json_string)

        whitelist_json_string = sub_dict['scopus_whitelist']
        whitelist = json.loads(whitelist_json_string)

        blacklist_json_string = sub_dict['scopus_blacklist']
        blacklist = json.loads(blacklist_json_string)

        author_observation = ScopusAuthorObservation(
            scopus_ids,
            sub_dict['first_name'],
            sub_dict['last_name'],
            keywords,
            whitelist,
            blacklist
        )

        return author_observation
