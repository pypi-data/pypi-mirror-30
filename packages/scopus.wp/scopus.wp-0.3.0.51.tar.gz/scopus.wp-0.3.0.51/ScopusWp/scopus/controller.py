from ScopusWp.scopus.data import ScopusPublication, ScopusAuthor, ScopusAuthorObservation

from ScopusWp.scopus.observe import ScopusObservationController

from ScopusWp.scopus.persistency import ScopusDatabaseController
from ScopusWp.scopus.persistency import ScopusDatabaseController

from ScopusWp.scopus.scopus import ScopusController

from ScopusWp.config import PATH
from ScopusWp.extend import DataSource

from ScopusWp.scopus.config import NAME

from memory_profiler import profile

import logging
import threading
import time
import queue


# TODO: Implement massive logging


# TODO: Make a controller for temp Persistency
# Todo: Make the new methods use the get methods that also cache

# todo: Make new cache based on database cuz faster
# todo: Logging mal richtig angehen


class ScopusWorker(threading.Thread):

    def __init__(self, publication_queue, caching=True):
        threading.Thread.__init__(self)
        self.scopus_controller = ScopusController()
        self.database_controller = ScopusDatabaseController()

        self.caching = caching
        self.logger = logging.getLogger(NAME)

        self.queue = publication_queue  # type: queue.Queue
        self.id = None
        self.publication = None
        self.active = False

    def assign_publication(self, scopus_id):
        self.active = True
        self.id = scopus_id

    def run(self):
        while True:
            if self.id is not None:
                try:
                    self.publication = self.get_publication(self.id)
                    self.queue.put(self.publication, timeout=30)
                except TimeoutError:
                    print('que put timed out')
                except Exception as e:
                    print(e)
                finally:
                    self.active = False
                    self.id = None
            else:
                time.sleep(0.1)

    def get_publication(self, scopus_id):
        publication = self.scopus_controller.get_publication(scopus_id)
        return publication


class ScopusWorkerPool:

    def __init__(self, worker_count=4):

        self.database_lock = threading.Lock()
        self.publication_queue = queue.Queue(1000)
        self.workers = []
        for i in range(worker_count):
            worker = ScopusWorker(self.publication_queue)
            self.workers.append(worker)
            worker.start()
        self.ids = []

    def assign_publications(self, id_list):
        self.ids = id_list

    def fetch(self):
        while not (len(self.ids) == 0 and self.publication_queue.empty()):
            inactive_workers = list(filter(lambda x: not x.active, self.workers))
            for worker in inactive_workers:
                if len(self.ids) != 0:
                    scopus_id = self.ids.pop()
                    worker.assign_publication(scopus_id)
            if not self.publication_queue.empty():
                try:
                    yield self.publication_queue.get(timeout=30)
                except TimeoutError:
                    print('que get timed out')
            #time.sleep(0.01)


class ScopusTopController(DataSource):

    def __init__(self, controller):
        DataSource.__init__(self, controller)

        self.observation_controller = ScopusObservationController()
        self.scopus_controller = ScopusController()
        self.database_controller = ScopusDatabaseController()

        self.scopus_pool = ScopusWorkerPool(12)

        self.author_profiles = []

        self.all_scopus_ids = []
        self.old_scopus_ids = [] # self.controller.register.select_origin_id('scopus')
        self.new_scopus_ids = []

        self.amount_publications = 0
        self.estimate_factor = 20

        self.logger = logging.getLogger(NAME)

    #####################
    # TOP LEVEL METHODS #
    #####################

    def estimate_remaining(self, publication_count, citation_count):
        self.estimate_factor = ((self.estimate_factor * publication_count) + citation_count) / (publication_count + 1)
        return self.estimate_factor * (self.amount_publications - publication_count)

    def load_author_profiles(self):
        # Getting all the author observations
        author_observations = self.observation_controller.all_observations()
        self.logger.info('[Top] {} scopus author observations loaded'.format(len(author_observations)))

        # fetching all the author profiles from the scopus website
        for author_observation in author_observations:  # type: ScopusAuthorObservation
            for author_id in author_observation.ids:
                try:
                    author_profile = self.get_author_profile(author_id, caching=True)
                    self.logger.info('[Top] Fetched author profile {}'.format(author_id))
                    self.author_profiles.append(author_profile)
                except ConnectionError:
                    self.logger.warning('[Web] Connection error with author'.format(author_id))
        self.logger.info('[Top] {} scopus author profiles fetched from scopus'.format(len(self.author_profiles)))

    def load_scopus_ids(self):
        # Getting all the relevant scopus ids from the author profiles
        for author_profile in self.author_profiles:
            self.all_scopus_ids += author_profile.publications
        self.logger.info('[Top] Total of {} relevant publications from author observations'.format(
            len(self.all_scopus_ids)
        ))

        # All the scopus ids, which are in the pub control register already
        self.old_scopus_ids = self.controller.register.select_origin_id('scopus')
        self.logger.info((
            '[Top] {} of those publications already in the pub control register'
        ).format(len(self.old_scopus_ids)))

        # The new scopus ids is the difference between all and the old ones
        self.new_scopus_ids = list(set(self.all_scopus_ids) - set(self.old_scopus_ids))
        self.amount_publications = len(self.new_scopus_ids)
        self.logger.info((
            '[Top] Fetching {} direct publications'
        ).format(len(self.new_scopus_ids)))

    def fetch_publications(self):
        # Getting fir the new scopus ids the publications
        publication_count = 0
        citation_count = 0
        for scopus_id in self.new_scopus_ids:
            estimate = self.estimate_remaining(publication_count, citation_count)
            publication_count += 1

            try:
                scopus_publication = self.scopus_controller.get_publication(scopus_id)
            except ConnectionError:
                continue
            except TimeoutError:
                continue
            citation_scopus_ids = list(map(lambda x: int(x), scopus_publication.citations))
            citation_scopus_ids = list(set(citation_scopus_ids) - set(self.old_scopus_ids))

            citation_count = 0
            # Getting as much citation publications from the cache as possible
            for citation_publication in self.from_cache(citation_scopus_ids):
                citation_count += 1
                # Removing the id from the list, so that it does not get fetched twice. Once from the cache
                # and once from the scopus website afterwards
                citation_scopus_ids.remove(citation_publication.id)
                self.logger.info((
                    '[Progress] Fetched {} from the cache. Estimate remaining citations: {}'
                ).format(citation_publication.id, estimate))
                yield citation_publication

            # Getting the rest from the scopus website, by using the worker pool for speed
            for citation_publication in self.from_scopus(citation_scopus_ids):
                citation_count += 1
                # Writing those publications into the local scopus cache, so that they can be fetched
                # faster the next time around
                if not self.database_controller.contains_publication(citation_publication):
                    self.database_controller.insert_publication(citation_publication)
                self.logger.info((
                    '[Progress] Fetched {} from scopus. Estimate remaining citations: {}'
                ).format(citation_publication.id, estimate))
                yield citation_publication

            self.logger.info((
                '[Progress] Fetched {} from scopus. Remaining direct publications {}'
            ).format(self.amount_publications - publication_count))
            yield scopus_publication

    def from_scopus(self, scopus_ids):
        self.scopus_pool.assign_publications(scopus_ids)
        for scopus_publication in self.scopus_pool.fetch():
            yield scopus_publication

    def from_cache(self, scopus_ids):
        for scopus_id in scopus_ids:
            if self.database_controller.contains_publication(scopus_id):
                yield self.database_controller.select_publication(scopus_id)

    @profile
    def fetch(self):

        self.load_author_profiles()
        self.load_scopus_ids()

        for publication in self.fetch_publications():
            yield self.to_publication_dict(publication)

    def to_publication_dict(self, scopus_publication):
        publication_dict = {
            'title': scopus_publication.title,
            'description': scopus_publication.description,
            'published': scopus_publication.date,
            'doi': scopus_publication.doi,
            'journal': scopus_publication.journal,
            'volume': scopus_publication.volume,
            'origin': {
                'name': self.name,
                'id': scopus_publication.id,
                'text': ''
            },
            'authors': list(map(
                lambda scopus_author: {
                    'id': scopus_author.id,
                    'first_name': scopus_author.first_name,
                    'last_name': scopus_author.last_name
                },
                scopus_publication.authors
            )),
            'citations': list(map(
                lambda scopus_id: {'id': scopus_id, 'name': self.name},
                scopus_publication.citations
            )),
            'links': [],
            'categories': self.observation_controller.get_publication_keywords(scopus_publication),
            'tags': scopus_publication.keywords
        }

        return publication_dict

    def get_publication(self, scopus_id, caching):
        if self.database_controller.contains_publication(scopus_id):
            if caching:
                publication = self.database_controller.select_publication(scopus_id)
            else:
                publication = self.scopus_controller.get_publication(scopus_id)
        else:
            publication = self.scopus_controller.get_publication(scopus_id)
            self.database_controller.insert_publication(publication)
        return publication

    @property
    def name(self):
        return 'scopus'

    def get_author_profile(self, author_id, caching=True):
        if self.database_controller.contains_author_profile(author_id):
            if caching:
                return self.database_controller.select_author_profile(author_id)
            else:
                return self.scopus_controller.get_author_profile(author_id)
        else:
            author_profile = self.scopus_controller.get_author_profile(author_id)
            self.database_controller.insert_author_profile(author_profile)
            return author_profile

    def explore_author_affiliations(self, author_dict):
        """
        Gets the list of all affiliation ids occurring in the history of all the publications to a author id of an
        author.

        Takes a dict, that assigns a list of possible author ids to a string tuple with last name and first name of
        an author
        Returns a dict with the string name tuple as keys and the values being dicts, that assigns list of affiliation
        ids to the author ids given in the input dict
        Example:
        IN: {('john', 'doe'): [1987623, 1294401]}
        OUT: {('john', 'doe'): {1987623: [8383992, 12387293],
                                1294401: [2312123]}
        :param author_dict: {('first name', 'last name') -> [author ids]}}
        :return: {('first name', 'last name') -> {author id -> [affiliation ids]}}
        """
        author_affiliation_dict = {}

        self.logger.info('loading temp storage for author aff.')

        # The naming function for the storage files
        def name_function(obj): return ''.join(list(obj.keys())[0])
        # Creating the temp storage list to save data persistently in case of crash
        temp_list = list('au_aff', PATH + '/temp', name_function)
        temp_list.load()

        # Loading the values, that were already saved in the temp list
        for temp_dict in temp_list:
            author_affiliation_dict.update(temp_dict)

        self.logger.info('requesting publications for affiliations')
        for name_tuple, author_id_list in author_dict.items():
            # Only really processing and requesting for a user, if that user is not already in the dict
            if name_tuple not in author_affiliation_dict.keys():
                # Getting the affiliation id list for each of the author ids and saving the list as the value to the key
                # being the author id
                affiliation_dict = {}
                for author_id in author_id_list:
                    affiliation_id_list = self.get_affiliations_author(author_id)
                    affiliation_dict[author_id] = affiliation_id_list
                # Adding the affiliation dict as the value to the name tuple key to the main dict
                temp_dict = {name_tuple: affiliation_dict}
                author_affiliation_dict.update(temp_dict)
                # Saving the temp dict, which represents the main entry for a single author
                temp_list.append(temp_dict)

        self.logger.info('finished exploring affiliations')
        return author_affiliation_dict




if __name__ == '__main__':
    controller = ScopusTopController()
    for a in controller.fetch():
        print(a)
