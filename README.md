# Smart City Traffic Management and Route Optimization System

A Streamlit application that models a city's road network as a weighted graph and applies graph algorithms to routing, congestion analysis, connectivity checks and infrastructure planning.

## Features
| Module | File | Algorithms |
|---|---|---|
| Road Network Modeling | `network_model.py` | adjacency list, adjacency matrix, CSV load, random/sample cities |
| Route Planning | `route_planner.py` | Dijkstra (with every distance update shown) |
| Traffic Analysis | `traffic_analysis.py` | Bellman-Ford, congestion / road closure simulation, route comparison |
| Network Connectivity | `connectivity_module.py` | BFS, DFS, reachability, connected regions |
| Infrastructure Planning | `mst_planner.py` | Prim, Kruskal (union-find) |
| Comparative Analysis | `benchmark.py` | timing and memory on 10/25/50/100 intersections |
| UI | `app.py`, `viz.py` | Streamlit multi-page app, matplotlib/NetworkX drawings |

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Run the experiments notebook with `jupyter notebook project_notebook.ipynb`, or the benchmark alone with `python benchmark.py`.

## Using the app
1. **Road Network** - load the sample city, generate a random one, upload a CSV (`from,to,weight`) or add intersections/roads by hand; view adjacency list and matrix.
2. **Route Planning** - pick source and destination to see the Dijkstra route, cost and all distance updates.
3. **Traffic Analysis** - choose roads, set a congestion factor (or close them) and compare the original and updated routes.
4. **Network Connectivity** - BFS/DFS traversal order and reachable intersections.
5. **Infrastructure Planning** - Prim and Kruskal MST with total cost.
6. **Comparative Analysis** - run the benchmark tables and charts.

## Repository layout
```
app.py  route_planner.py  traffic_analysis.py  connectivity_module.py  mst_planner.py
network_model.py  benchmark.py  viz.py  project_notebook.ipynb
requirements.txt  .gitignore  screenshots/  Final_Project_Report.docx
```

## Complexity summary
| Algorithm | Time | Notes |
|---|---|---|
| Dijkstra (heap) | O((V+E) log V) | non-negative weights |
| Bellman-Ford | O(V·E) | handles negative weights, detects negative cycles |
| BFS / DFS | O(V+E) | |
| Prim (heap) | O(E log V) | |
| Kruskal | O(E log E) | |

## References
- Cormen, Leiserson, Rivest, Stein - *Introduction to Algorithms*
- Kleinberg and Tardos - *Algorithm Design*
- NetworkX, Streamlit and Python documentation
