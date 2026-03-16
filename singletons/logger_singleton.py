# singletons/logger_singleton.py
# Singleton pattern for centralized logging management across the application


import logging

class LoggerSingleton:
    """Singleton class to manage application logging."""

    _instance = None # stores the singleton instance


    def __new__(cls, *args, **kwargs):
        """Creates or returns the singleton instance; ensures there's only one logger instance across the app."""

        if not cls._instance:
            cls._instance = super(LoggerSingleton, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance


    def _initialize(self):
        """Initializes the logger with formatting and output handler. Runs only once when the instance is created."""

        self.logger = logging.getLogger("connectly_logger") # creates a logger instance
        handler = logging.StreamHandler() # outputs logs to the console
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s") # log format is formatted: timestamp, level, message
        handler.setFormatter(formatter) # applies format to handler
        self.logger.addHandler(handler) # attaches handler to logger
        self.logger.setLevel(logging.INFO) # sets minimum log level to INFO


    def get_logger(self): 
        """Returns the logger instance for use across the app."""
        return self.logger

