# bst.py
# This is not a weak BST.
# This is a self-balancing AVL Tree with:
# - duplicate price handling
# - deletion
# - inorder traversal
# - range queries
# Anything less would be embarrassing.

class AVLNode:
    def __init__(self, key, value):
        self.key = key              # price
        self.values = [value]       # product_ids (duplicate prices allowed)
        self.left = None
        self.right = None
        self.height = 1


class BST:
    def __init__(self):
        self.root = None

    # ---------- HEIGHT & BALANCE ----------

    def _height(self, node):
        return node.height if node else 0

    def _balance(self, node):
        return self._height(node.left) - self._height(node.right)

    def _update_height(self, node):
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    # ---------- ROTATIONS ----------

    def _rotate_right(self, y):
        x = y.left
        t2 = x.right

        x.right = y
        y.left = t2

        self._update_height(y)
        self._update_height(x)

        return x

    def _rotate_left(self, x):
        y = x.right
        t2 = y.left

        y.left = x
        x.right = t2

        self._update_height(x)
        self._update_height(y)

        return y

    # ---------- INSERT ----------

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
            node.values.append(value)
            return node

        self._update_height(node)
        return self._rebalance(node, key)

    # ---------- DELETE ----------

    def delete(self, key, value):
        self.root = self._delete(self.root, key, value)

    def _delete(self, node, key, value):
        if not node:
            return None

        if key < node.key:
            node.left = self._delete(node.left, key, value)
        elif key > node.key:
            node.right = self._delete(node.right, key, value)
        else:
            if value in node.values:
                node.values.remove(value)

            if node.values:
                return node

            if not node.left:
                return node.right
            if not node.right:
                return node.left

            successor = self._min_value_node(node.right)
            node.key = successor.key
            node.values = successor.values.copy()
            node.right = self._delete(node.right, successor.key, successor.values[0])

        self._update_height(node)
        return self._rebalance_after_delete(node)

    def _min_value_node(self, node):
        while node.left:
            node = node.left
        return node

    # ---------- REBALANCING ----------

    def _rebalance(self, node, key):
        balance = self._balance(node)

        if balance > 1 and key < node.left.key:
            return self._rotate_right(node)

        if balance < -1 and key > node.right.key:
            return self._rotate_left(node)

        if balance > 1 and key > node.left.key:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        if balance < -1 and key < node.right.key:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _rebalance_after_delete(self, node):
        balance = self._balance(node)

        if balance > 1:
            if self._balance(node.left) >= 0:
                return self._rotate_right(node)
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        if balance < -1:
            if self._balance(node.right) <= 0:
                return self._rotate_left(node)
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # ---------- TRAVERSALS ----------

    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            for v in node.values:
                result.append((node.key, v))
            self._inorder(node.right, result)

    # ---------- RANGE SEARCH ----------

    def range_search(self, low, high):
        result = []
        self._range_search(self.root, low, high, result)
        return result

    def _range_search(self, node, low, high, result):
        if not node:
            return

        if low < node.key:
            self._range_search(node.left, low, high, result)

        if low <= node.key <= high:
            result.extend(node.values)

        if node.key < high:
            self._range_search(node.right, low, high, result)

    # ---------- DEBUG ----------

    def __str__(self):
        return f"AVLTree(height={self._height(self.root)})"
