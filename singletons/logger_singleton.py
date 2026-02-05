# singletons/logger_singleton.py
# Singleton pattern for centralized logging management across the application


import logging

class LoggerSingleton:
    _instance = None # stores the singleton instance


    def __new__(cls, *args, **kwargs): # ensures that there is only one instance of LoggerSingleton
        if not cls._instance:
            cls._instance = super(LoggerSingleton, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance


    def _initialize(self): # sets up the logger with formatting and output handler
        self.logger = logging.getLogger("connectly_logger") # creates a logger instance
        handler = logging.StreamHandler() # outputs logs to the console
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s") # log format is formatted: timestamp, level, message
        handler.setFormatter(formatter) # applies format to handler
        self.logger.addHandler(handler) # attaches handler to logger
        self.logger.setLevel(logging.INFO) # sets minimum log level to INFO


    def get_logger(self): # returns the logger instance for use in other parts of the app
        return self.logger

