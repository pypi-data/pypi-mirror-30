from ScopusWp.scopus.data import ScopusPublication, ScopusAuthor, ScopusAuthorObservation

from ScopusWp.scopus.observe import ScopusObservationController

from ScopusWp.scopus.persistency import ScopusDatabaseController
from ScopusWp.scopus.persistency import ScopusDatabaseController

from ScopusWp.scopus.scopus import ScopusController

from ScopusWp.config import PATH
from ScopusWp.extend import DataSource

from ScopusWp.scopus.config import NAME

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

    def __init__(self, queue, caching=True):
        threading.Thread.__init__(self)
        self.scopus_controller = ScopusController()
        self.database_controller = ScopusDatabaseController()

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
                except ConnectionError:
                    self.logger.warning('[Web] Connection Error for {}'.format(self.id))
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

    def __init__(self, worker_count=4):
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
        while len(self.ids) != 0:
            inactive_workers = list(filter(lambda x: not x.active, self.workers))
            for worker in inactive_workers:
                if len(self.ids) != 0:
                    worker.assign_publication(self.ids.pop())
            if self.publication_queue.qsize() != 0:
                yield self.publication_queue.get()


class ScopusTopController(DataSource):

    def __init__(self, controller):
        DataSource.__init__(self, controller)

        self.observation_controller = ScopusObservationController()
        self.scopus_controller = ScopusController()
        self.database_controller = ScopusDatabaseController()

        self.scopus_pool = ScopusWorkerPool(5)

        self.logger = logging.getLogger(NAME)

    #####################
    # TOP LEVEL METHODS #
    #####################

    def fetch(self):
        # Getting all the author observations
        author_observations = self.observation_controller.all_observations()
        self.logger.info('[Top] {} scopus author observations loaded'.format(len(author_observations)))

        # fetching all the author profiles from the scopus website
        author_profiles = []
        for author_observation in author_observations:  # type: ScopusAuthorObservation
            for author_id in author_observation.ids:
                author_profile = self.get_author_profile(author_id, caching=True)
                author_profiles.append(author_profile)
        self.logger.info('[Top] {} scopus author profiles fetched from scopus'.format(len(author_profiles)))

        # Printing the total amount of publications to get from the authors
        total = sum(map(lambda x: len(x.publications), author_profiles))
        self.logger.info('[Progress] total direct publications {}'.format(total))

        self.logger.debug('[Top] Fetching direct publications...')
        author_publications = []
        for author_profile in author_profiles:

            self.scopus_pool.assign_publications(author_profile.publications)

            for scopus_publication in self.scopus_pool.fetch():
                # Deciding whether to actually return it
                if self.observation_controller.supports_publication(scopus_publication):
                    author_publications.append(scopus_publication)
                    remaining = total - len(author_publications)
                    self.logger.info((
                        '[Progress] Fetched {} Remaining direct publications: {} '
                    ).format(
                        scopus_publication.id,
                        remaining,
                        0
                    ))

        count = 0
        total_citations = sum(map(lambda x: len(x.citations), author_publications))
        self.logger.info('[Progress] total citation publications: {}'.format(total_citations))
        self.logger.debug('[Top] Fetching citation publications...')
        for scopus_publication in author_publications:
            # If the publication is actually in the set of observed publications, getting all the citations
            # as publications first and returning them
            self.scopus_pool.assign_publications(scopus_publication.citations)
            for citation_publication in self.scopus_pool.fetch():
                citation_publication.citations = []
                publication_dict = self.general_publication(citation_publication)
                publication_dict['origin']['text'] = 'citation'
                self.logger.info('[Progress] Fetched {}. Remaining citation publications {}'.format(
                    citation_publication.id,
                    total_citations - count
                ))
                count += 1
                yield publication_dict
                continue
            yield self.general_publication(scopus_publication)

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
