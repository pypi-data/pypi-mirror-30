import uuid
import datetime
import json

class Backpack(object):
    def __init__(self, **kwargs):
        self.temp_items = {}
        self.metrics = {}
        self.perm_items = {}
        self.one_time_items = {}
        self.timers = {}
        self.perm_items['id'] = kwargs.pop("id", str(uuid.uuid4()))

    @property
    def id(self):
        return self.perm_items['id']
        
    def with_item(self, key, value):
        self.perm_items[key] = value
        return self
        
    def without_item(self, key):
        del self.perm_items[key]
        return self

    def with_one_time_item(self, key, value):
        self.one_time_items[key] = value
        return self

    def without_one_item_item(self, key):
        del self.one_time_items[key]
        return self
        
    def with_metric(self, key, value):
        metric = 'm_{}'.format(key)
        self.metrics[metric] = value
        return self
        
    def without_metric(self, key):
        metric = 'm_{}'.format(key)
        del self.metrics[metric]
        return self

    def with_timer(self, name):
        self.timers[name] = datetime.datetime.now().isoformat()
        return self
        
    def without_timer(self, name):
        del self.timers[name]
        return self

    def to_json(self):
        b = {}
        b['id'] = self.perm_items['id']
        b['metrics'] = self.metrics
        b['perm_items'] = self.perm_items
        b['timers'] = self.timers
        return json.dumps(b)
        
    def from_json(self, j):
        backpack = json.loads(j)
        self.metrics = backpack['metrics']
        self.perm_items = backpack['perm_items']
        self.timers = backpack['timers']
        self.one_time_items = {}
        self.temp_items = {}
        return self