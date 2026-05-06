# hash_table.py

class HashTable:
    def __init__(self, initial_capacity=211, load_factor=0.7):
        if initial_capacity <= 0:
            raise ValueError("initial_capacity must be positive")

        self.capacity = initial_capacity
        self.load_factor = load_factor
        self.size = 0
        self.table = [[] for _ in range(self.capacity)]

    # ---------- CORE INTERNALS ----------

    def _hash(self, key):
        return hash(key) % self.capacity

    def _should_resize(self):
        return self.size / self.capacity >= self.load_factor

    def _resize(self):
        old_table = self.table
        self.capacity = self.capacity * 2 + 1
        self.table = [[] for _ in range(self.capacity)]
        self.size = 0

        for bucket in old_table:
            for key, value in bucket:
                self.insert(key, value)

    # ---------- PUBLIC API ----------

    def insert(self, key, value):
        if key is None:
            raise ValueError("key cannot be None")

        index = self._hash(key)
        bucket = self.table[index]

        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return

        bucket.append((key, value))
        self.size += 1

        if self._should_resize():
            self._resize()

    def get(self, key):
        if key is None:
            return None

        index = self._hash(key)
        bucket = self.table[index]

        for k, v in bucket:
            if k == key:
                return v

        return None

    def delete(self, key):
        if key is None:
            raise ValueError("key cannot be None")

        index = self._hash(key)
        bucket = self.table[index]

        for i, (k, _) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.size -= 1
                return True

        return False

    # ---------- UTILITIES ----------

    def contains(self, key):
        return self.get(key) is not None

    def keys(self):
        return [k for bucket in self.table for k, _ in bucket]

    def values(self):
        return [v for bucket in self.table for _, v in bucket]

    def items(self):
        return [(k, v) for bucket in self.table for k, v in bucket]

    def clear(self):
        self.capacity = 211
        self.size = 0
        self.table = [[] for _ in range(self.capacity)]

    def __len__(self):
        return self.size

    def __str__(self):
        return f"HashTable(size={self.size}, capacity={self.capacity})"
