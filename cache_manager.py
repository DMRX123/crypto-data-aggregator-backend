# cache_manager.py - Memory Cache
import time

class CacheManager:
    def __init__(self):
        self.cache = {}
        print("✅ Cache initialized (Memory)")
    
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < 5:
                return data
        return None
    
    def set(self, key, data):
        self.cache[key] = (data, time.time())
        return True
    
    def clear(self):
        self.cache = {}
        print("🧹 Cache cleared")
