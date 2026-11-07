"""Network Connectivity Module (Task 6) - BFS and DFS."""
from collections import deque


def bfs(net, start):
    """Breadth-first traversal. O(V + E). Returns visit order and BFS levels."""
    order, level = [], {start: 0}
    q = deque([start])
    while q:
        u = q.popleft()
        order.append(u)
        for v in sorted(net.adj[u]):
            if v not in level:
                level[v] = level[u] + 1
                q.append(v)
    return {"order": order, "level": level, "reachable": set(order)}


def dfs(net, start):
    """Depth-first traversal (iterative, so large networks cannot overflow the
    recursion limit). O(V + E). Same preorder as the recursive version."""
    order, seen, stack = [], set(), [start]
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        order.append(u)
        for v in sorted(net.adj[u], reverse=True):
            if v not in seen:
                stack.append(v)
    return {"order": order, "reachable": set(order)}


def unreachable_from(net, start, result):
    return sorted(set(net.adj) - result["reachable"])


def connected_components(net):
    seen, comps = set(), []
    for n in sorted(net.adj):
        if n not in seen:
            comp = bfs(net, n)["order"]
            seen.update(comp)
            comps.append(comp)
    return comps
