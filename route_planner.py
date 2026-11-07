"""Route Planning Module (Task 4) - Dijkstra's algorithm."""
import heapq
from dataclasses import dataclass, field

from network_model import INF


@dataclass
class RouteResult:
    source: str
    target: str
    path: list
    cost: float
    dist: dict
    steps: list = field(default_factory=list)  # every distance update
    algorithm: str = ""

    @property
    def found(self):
        return bool(self.path)


def reconstruct_path(prev, source, target):
    if target != source and target not in prev:
        return []
    path, node = [target], target
    while node != source:
        node = prev[node]
        path.append(node)
    return path[::-1]


def dijkstra(net, source, target=None, record_steps=True):
    """Shortest path from `source` (to `target` if given). Non-negative weights.
    Complexity: O((V + E) log V) with a binary heap."""
    if source not in net.adj:
        raise KeyError(f"Unknown intersection: {source}")
    dist = {n: INF for n in net.adj}
    prev, steps, settled = {}, [], set()
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in settled:
            continue
        settled.add(u)
        if target is not None and u == target:
            break
        for v, w in net.adj[u].items():
            if v in settled:
                continue
            nd = d + w
            if nd < dist[v]:
                if record_steps:
                    steps.append({"Step": len(steps) + 1, "Settled node": u, "Relax to": v,
                                  "Road cost": w, "Old distance": dist[v], "New distance": nd})
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
    path = reconstruct_path(prev, source, target) if target is not None else []
    cost = dist[target] if target is not None else 0
    return RouteResult(source, target, path, cost, dist, steps, "Dijkstra")
