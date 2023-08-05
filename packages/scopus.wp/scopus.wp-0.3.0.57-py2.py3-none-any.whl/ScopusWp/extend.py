import logging
import pathlib
import configparser
import sys
import getopt
import jinja2
import os

from ScopusWp.database import MySQLDatabase

from ScopusWp.config import PATH

from jutil.installation import PathLookupPrompt
from jutil.installation import create_database_mysql, create_sqlalchemy_mysql

from sqlalchemy.orm import sessionmaker, Session


class ExtensionInstallationController:
    """
    DEV
    -> One could add support for creating additional sqlite databases, but if that is the case the main class would be
    too overloaded and one would have to make a separate class to handle the databases
    """
    OPTIONS_FORMAT_SHORT = 'p:'
    OPTIONS_FORMAT_LONG = ['project_path=']

    def __init__(self, extension_name):
        self.name = extension_name
        self.options, self.arguments = getopt.getopt(sys.argv[1:], self.OPTIONS_FORMAT_SHORT, self.OPTIONS_FORMAT_LONG)
        self.project_path = self.get_project_path()

        self.path = pathlib.Path(self.project_path) / extension_name
        # Creating the folder, if it does not already exists
        self._create_extension_folder()

        self.explorer = PubControlExplorer(self.project_path)

        self._engine = None
        self._session_maker = None

        self._session = None

    @property
    def session(self):
        if self._session_maker is None:
            raise AttributeError('No database has been created yet')
        if self._session is None:
            self._session = self._session_maker()
        return self._session

    def create_file(self, name, content):
        """
        Creates a new file in the local folder of the extension inside of the project root and writes the given content
        into it.
        :param name: The name of the file
        :param content: The content to be written into the file
        :return: void
        """
        file_path = self.path / name
        if not file_path.exists():
            with file_path.open(mode='w+') as file:
                file.write(content)
                file.flush()

    def load_template(self, path):
        """
        If given the path to a jinja2 template file, this method will load the files contents into a jinja template
        and returns this template object.
        :param path: The string path to the template file
        :return: jinja2.Template
        """
        template_path = pathlib.Path(path)
        with template_path.open() as file:
            return jinja2.Template(file.read())

    def create_mysql_database(self, name, declarative):
        """
        Given the name of the database and the sqlalchemy declarative base this method will create all the tables
        according to sqlalchemy models. If there is no database with the given name yet a new one will be created
        IMPORTANT
        Make sure, that the module, which contains all the actual model classes for sqlalchemy has been imported or is
        in the scope, when this method is being called, otherwise it will not work
        :param name: The name of the database, that is supposed to be used for the sqlalchemy tables
        :param declarative: The declarative base object of sqlalchemy, that was used to create all the model classes
        :return:
        """
        # Attempting to create the database
        try:
            create_database_mysql(
                self.explorer.mysql_username,
                self.explorer.mysql_password,
                self.explorer.mysql_host,
                name,
            )
        except Exception as e:
            print("{} {}".format(type(e), str(e)))
        # Creating the tables for the sqlalchemy models
        try:
            self._engine = create_sqlalchemy_mysql(
                self.explorer.mysql_username,
                self.explorer.mysql_password,
                self.explorer.mysql_host,
                name,
                declarative
            )
            self._session_maker = sessionmaker(bind=self._engine)
        except Exception as e:
            print("{} {}".format(type(e), str(e)))

    def get_project_path(self):
        """
        Attempts to get the project path from the command line options called with the script. In case the project
        path of PubControl was not given through the command line, prompts the user to input the path manually, as the
        path is absolutely necessary for the installation to work.
        :return: string path
        """
        if len(sys.argv[1:]) != 0:
            # Checking the options passed to the script, if it contains the path option returning that for te path
            for opt, arg in self.options:
                if opt in ['-p', '--project_path']:
                    return arg

        # In case there was no path in the command line call, prompts the user to manually input the path
        prompt = PathLookupPrompt()
        return prompt.get()

    def _create_extension_folder(self):
        """
        Every extension for PubControl gets its own folder in the PubControl project root and there it can install all
        configuration/output files w/e the user has to interact with in some way eventually.
        This function creates a new such folder, if it does not already exists.
        :raises NotADirectoryError: When the path to the extension folder already exists, but is not a folder
        :return: void
        """
        # Checking if the folder already exists, if it already exists, does not create the folder
        if self.path.exists():
            # If the path exists, but is not a folder, but a file or something else, that is a problem and a error
            if not self.path.is_dir():
                raise NotADirectoryError((
                    'The extension "{}" to PUBCONTROL could not be installed. '
                    'path to extension root already exists, but is not a folder'
                ).format(self.name))
        else:
            # Creating the folder
            self.path.mkdir()


class PubControlExplorer:

    def __init__(self, project_path):
        self.path_string = project_path
        self.path = pathlib.Path(project_path)

        # Will contain the configparser.ConfigParser object after the project folder has been read
        self.config = None

        # This is the session object for the sqlalchemy mysql database of the pub control project, this database
        # contains all the publications
        self.session = MySQLDatabase.get_session()

        self.check_path()
        # Actually reading the config file into the variable
        self.read_config_file()

    def read_config_file(self):
        """
        Creates a new config parser object and reads the contents of the config.ini in the project folder to it.
        :return: void
        """
        config_file_path = str(self.path / "config.ini")

        self.config = configparser.ConfigParser()
        self.config.read(config_file_path)

    @property
    def mysql_username(self):
        """
        The string username for the mysql database
        :return: string
        """
        return self.config['MYSQL']['username']

    @property
    def mysql_password(self):
        """
        The string password for mysql database and the given user
        :return: string
        """
        return self.config['MYSQL']['password']

    @property
    def mysql_host(self):
        """
        The string, specifying the host argument for the mysql database
        :return: string
        """
        return self.config['MYSQL']['host']

    def check_path(self):
        """
        Checks whether the path given exists and if it is a folder. In case it is not raises an error

        :raises EnvironmentError: In case the given project path is not correct
        :return: void
        """
        if not(self.path.exists() and self.path.is_dir()):
            raise EnvironmentError('The given PubControl Project path is not correct')


class DataSource:

    def __init__(self, controller):
        self.controller = controller
        self.logger = logging.getLogger('source-{}'.format(self.name))

    def fetch(self):
        raise NotImplementedError()

    @property
    def name(self):
        raise NotImplementedError()


class DataSink:

    def __init__(self, controller):
        self.controller = controller
        self.logger = logging.getLogger('sink-{}'.format(self.name))

    @property
    def run(self):
        raise NotImplementedError()

    @property
    def register(self):
        return self.controller.register

    @property
    def config(self):
        return self.controller.config

    @property
    def name(self):
        raise NotImplementedError()
