# coding=utf-8

from logging import basicConfig, getLogger, DEBUG

# Create the logger
logger = getLogger(__name__)


def logger_config(log_file_path):
    """
    Logger configuration
    :param log_file_path: The page id
    :return:
    """
    # Configure the logging module
    basicConfig(
        format='[%(asctime)s][%(levelname)s][%(name)s.%(funcName)s] %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        filename=log_file_path,
        level=DEBUG
    )
    # Return the logger
    return getLogger(__name__)


def custom_exit(exit_code):
    """
    Custom exit function that shadows the built-in one
    :param exit_code: Exit code
    :return: Nothing
    """
    print("The program exited with code: {}.\nPlease consult the log files for details.".format(exit_code))
    logger.error("Process finished with exit code {}".format(exit_code))
    exit(exit_code)
