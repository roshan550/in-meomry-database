import random

class SkipNode:
    def __init__(self, key, value, level):
        self.key = key
        self.value = value
        self.forward = [None] * (level + 1)

class SkipList:
    def __init__(self, max_level=16, p=0.5):
        self.max_level = max_level
        self.p = p
        self.level = 0
        self.header = SkipNode(-1, None, max_level)
        
    def random_level(self):
        lvl = 0
        while random.random() < self.p and lvl < self.max_level:
            lvl += 1
        return lvl
        
    def insert(self, key, value):
        update = [None] * (self.max_level + 1)
        current = self.header
        
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current
            
        current = current.forward[0]
        
        if current and current.key == key:
            current.value = value
        else:
            new_level = self.random_level()
            
            if new_level > self.level:
                for i in range(self.level + 1, new_level + 1):
                    update[i] = self.header
                self.level = new_level
                
            new_node = SkipNode(key, value, new_level)
            
            for i in range(new_level + 1):
                new_node.forward[i] = update[i].forward[i]
                update[i].forward[i] = new_node
                
    def search(self, key):
        current = self.header
        
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
                
        current = current.forward[0]
        
        if current and current.key == key:
            return current.value
        return None
