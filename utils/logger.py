import logging 
from datetime import datetime 
import sys 


def setup_logger(name: str, log_file: str= "bot.log"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    logger.handler.clear()

    #file handler
    file_handler = logging.FileHandler(sys.stdout)
    file_handler.setLevel(logging.INFO)

    #Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    #Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
        )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger