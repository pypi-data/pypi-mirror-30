import logging
from backpack import Backpack

class FluentLogger(logging.Logger):
    def __init__(self, **kwargs):
        self.context = {}
        name = kwargs.pop("name", "logger")
        self.logger = logging.getLogger(name)
        self.backpack = {}
        self.backpack = kwargs.pop("backpack", Backpack())

    def with_item(self, key, value):
        self.backpack.with_item(key, value)
        return self

    def without_item(self, key):
        self.backpack.without_item(key)
        return self


    def with_one_time(self, key, value):
        self.backpack.with_one_time(key, value)
        return self
    
    def with_handler(self, handler):
        if self.backpack:
            handler.with_backpack(self.backpack)
        self.logger.addHandler(handler)
        return self

    def log_metric(self, message, name, value):
        self.backpack.with_metric(name, value)
        self.logger.warning(message)
        self.backpack.without_metric(name)
        
    def with_level(self, level):
        self.logger.setLevel(level)
        return self
        
    def info(self, msg):
        self.logger.info(msg)
        return self
        
    def error(self, msg):
        self.logger.error(msg)
        return self
        
    def with_timer(self, name):
        self.backpack.with_timer(name)
        return self
    
    def without_timer(self, name):
        self.backpack.without_timer(name)
        return self
        
    def persist(self, **kwargs):
        id = kwargs.pop('StateId', self.backpack.id)
        state_manager = StateManager()
        state_manager.upsert(self.backpack, StateId = id)