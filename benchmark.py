"""Comparative Analysis (Task 8): timing / memory experiments on growing networks."""
import time
import tracemalloc
from statistics import mean

import pandas as pd

from network_model import RoadNetwork
from route_planner import dijkstra
from traffic_analysis import bellman_ford
from connectivity_module import bfs, dfs
from mst_planner import prim, kruskal


def _time_ms(fn, reps):
    times = []
    for _ in range(reps):
        t = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t)
    return mean(times) * 1000


def _peak_kb(fn):
    tracemalloc.start()
    fn()
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return peak / 1024


def run_benchmarks(sizes=(10, 25, 50, 100), reps=30, seed=42):
    """Returns dict of three comparison DataFrames (one per algorithm pair)."""
    bt, rt, mt = [], [], []
    for n in sizes:
        net = RoadNetwork.random(n, seed=seed + n)
        src, dst = "I0", f"I{n - 1}"
        base = {"Intersections": n, "Roads": net.num_edges}

        fb, fd = (lambda: bfs(net, src)), (lambda: dfs(net, src))
        bt.append({**base,
                   "BFS time (ms)": _time_ms(fb, reps), "DFS time (ms)": _time_ms(fd, reps),
                   "BFS memory (KB)": _peak_kb(fb), "DFS memory (KB)": _peak_kb(fd),
                   "BFS visited": len(bfs(net, src)["order"]),
                   "DFS visited": len(dfs(net, src)["order"])})

        fdj = lambda: dijkstra(net, src, dst, record_steps=False)
        fbf = lambda: bellman_ford(net, src, dst, record_steps=False)
        r1, r2 = fdj(), fbf()
        rt.append({**base,
                   "Dijkstra time (ms)": _time_ms(fdj, reps), "Bellman-Ford time (ms)": _time_ms(fbf, reps),
                   "Dijkstra memory (KB)": _peak_kb(fdj), "Bellman-Ford memory (KB)": _peak_kb(fbf),
                   "Route cost": r1.cost, "Route hops": len(r1.path) - 1,
                   "Costs agree": abs(r1.cost - r2.cost) < 1e-9})

        fp, fk = (lambda: prim(net, record_steps=False)), (lambda: kruskal(net, record_steps=False))
        p, k = fp(), fk()
        mt.append({**base,
                   "Prim time (ms)": _time_ms(fp, reps), "Kruskal time (ms)": _time_ms(fk, reps),
                   "Prim memory (KB)": _peak_kb(fp), "Kruskal memory (KB)": _peak_kb(fk),
                   "Prim MST cost": p["total"], "Kruskal MST cost": k["total"]})
    return {"BFS vs DFS": pd.DataFrame(bt), "Dijkstra vs Bellman-Ford": pd.DataFrame(rt),
            "Prim vs Kruskal": pd.DataFrame(mt)}


if __name__ == "__main__":
    for name, df in run_benchmarks().items():
        print(f"\n== {name} ==")
        print(df.round(4).to_string(index=False))
