# coding=utf-8

from os import getcwd
from os.path import join, isfile, expanduser, exists

from fabric.api import env
from yaml import load, YAMLError

from ..utils.utils import custom_exit, logger_config

# Create the logger
logger = logger_config(join(getcwd(), 'clusterp.log'))


class Configuration(object):
    """
    Configuration class to load the content of the YAML configuration file
    """

    __instance = None

    def __init__(self):
        """
        Constructor
        """
        if Configuration.__instance is not None:
            logger.error("Cannot instantiate the Configuration more than once. Use Configuration.get_instance() "
                         "instead.")
            custom_exit(-1)

        # Define the base configuration attributes
        self.hardware = ['cpu', 'memory', 'swap', 'disk', 'network']
        self.interval = 1
        self.sar_args = {
            'cpu': '-u',
            'memory': '-r',
            'swap': '-S',
            'disk': '-dp',
            'network': '-n DEV'
        }
        self.raw_columns = {
            'cpu': ['time', 'CPU', '%user', '%nice', '%system', '%iowait', '%steal', '%idle'],
            'memory': ['time', 'kbmemfree', 'kbmemused', '%memused', 'kbbuffers', 'kbcached', 'kbcommit', '%commit',
                       'kbactive', 'kbinact', 'kbdirty'],
            'swap': ['time', 'kbswpfree', 'kbswpused', '%swpused', 'kbswpcad', '%swpcad'],
            'disk': ['time', 'DEV', 'tps', 'rd_sec/s', 'wr_sec/s', 'avgrq-sz', 'avgqu-sz', 'await', 'svctm', '%util'],
            'network': ['time', 'IFACE', 'rxpck/s', 'txpck/s', 'rxkB/s', 'txkB/s', 'rxcmp/s', 'txcmp/s', 'rxmcst/s']
        }
        self.relevant_columns = {
            'cpu': ['time', '%iowait', '%idle'],
            'memory': ['time', 'kbmemused'],
            'swap': ['time', 'kbswpused'],
            'disk': ['time', 'DEV', 'rd_sec/s', 'wr_sec/s', '%util'],
            'network': ['time', 'IFACE', 'rxkB/s', 'txkB/s']
        }
        self.renamed_columns = {
            'cpu': {
                '%iowait': '%i/o_wait'
            }, 'memory': {
                'kbmemused': 'memory_used_mb'
            }, 'swap': {
                'kbswpused': 'swap_used_mb'
            }, 'disk': {
                'DEV': 'device',
                'rd_sec/s': 'read_mb/s',
                'wr_sec/s': 'write_mb/s'
            }, 'network': {
                'IFACE': 'interface',
                'rxkB/s': 'read_mb/s',
                'txkB/s': 'transmitted_mb/s'
            }
        }
        self.columns_dtype = {
            'cpu': {
                'time': int,
                '%i/o_wait': float,
                '%util': float
            }, 'memory': {
                'time': int,
                'memory_used_mb': float
            }, 'swap': {
                'time': int,
                'swap_used_mb': float
            }, 'disk': {
                'time': int,
                'read_mb/s': float,
                'write_mb/s': float,
                '%util': float
            }, 'network': {
                'read_mb/s': float,
                'transmitted_mb/s': float,
                'time': int
            }
        }

        # Define the user configuration attributes
        self.ssh_gateway = None
        self.ssh_username = None
        self.ssh_password = None
        self.hosts = None
        self.filesystem_names = None
        self.net_interfaces = None
        self.output_dir = getcwd()

        # Adding another attribute to handle the aliases (dictionary)
        self.aliases = {}

    def load_configuration(self):
        """
        Load the configuration files
        :return:
        """
        # Load the user configuration file
        self.__set_configuration_attributes(join(getcwd(), 'config.yml'))

        # Check that all of the attributes has been configured by the user
        if self.hosts is None:
            logger.error("You need to configure the 'hosts' attribute in the config file!")
            custom_exit(-4)

        # Store the aliases in order to use them later
        self.hosts = self.__get_aliases('hosts')
        self.filesystem_names = self.__get_aliases('filesystem_names') if self.filesystem_names is not None else None
        self.net_interfaces = self.__get_aliases('net_interfaces') if self.net_interfaces is not None else None

        # Setup the hosts addresses for Fabric
        env.hosts = self.hosts
        # Setup the SSH gateway
        env.gateway = self.ssh_gateway if self.ssh_gateway is not None else env.gateway
        # Setup the username
        env.user = self.ssh_username if self.ssh_username is not None else env.user
        # Setup the password for ssh connections
        env.password = self.ssh_password if self.ssh_password is not None else env.password
        # Fix to use the user ~/.ssh/config file
        env.use_ssh_config = True if env.ssh_config_path is True and isfile(expanduser(env.ssh_config_path)) is True \
            else env.use_ssh_config

    @staticmethod
    def get_instance():
        """
        Return the active instance if it exists, else return a new instance
        :return:
        """
        if Configuration.__instance is None:
            Configuration.__instance = Configuration()
        return Configuration.__instance

    @staticmethod
    def __load_yaml_file(yaml_file_path):
        """
        Load the content of a YAML file
        :param yaml_file_path: The YAML file path
        :return:
        """
        with open(yaml_file_path) as f:
            try:
                return load(f)
            except YAMLError as e:
                print(e)
                custom_exit(-2)

    def __set_configuration_attributes(self, config_file_path):
        """
        Set the base configuration attributes
        :param config_file_path: The configuration file path (YAML file)
        :return:
        """
        if exists(config_file_path) is False:
            print("No configuration file found!\nRun `clusterp init` to create a new one.")
            logger.error("No configuration file found! Run `clusterp init` to create a new one.")
            exit(-3)
        conf = self.__load_yaml_file(config_file_path)
        for key, value in conf.items():
            setattr(self, key, value)

    def __get_aliases(self, attribute):
        """
        Get the aliases from the configuration file
        :param attribute: Configuration entry
        :return:
        """
        # Store the values in a list
        temp = []
        for element in getattr(self, attribute):
            if type(element) == dict:
                for _key, _value in element.items():
                    if attribute not in self.aliases.keys():
                        self.aliases[attribute] = {}
                    # Store the aliases in a dictionary
                    self.aliases[attribute][_key] = _value
                    temp.append(_key)
            else:
                temp.append(element)
        # Return the list of values
        return temp
