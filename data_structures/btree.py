class BPlusNode:
    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys = []
        self.children = []
        self.next = None

class BPlusTree:
    def __init__(self, order):
        self.root = BPlusNode()
        self.order = order

    def insert(self, key, value):
        # Handle root split if needed
        if len(self.root.keys) == self.order:
            old_root = self.root
            self.root = BPlusNode(leaf=False)
            self.root.children = [old_root]
            self._split_child(self.root, 0)

        self._insert_non_full(self.root, key, value)

    def _insert_non_full(self, node, key, value):
        i = len(node.keys) - 1

        if node.leaf:
            # Insert into leaf node
            while i >= 0 and key < node.keys[i][0]:
                i -= 1
            node.keys.insert(i + 1, (key, value))
        else:
            # Find the child to recurse to
            while i >= 0 and key < node.keys[i][0]:
                i -= 1
            i += 1

            if len(node.children[i].keys) == self.order:
                self._split_child(node, i)
                if key > node.keys[i][0]:
                    i += 1

            self._insert_non_full(node.children[i], key, value)

    def _split_child(self, parent, child_index):
        order = self.order
        child = parent.children[child_index]
        new_node = BPlusNode(leaf=child.leaf)

        # Split differently for leaf and non-leaf nodes
        if child.leaf:
            mid = order // 2
            new_node.keys = child.keys[mid:]
            child.keys = child.keys[:mid]

            # Update leaf node links
            new_node.next = child.next
            child.next = new_node

            # Copy up the first key of new node
            parent.keys.insert(child_index, (new_node.keys[0][0], None))
        else:
            mid = (order - 1) // 2
            new_node.keys = child.keys[mid+1:]
            new_node.children = child.children[mid+1:]

            # Move up the middle key
            parent.keys.insert(child_index, child.keys[mid])

            child.keys = child.keys[:mid]
            child.children = child.children[:mid+1]

        parent.children.insert(child_index + 1, new_node)

    def search(self, key):
        node = self.root
        while not node.leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i][0]:
                i += 1
            node = node.children[i]

        # Search within leaf node
        for k, v in node.keys:
            if k == key:
                return v
        return None