# graph.py
# Advanced routing graph for warehouse & delivery optimization
# Adjacency List + Dijkstra + Path Reconstruction
# Designed to integrate cleanly with Inventory per warehouse

import heapq


class Graph:
    def __init__(self):
        # node -> {neighbor: weight}
        self.adj = {}

    # ---------- NODE & EDGE MANAGEMENT ----------

    def add_node(self, node):
        if node not in self.adj:
            self.adj[node] = {}

    def add_edge(self, src, dest, weight, bidirectional=True):
        if weight < 0:
            raise ValueError("Negative weights are not allowed (Dijkstra constraint)")

        self.add_node(src)
        self.add_node(dest)

        self.adj[src][dest] = weight
        if bidirectional:
            self.adj[dest][src] = weight

    # ---------- DIJKSTRA CORE ----------

    def dijkstra(self, start):
        if start not in self.adj:
            raise ValueError("Start node does not exist in graph")

        distances = {node: float("inf") for node in self.adj}
        previous = {node: None for node in self.adj}

        distances[start] = 0
        pq = [(0, start)]

        while pq:
            current_dist, node = heapq.heappop(pq)

            if current_dist > distances[node]:
                continue

            for neighbor, weight in self.adj[node].items():
                new_dist = current_dist + weight

                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = node
                    heapq.heappush(pq, (new_dist, neighbor))

        return distances, previous

    # ---------- SHORTEST PATH (WITH ROUTE) ----------

    def shortest_path(self, start, target):
        distances, previous = self.dijkstra(start)

        if distances[target] == float("inf"):
            return float("inf"), []

        path = []
        current = target
        while current is not None:
            path.append(current)
            current = previous[current]

        path.reverse()
        return distances[target], path

    # ---------- MULTI-TARGET QUERY ----------

    def nearest_node(self, start, candidates):
        """
        Given a start node and a set of candidate nodes,
        return the nearest candidate and distance.
        """
        distances, _ = self.dijkstra(start)

        nearest = None
        min_dist = float("inf")

        for node in candidates:
            if node in distances and distances[node] < min_dist:
                min_dist = distances[node]
                nearest = node

        return nearest, min_dist

    # ---------- VALIDATION & DEBUG ----------

    def has_node(self, node):
        return node in self.adj

    def nodes(self):
        return list(self.adj.keys())

    def edges(self):
        edge_list = []
        for src in self.adj:
            for dest, w in self.adj[src].items():
                edge_list.append((src, dest, w))
        return edge_list

    def __str__(self):
        return f"Graph(nodes={len(self.adj)}, edges={len(self.edges())})"
