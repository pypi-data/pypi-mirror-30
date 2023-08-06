# coding=utf-8

from logging import getLogger
from multiprocessing import Process

from fabric.api import execute
from fabric.decorators import parallel

from ..configuration.configuration import Configuration
from ..core.core import collect_data, parse_data, plot_data, download_data, kill_process

# Create the logger
logger = getLogger(__name__)
# Get the instance of Configuration
cf = Configuration.get_instance()


@parallel
def start():
    """
    Start the data collection
    :return:
    """
    # Loading the configuration files
    cf.load_configuration()
    # Start
    logger.info("Starting data collection")
    execute(collect_data, hosts=cf.hosts)


@parallel
def stop():
    """
    Stop the data collection
    :return: 
    """
    # Loading the configuration files
    cf.load_configuration()
    # Stop
    logger.info("Stopping the data collection")
    execute(kill_process, "sar", hosts=cf.hosts)
    logger.info("Downloading collected data from nodes")
    execute(download_data, "/tmp/raw", cf.output_dir, hosts=cf.hosts)


def parse():
    """
    Parse the data
    :return:
    """
    # Loading the configuration files
    cf.load_configuration()
    # Parse
    logger.info("Parsing the data")
    processes = [Process(target=parse_data, args=(hw,)) for hw in cf.hardware]
    for process in processes:
        process.start()
    for process in processes:
        process.join()


def plot():
    """
    Plot the data
    :return:
    """
    # Loading the configuration files
    cf.load_configuration()
    # Plot
    logger.info("Plotting the data")
    processes = [Process(target=plot_data, args=(hw,)) for hw in cf.hardware]
    for process in processes:
        process.start()
    for process in processes:
        process.join()
