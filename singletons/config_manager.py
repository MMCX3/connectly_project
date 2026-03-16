# singletons/config_manager.py
# Singleton pattern for centralized configuration management

class ConfigManager:
    """Singleton class to manage application configuration settings."""

    _instance = None # stores the singleton instance


    def __new__(cls, *args, **kwargs): 
        """Function to create or return the singleton instance"""
       
        if not cls._instance: # creates instance if it doesn't exist
            cls._instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance


    def _initialize(self): 
        """Private method to initialize configuration settings"""

        self.settings = { # runs only once when the instance is created
            "DEFAULT_PAGE_SIZE": 10, # default number of items returned per paginated query
            "ENABLE_ANALYTICS": True,
            "RATE_LIMIT": 100
        }


    def get_setting(self, key):
        """Retrieves a configuration setting by key"""

        return self.settings.get(key) 


    def set_setting(self, key, value):
        """Updates a configuration setting by key"""
        self.settings[key] = value 

