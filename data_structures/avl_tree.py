class AVLNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def __init__(self):
        self.root = None
        
    def height(self, node):
        if not node:
            return 0
        return node.height
    
    def balance(self, node):
        if not node:
            return 0
        return self.height(node.left) - self.height(node.right)
    
    def right_rotate(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = max(self.height(y.left), self.height(y.right)) + 1
        x.height = max(self.height(x.left), self.height(x.right)) + 1
        return x
    
    def left_rotate(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = max(self.height(x.left), self.height(x.right)) + 1
        y.height = max(self.height(y.left), self.height(y.right)) + 1
        return y
    
    def insert(self, key, value):
        self.root = self._insert(self.root, key, value)
        
    def _insert(self, node, key, value):
        if not node:
            return AVLNode(key, value)
        
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value = value
            return node
            
        node.height = max(self.height(node.left), self.height(node.right)) + 1
        
        balance = self.balance(node)
        
        if balance > 1:
            if key < node.left.key:
                return self.right_rotate(node)
            else:
                node.left = self.left_rotate(node.left)
                return self.right_rotate(node)
                
        if balance < -1:
            if key > node.right.key:
                return self.left_rotate(node)
            else:
                node.right = self.right_rotate(node.right)
                return self.left_rotate(node)
                
        return node
        
    def search(self, key):
        return self._search(self.root, key)
        
    def _search(self, node, key):
        if not node:
            return None
        if node.key == key:
            return node.value
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)
