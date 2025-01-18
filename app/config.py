import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
      # Get the project's root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Define the logs directory path at the root level
    logs_dir = os.path.join(project_root, 'logs')

    # Create the logs directory if it doesn't exist
    os.makedirs(logs_dir, exist_ok=True)
    
    # Defines log file path
    log_file = os.path.join(logs_dir, 'weather_app.log')
    
    # Formatter that defines how log messages look
    # %(asctime)s     - Timestamp
    # %(name)s        - Logger name (e.g., 'weather')
    # %(levelname)s   - Level (INFO, ERROR, etc.)
    # %(message)s     - The actual log message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Makes sure file doesnt exceed 5MB
    file_handler = RotatingFileHandler(
        log_file,               # Path to log file
        maxBytes=5*1024*1024,   # 5 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Console handler for printing logs to terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Root logger configuration
    root_logger = logging.getLogger()     # Get the root logger
    root_logger.setLevel(logging.INFO)    # Set minimum log level
    root_logger.addHandler(file_handler)  # Add file output
    root_logger.addHandler(console_handler)  # Add console output
    
    return root_logger
