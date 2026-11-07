"""Road Network Modeling Module (Task 3).

The city is modelled as a weighted graph:
    vertices -> intersections / junctions
    edges    -> roads
    weights  -> travel cost (minutes or km)
Stored internally as an adjacency list (dict of dicts).
"""
import random
import pandas as pd

INF = float("inf")


class RoadNetwork:
    def __init__(self, directed=False):
        self.directed = directed
        self.adj = {}  # {node: {neighbour: weight}}

    # ---------- construction ----------
    def add_intersection(self, name):
        name = str(name).strip()
        if not name:
            raise ValueError("Intersection name cannot be empty.")
        self.adj.setdefault(name, {})

    def add_road(self, u, v, weight):
        u, v = str(u).strip(), str(v).strip()
        if u == v:
            raise ValueError("A road must connect two different intersections.")
        weight = float(weight)
        if weight <= 0:
            raise ValueError("Travel cost must be positive.")
        self.add_intersection(u)
        self.add_intersection(v)
        self.adj[u][v] = weight
        if not self.directed:
            self.adj[v][u] = weight

    def remove_road(self, u, v):
        self.adj[u].pop(v, None)
        if not self.directed:
            self.adj[v].pop(u, None)

    def set_weight(self, u, v, weight):
        if v not in self.adj.get(u, {}):
            raise KeyError(f"No road between {u} and {v}.")
        self.add_road(u, v, weight)

    def copy(self):
        new = RoadNetwork(self.directed)
        new.adj = {u: dict(nb) for u, nb in self.adj.items()}
        return new

    # ---------- queries ----------
    def nodes(self):
        return list(self.adj)

    def edges(self):
        """List of (u, v, w); each undirected road listed once."""
        out = []
        for u, nb in self.adj.items():
            for v, w in nb.items():
                if self.directed or u <= v:
                    out.append((u, v, w))
        return out

    def undirected_edges(self):
        """Roads as undirected pairs (cheapest direction kept) - used by MST."""
        best = {}
        for u, v, w in self.edges():
            key = tuple(sorted((u, v)))
            best[key] = min(w, best.get(key, INF))
        return [(a, b, w) for (a, b), w in best.items()]

    @property
    def num_nodes(self):
        return len(self.adj)

    @property
    def num_edges(self):
        return len(self.edges())

    # ---------- representations ----------
    def adjacency_list(self):
        return {u: sorted(nb.items()) for u, nb in sorted(self.adj.items())}

    def adjacency_list_text(self):
        lines = []
        for u, nb in self.adjacency_list().items():
            items = ", ".join(f"({v}, {w:g})" for v, w in nb) or "-"
            lines.append(f"{u} -> {items}")
        return "\n".join(lines)

    def adjacency_matrix(self, display=True):
        nodes = sorted(self.adj)
        data = [[0 if u == v else self.adj[u].get(v, INF) for v in nodes] for u in nodes]
        df = pd.DataFrame(data, index=nodes, columns=nodes)
        if display:
            df = df.map(lambda x: "∞" if x == INF else f"{x:g}")
        return df

    def to_edge_df(self):
        return pd.DataFrame(self.edges(), columns=["from", "to", "weight"])

    def to_networkx(self):
        import networkx as nx
        g = nx.DiGraph() if self.directed else nx.Graph()
        g.add_nodes_from(self.adj)
        for u, v, w in self.edges():
            g.add_edge(u, v, weight=w)
        return g

    # ---------- factories ----------
    @classmethod
    def from_edge_df(cls, df):
        net = cls()
        cols = {c.lower().strip(): c for c in df.columns}
        for need in ("from", "to", "weight"):
            if need not in cols:
                raise ValueError("CSV needs columns: from, to, weight")
        for _, r in df.iterrows():
            net.add_road(r[cols["from"]], r[cols["to"]], r[cols["weight"]])
        return net

    @classmethod
    def random(cls, n, seed=42, extra_edge_factor=1.0, w_range=(1, 20)):
        """Connected random network: random spanning tree + extra roads."""
        rng = random.Random(seed)
        net = cls()
        names = [f"I{i}" for i in range(n)]
        for nm in names:
            net.add_intersection(nm)
        for i in range(1, n):  # spanning tree guarantees connectivity
            net.add_road(names[i], names[rng.randrange(i)], rng.randint(*w_range))
        extra, attempts = int(n * extra_edge_factor), 0
        while extra > 0 and attempts < 20 * n:
            attempts += 1
            a, b = rng.sample(names, 2) if n > 1 else (None, None)
            if a is None or b in net.adj[a]:
                continue
            net.add_road(a, b, rng.randint(*w_range))
            extra -= 1
        return net

    @classmethod
    def sample_city(cls):
        net = cls()
        roads = [
            ("Airport", "Tech Park", 12), ("Airport", "Highway Jn", 8),
            ("Highway Jn", "Tech Park", 6), ("Highway Jn", "Stadium", 10),
            ("Tech Park", "University", 7), ("University", "Central Station", 5),
            ("Stadium", "Central Station", 9), ("Central Station", "City Hall", 4),
            ("Central Station", "Market", 6), ("City Hall", "Market", 3),
            ("City Hall", "Hospital", 8), ("Market", "Old Town", 5),
            ("Hospital", "Mall", 6), ("Old Town", "Harbor", 7),
            ("Mall", "Harbor", 9), ("Hospital", "Old Town", 10),
            ("University", "Hospital", 11), ("Stadium", "Mall", 14),
        ]
        for u, v, w in roads:
            net.add_road(u, v, w)
        return net
