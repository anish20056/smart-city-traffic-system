"""Traffic Analysis Module (Task 5) - Bellman-Ford and congestion simulation."""
from network_model import INF
from route_planner import RouteResult, reconstruct_path


def bellman_ford(net, source, target=None, record_steps=True):
    """Bellman-Ford shortest paths. O(V*E); also detects negative cycles.
    Every undirected road is relaxed in both directions."""
    if source not in net.adj:
        raise KeyError(f"Unknown intersection: {source}")
    arcs = [(u, v, w) for u, nb in net.adj.items() for v, w in nb.items()]
    dist = {n: INF for n in net.adj}
    prev, steps = {}, []
    dist[source] = 0
    for p in range(1, net.num_nodes):
        changed = False
        for u, v, w in arcs:
            if dist[u] != INF and dist[u] + w < dist[v]:
                if record_steps:
                    steps.append({"Pass": p, "Edge": f"{u} -> {v}", "Road cost": w,
                                  "Old distance": dist[v], "New distance": dist[u] + w})
                dist[v] = dist[u] + w
                prev[v] = u
                changed = True
        if not changed:  # early exit: converged
            break
    for u, v, w in arcs:
        if dist[u] != INF and dist[u] + w < dist[v]:
            raise ValueError("Negative-weight cycle detected.")
    path = reconstruct_path(prev, source, target) if target is not None else []
    cost = dist[target] if target is not None else 0
    return RouteResult(source, target, path, cost, dist, steps, "Bellman-Ford")


def apply_congestion(net, roads, factor=1.0, close=False):
    """Return a new network where `roads` (list of (u, v)) are slowed down by
    `factor` (e.g. 2.5 = 2.5x travel time) or removed completely (road closure)."""
    new = net.copy()
    for u, v in roads:
        if close:
            new.remove_road(u, v)
        else:
            new.set_weight(u, v, net.adj[u][v] * factor)
    return new


def compare_routes(before, after):
    """Summarise the impact of a traffic change on one source->destination trip."""
    if not before.found or not after.found:
        return {"route_changed": before.path != after.path, "reachable_after": after.found,
                "original_cost": before.cost, "updated_cost": after.cost if after.found else None,
                "delta": None, "pct": None}
    delta = after.cost - before.cost
    return {"route_changed": before.path != after.path, "reachable_after": True,
            "original_cost": before.cost, "updated_cost": after.cost,
            "delta": delta, "pct": (delta / before.cost * 100) if before.cost else 0.0}
