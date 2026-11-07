"""Infrastructure Planning Module (Task 7) - Prim and Kruskal MST."""
import heapq


def _undirected_adj(net):
    adj = {n: {} for n in net.adj}
    for u, v, w in net.undirected_edges():
        adj[u][v] = w
        adj[v][u] = w
    return adj


def prim(net, start=None, record_steps=True):
    """Prim's algorithm with a binary heap, O(E log V).
    On a disconnected network it returns a minimum spanning forest."""
    adj = _undirected_adj(net)
    nodes = sorted(adj)
    if not nodes:
        return {"edges": [], "total": 0, "steps": [], "spanning": True}
    order = ([start] if start else []) + [n for n in nodes if n != start]
    visited, edges, steps = set(), [], []
    for root in order:
        if root in visited:
            continue
        visited.add(root)
        heap = [(w, root, v) for v, w in adj[root].items()]
        heapq.heapify(heap)
        while heap:
            w, u, v = heapq.heappop(heap)
            if v in visited:
                continue
            visited.add(v)
            edges.append((u, v, w))
            if record_steps:
                steps.append({"Step": len(edges), "Added road": f"{u} - {v}", "Cost": w,
                              "Tree size": len(visited)})
            for x, wx in adj[v].items():
                if x not in visited:
                    heapq.heappush(heap, (wx, v, x))
    return {"edges": edges, "total": sum(e[2] for e in edges), "steps": steps,
            "spanning": len(edges) == len(nodes) - 1}


class DisjointSet:
    def __init__(self, items):
        self.parent = {i: i for i in items}
        self.rank = {i: 0 for i in items}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def kruskal(net, record_steps=True):
    """Kruskal's algorithm with union-find, O(E log E)."""
    ds = DisjointSet(net.adj)
    edges, steps = [], []
    for u, v, w in sorted(net.undirected_edges(), key=lambda e: (e[2], e[0], e[1])):
        accepted = ds.union(u, v)
        if accepted:
            edges.append((u, v, w))
        if record_steps:
            steps.append({"Considered road": f"{u} - {v}", "Cost": w,
                          "Decision": "Accepted" if accepted else "Rejected (cycle)"})
    return {"edges": edges, "total": sum(e[2] for e in edges), "steps": steps,
            "spanning": len(edges) == net.num_nodes - 1}
