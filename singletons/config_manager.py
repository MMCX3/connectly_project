# singletons/ config_manager.py
# Singleton pattern for centralized configuration management

class ConfigManager:
    _instance = None # stores the singleton instance


    def __new__(cls, *args, **kwargs): # function to create or return the singleton instance
        if not cls._instance: # creates instance if it doesn't exist
            cls._instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance


    def _initialize(self): # private method to initialize configuration settings
        self.settings = { # runs only once when the instance is created
            "DEFAULT_PAGE_SIZE": 20,
            "ENABLE_ANALYTICS": True,
            "RATE_LIMIT": 100
        }


    def get_setting(self, key):
        return self.settings.get(key) # retrieves a configuration setting by key


    def set_setting(self, key, value):
        self.settings[key] = value #updates a configuration setting by key

