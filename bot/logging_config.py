import logging
import os
from datetime import datetime

def setup_logging():
    """Configure logging for the trading bot."""
    
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'trading_bot.log')
    
    logger = logging.getLogger('trading_bot')
    logger.setLevel(logging.DEBUG)
    
    if logger.handlers:
        return logger
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    
    file_handler.setFormatter(file_format)
    console_handler.setFormatter(console_format)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name=None):
    """Get a logger instance."""
    if name:
        return logging.getLogger(f'trading_bot.{name}')
    return logging.getLogger('trading_bot')
