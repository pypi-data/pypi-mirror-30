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

    def __init__(self, queue, database_controller, caching=True):
        threading.Thread.__init__(self)
        self.scopus_controller = ScopusController()
        self.database_controller = database_controller

        self.caching = caching
        self.logger = logging.getLogger(NAME)

        self.queue = queue  # type: queue.Queue
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
                    self.queue.put(self.publication)
                    self.database_controller.lock.release()
                except Exception as e:
                    pass
                finally:
                    self.active = False
                    self.id = None
            else:
                time.sleep(0.1)

    def get_publication(self, scopus_id):
        if self.database_controller.contains_publication(scopus_id):
            if self.caching:
                publication = self.database_controller.select_publication(scopus_id)
            else:
                publication = self.scopus_controller.get_publication(scopus_id)
        else:
            publication = self.scopus_controller.get_publication(scopus_id)
            self.database_controller.insert_publication(publication)
        return publication


class ScopusWorkerPool:

    def __init__(self, database_controller, worker_count=4):
        self.publication_queue = queue.Queue(1000)
        self.workers = []
        for i in range(worker_count):
            worker = ScopusWorker(self.publication_queue, database_controller)
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
                yield self.publication_queue.get()
            #time.sleep(0.01)


class ScopusTopController(DataSource):

    def __init__(self, controller):
        DataSource.__init__(self, controller)

        self.observation_controller = ScopusObservationController()
        self.scopus_controller = ScopusController()
        self.database_controller = ScopusDatabaseController()

        self.scopus_pool = ScopusWorkerPool(self.database_controller, 6)

        self.amount_publications = 0
        self.estimate_factor = 20

        self.logger = logging.getLogger(NAME)

    #####################
    # TOP LEVEL METHODS #
    #####################

    @profile
    def fetch(self):
        # Getting all the author observations
        author_observations = self.observation_controller.all_observations()
        self.logger.info('[Top] {} scopus author observations loaded'.format(len(author_observations)))

        author_profiles = self.get_author_profiles(author_observations)

        count = 0
        self.logger.info('[Progress] No information about the total amount of publications')
        self.logger.debug('[Top] Fetching citation publications...')
        for scopus_publication in self.get_author_publications(author_profiles):
            # If the publication is actually in the set of observed publications, getting all the citations
            # as publications first and returning them
            citation_count = 0
            self.scopus_pool.assign_publications(scopus_publication.citations)
            for citation_publication in self.scopus_pool.fetch():
                citation_publication.citations = []
                publication_dict = self.general_publication(citation_publication)
                publication_dict['origin']['text'] = 'citation'
                self.logger.info('[Progress] Fetched {}. Estimate CITATION publications {}'.format(
                    citation_publication.id,
                    self.estimate_factor * (self.amount_publications - count)
                ))
                citation_count += 1
                yield publication_dict
                continue
            yield self.general_publication(scopus_publication)
            count += 1

            self.estimate_factor = self.estimate_factor * (count / (count + 1)) + citation_count * (1 / (count + 1))

    @profile
    def get_author_profiles(self, author_observations):
        # fetching all the author profiles from the scopus website
        author_profiles = []
        for author_observation in author_observations:  # type: ScopusAuthorObservation
            for author_id in author_observation.ids:
                try:
                    author_profile = self.get_author_profile(author_id, caching=True)
                    self.logger.info('[Top] Fetched author profile {}'.format(author_id))
                    author_profiles.append(author_profile)
                except ConnectionError:
                    self.logger.warning('[Web] Connection error with author'.format(author_id))
        self.logger.info('[Top] {} scopus author profiles fetched from scopus'.format(len(author_profiles)))
        return author_profiles

    @profile
    def get_author_publications(self, author_profiles):
        self.amount_publications = sum(map(lambda x: len(x.publications), author_profiles))
        # Printing the total amount of publications to get from the authors
        count = 0
        for author_profile in author_profiles:

            for scopus_id in author_profile.publications:
                try:
                    scopus_publication = self.get_publication(scopus_id, True)
                except ConnectionError:
                    continue
                # Deciding whether to actually return it
                if self.observation_controller.supports_publication(scopus_publication):
                    self.logger.info((
                        '[Progress] Fetched {}. Remaining DIRECT publications: {} '
                    ).format(
                        scopus_publication.id,
                        self.amount_publications - count
                    ))
                    yield scopus_publication
                count += 1

    def general_publication(self, scopus_publication):
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
