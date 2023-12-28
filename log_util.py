import logging
import os
from datetime import datetime

def setup_logging(log_dir='logs'):
    """Sets up the logging environment."""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Creating a filename with a timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = os.path.join(log_dir, f'translation_log_{timestamp}.log')

    # Setting up basic configuration for logging
    logging.basicConfig(filename=log_filename,
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

def log_message(level, message):
    """Logs a message at the given level."""
    if level.lower() == 'info':
        logging.info(message)
    elif level.lower() == 'error':
        logging.error(message)
    elif level.lower() == 'warning':
        logging.warning(message)
    # Add other levels if needed

# Call setup_logging() when this module is imported
setup_logging()
