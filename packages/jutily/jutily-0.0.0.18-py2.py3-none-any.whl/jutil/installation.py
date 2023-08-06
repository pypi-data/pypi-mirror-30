import MySQLdb
import pathlib
import jinja2
import os

from sqlalchemy import create_engine


def _create_database_connector_mysql(username, password, host):
    """
    Creates a new MySQLdb.connect() object, which is used to acquire cursors to the local mysql database server
    instance and these cursors can then be used to query SQL code to the database.
    :param username: The string username to be used for the authentication
    :param password: The string password for the given user
    :param host: The host of the mysql server.Usually the database is installed locally and therefore will be
        'localhost'
    :return: The MySQLdb.connect() object
    """
    connector = MySQLdb.connect(
        host=host,
        user=username,
        passwd=password
    )
    return connector


def create_database_mysql(username, password, host, name):
    """
    Creates a new database schema with the given name on the mysql server at the given host name, using the given
    login credentials to gain access.
    :param username: The string username of the user of the database
    :param password: The password to the given user
    :param host: The host name for the mysql server to connect to
    :param name: The name of the database to be created
    :return: void
    """
    # Getting a new connector object
    connector = _create_database_connector_mysql(username, password, host)
    # Getting a new cursor from that connector onject
    cursor = connector.cursor()
    # Executing a create database clause through that cursor
    sql = 'CREATE DATABASE {}; COMMIT;'.format(name)
    cursor.execute(sql)


def create_sqlalchemy_mysql(username, password, host, database, declarative):
    """
    If given the database name and the desclarative base used for the sqalchemy models this method will setup
    the database (has to exists already) with all the tables according to the sqlalchemy models
    :param module:
    :param database:
    :param declarative:
    :return: void
    """
    # Creating a mysql engine
    engine_string = 'mysql+mysqldb://{}:{}@{}/{}'.format(
        username,
        password,
        host,
        database
    )
    engine = create_engine(engine_string)
    # The sqlalachemy statement to actually create all the tables
    declarative.metadata.create_all(engine)

    return engine


def installation_database_singleton(username, password, host):

    class Db:

        _instance = None

        @staticmethod
        def create_database(name):
            try:
                cursor = Db.get_cursor()
                cursor.execute('CREATE DATABASE {}; COMMIT;'.format(name))
            except:
                print('COULD NOT CREATE DATABASE {}'.format(name))

        @staticmethod
        def get_cursor():
            conn = Db.get_instance()  # type: MySQLdb.Connection
            cursor = conn.cursor()
            return cursor

        @staticmethod
        def get_instance():
            if Db._instance is None:
                Db.new_instance()

            return Db._instance

        @staticmethod
        def new_instance():
            try:
                connector = MySQLdb.connect(
                    host=host,
                    user=username,
                    passwd=password
                )
                Db._instance = connector
                print('DATABASE CONNECTOR SUCCESSFULLY CREATED')
                return True
            except Exception as e:
                print('DURING THE ATTEMPT TO CREATE A DATABASE CONNECTION THE EXCEPTION OCCURRED\n"{}"'.format(str(e)))
                return False

        @staticmethod
        def test():
            return Db.new_instance()

    return Db


class SetupController:

    def run(self):
        raise NotImplementedError()


class FileSetupController(SetupController):

    def __init__(self, path, file_name, template_path, **kwargs):
        self.path = pathlib.Path(path) / file_name
        with open(template_path, mode='r') as file:
            self.template = jinja2.Template(file.read())
        self.content = self.template.render(**kwargs)

    def run(self):
        if not self.exists():
            self.create()

    def create(self):
        with self.path.open(mode='w+') as file:
            file.write(self.content)
            file.flush()

    def exists(self):
        return self.path.exists() and self.path.is_file()


class PathLookupPrompt:

    def __init__(self, ask_current_path=True, path_type='folder', output_function=print, input_function=input):
        self.ask_current_path = ask_current_path
        self.path_type = path_type
        self.print = output_function
        self.input = input_function

    @property
    def path(self):
        return self.get()

    def get(self):
        """
        Returns the path that was input
        :return: string
        """
        # First asking if the current path wants to be used
        if self.ask_current_path:
            flag, path = self._prompt_current_path()
            return path

        # Getting the path from user input
        path_valid = False
        while not path_valid:
            path = self._prompt_path_input()
            path_valid = self._check_path(path)

        return path

    def _check_path(self, path_string):
        """
        Checks if the path exists and if the path has the correct type. Returns true if everything is fine and false in
        case there is a problem.
        :param path_string: The string path to be checked
        :return: boolean
        """
        path = pathlib.Path(path_string)
        if path.exists():
            # Checking if it is the right type
            # Doing things differently depending on which type of path it is supposed to be, specif. by self.path_type
            if self.path_type == 'folder':
                if path.is_dir():
                    return True
                else:
                    self.print('The given path is not a folder!')
            elif self.path_type == 'file':
                if path.is_file():
                    return True
                else:
                    self.print('The given path is not a file')
        else:
            self.print('The given path does not exist')
        # Returning false at the end when true has not been returned before
        return False

    def _prompt_path_input(self):
        """
        Simply prompts the user to input a path string and returns the input
        :return:
        """
        input_string = self.input(
            '\nPlease enter path: '
        )
        return input_string

    def _prompt_current_path(self):
        """
        Presents the user with the string path of the current working directory and asks if this path should be used
        for the prompted path.
        :return: (decision, cwd_path)
        decision - The boolean value of whether the user wants to use the current working directory as the path or not
        cwd_path - The string path of the current working directory
        """
        self.print('\nYour current working directory is:')
        self.print('{}'.format(os.getcwd()))
        input_string = self.input(
            'Would you like to use this path? (y/n)'
        )

        if input_string.upper().strip(' ') in ['Y', 'YES']:
            return True, os.getcwd()
        else:
            return False, os.getcwd()


