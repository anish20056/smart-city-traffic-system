"""Smart City Traffic Management & Route Optimization System (Streamlit UI).
Run:  streamlit run app.py
"""
import pandas as pd
import streamlit as st

from network_model import RoadNetwork, INF
from route_planner import dijkstra
from traffic_analysis import bellman_ford, apply_congestion, compare_routes
from connectivity_module import bfs, dfs, unreachable_from, connected_components
from mst_planner import prim, kruskal
from benchmark import run_benchmarks
from viz import draw_network, layout, BLUE

st.set_page_config(page_title="Smart City Traffic System", page_icon="🚦", layout="wide")

if "net" not in st.session_state:
    st.session_state.net = RoadNetwork.sample_city()
net: RoadNetwork = st.session_state.net


def flash(msg, kind="success"):
    st.session_state.flash = (kind, msg)
    st.rerun()


def show_flash():
    if "flash" in st.session_state:
        kind, msg = st.session_state.pop("flash")
        getattr(st, kind)(msg)


def show(fig):
    st.pyplot(fig, clear_figure=True)


def road_label(e):
    return f"{e[0]} — {e[1]} ({e[2]:g})"


def pick_trip(key):
    nodes = sorted(net.nodes())
    c1, c2 = st.columns(2)
    d_src = nodes.index("Airport") if "Airport" in nodes else 0
    d_dst = nodes.index("Harbor") if "Harbor" in nodes else len(nodes) - 1
    src = c1.selectbox("Source", nodes, index=d_src, key=f"{key}_s")
    dst = c2.selectbox("Destination", nodes, index=d_dst, key=f"{key}_d")
    return src, dst


# ------------------------------------------------------------------ pages
def page_network():
    st.header("🏙️ Road Network Modeling")
    show_flash()
    with st.expander("Create or load a city road network", expanded=False):
        c1, c2, c3 = st.columns(3)
        if c1.button("Load sample city (12 intersections)"):
            st.session_state.net = RoadNetwork.sample_city()
            flash("Sample city loaded.")
        n = c2.number_input("Random network size", 5, 200, 25)
        if c2.button("Generate random network"):
            st.session_state.net = RoadNetwork.random(int(n), seed=int(n))
            flash(f"Random network with {int(n)} intersections created.")
        up = c3.file_uploader("Load CSV (from,to,weight)", type="csv")
        if up is not None and c3.button("Use uploaded CSV"):
            try:
                st.session_state.net = RoadNetwork.from_edge_df(pd.read_csv(up))
                flash("CSV network loaded.")
            except Exception as e:
                st.error(f"Could not load CSV: {e}")
        if st.button("Start with an empty network"):
            st.session_state.net = RoadNetwork()
            flash("Empty network created. Add intersections and roads below.", "info")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Add intersection")
        name = st.text_input("Intersection name", key="new_node")
        if st.button("Add intersection"):
            try:
                net.add_intersection(name)
                flash(f"Intersection '{name}' added.")
            except ValueError as e:
                st.error(str(e))
    with c2:
        st.subheader("Add road")
        nodes = sorted(net.nodes())
        if len(nodes) < 2:
            st.info("Add at least two intersections first (or type new names below).")
        a = st.text_input("From", value=nodes[0] if nodes else "", key="r_from")
        b = st.text_input("To", value=nodes[-1] if nodes else "", key="r_to")
        w = st.number_input("Travel cost (minutes / km)", min_value=0.1, value=5.0, step=0.5)
        if st.button("Add road"):
            try:
                net.add_road(a, b, w)
                flash(f"Road {a} — {b} added with cost {w:g}.")
            except ValueError as e:
                st.error(str(e))

    st.subheader("Network view")
    if net.num_nodes:
        show(draw_network(net, title=f"{net.num_nodes} intersections, {net.num_edges} roads", figsize=(9, 5.5)))
        t1, t2, t3 = st.tabs(["Adjacency list", "Adjacency matrix", "Roads table"])
        t1.code(net.adjacency_list_text())
        t2.dataframe(net.adjacency_matrix(), width="stretch")
        t2.caption("0 on the diagonal, ∞ = no direct road.")
        t3.dataframe(net.to_edge_df(), width="stretch")
        t3.download_button("Download roads CSV", net.to_edge_df().to_csv(index=False), "roads.csv")
    else:
        st.info("The network is empty.")


def page_route():
    st.header("🧭 Route Planning (Dijkstra)")
    if net.num_nodes < 2:
        return st.warning("Create a network with at least two intersections first.")
    src, dst = pick_trip("route")
    res = dijkstra(net, src, dst)
    if not res.found:
        return st.error(f"No route exists from {src} to {dst}.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total travel cost", f"{res.cost:g}")
    c2.metric("Roads used", len(res.path) - 1)
    c3.metric("Distance updates", len(res.steps))
    st.success("**Shortest route:** " + "  →  ".join(res.path))
    left, right = st.columns([3, 2])
    with left:
        show(draw_network(net, path=res.path, title=f"Shortest route {src} → {dst}  (cost {res.cost:g})"))
    with right:
        st.subheader("Final shortest distances")
        d = pd.DataFrame({"Intersection": list(res.dist), "Distance from source": ["∞" if v == INF else f"{v:g}" for v in res.dist.values()]})
        st.dataframe(d, width="stretch", hide_index=True)
    st.subheader("Every intermediate distance update")
    st.dataframe(pd.DataFrame(res.steps), width="stretch", hide_index=True)


def page_traffic():
    st.header("🚧 Traffic Analysis (Bellman-Ford)")
    if net.num_edges < 1:
        return st.warning("Create a network with roads first.")
    src, dst = pick_trip("traffic")
    edges = sorted(net.undirected_edges())
    labels = {road_label(e): e for e in edges}
    default = [k for k in labels if k.startswith("Mall — Stadium") or k.startswith("Stadium — Mall")][:1]
    chosen = st.multiselect("Congested / closed roads", list(labels), default=default)
    c1, c2 = st.columns(2)
    factor = c1.slider("Congestion factor (× travel time)", 1.0, 10.0, 3.0, 0.5)
    close = c2.checkbox("Close these roads completely (accident / road closure)")
    roads = [labels[k][:2] for k in chosen]
    new_net = apply_congestion(net, roads, factor, close)

    before, after = bellman_ford(net, src, dst), bellman_ford(new_net, src, dst)
    if not before.found:
        return st.error("Source and destination are not connected in the original network.")
    cmp = compare_routes(before, after)
    if not after.found:
        st.error("After the change, the destination is unreachable.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Original cost", f"{cmp['original_cost']:g}")
        m2.metric("Updated cost", f"{cmp['updated_cost']:g}", f"{cmp['delta']:+g}", delta_color="inverse")
        m3.metric("Cost change", f"{cmp['pct']:+.1f}%")
        m4.metric("Route changed?", "Yes" if cmp["route_changed"] else "No")
        if cmp["route_changed"]:
            st.info("Congestion made a different route cheaper — traffic should be diverted.")
        else:
            st.info("The best route is unchanged; the delay is absorbed on the same roads.")
        st.table(pd.DataFrame({"Scenario": ["Original", "After congestion"],
                               "Route": [" → ".join(before.path), " → ".join(after.path)],
                               "Cost": [before.cost, after.cost]}))
    pos = layout(net)
    l, r = st.columns(2)
    with l:
        show(draw_network(net, pos, path=before.path, title="Original route"))
    with r:
        show(draw_network(new_net, pos, path=after.path, color="#F58518", title="Route after congestion"))
    e1, e2 = st.expander("Bellman-Ford relaxations — original network"), st.expander("Bellman-Ford relaxations — after congestion")
    e1.dataframe(pd.DataFrame(before.steps), width="stretch", hide_index=True)
    e2.dataframe(pd.DataFrame(after.steps), width="stretch", hide_index=True)


def page_connectivity():
    st.header("🔗 Network Connectivity (BFS / DFS)")
    if not net.num_nodes:
        return st.warning("The network is empty.")
    start = st.selectbox("Starting intersection", sorted(net.nodes()))
    b, d = bfs(net, start), dfs(net, start)
    pos = layout(net)
    c1, c2 = st.columns(2)
    for col, name, r in ((c1, "BFS", b), (c2, "DFS", d)):
        with col:
            st.subheader(name)
            st.write("**Traversal order:** " + " → ".join(r["order"]))
            miss = unreachable_from(net, start, r)
            st.write(f"**Reachable:** {len(r['reachable'])} of {net.num_nodes} intersections")
            if miss:
                st.warning("Unreachable: " + ", ".join(miss))
            show(draw_network(net, pos, order=r["order"], title=f"{name} from {start}", figsize=(6, 4.5)))
    st.caption(f"The network has {len(connected_components(net))} connected region(s).")


def page_mst():
    st.header("🏗️ Infrastructure Planning (MST)")
    if net.num_nodes < 2:
        return st.warning("Create a network first.")
    start = st.selectbox("Prim start intersection", sorted(net.nodes()))
    p, k = prim(net, start), kruskal(net)
    if not p["spanning"]:
        st.warning("The network is disconnected, so the result is a minimum spanning forest.")
    pos = layout(net)
    c1, c2 = st.columns(2)
    for col, name, r in ((c1, "Prim", p), (c2, "Kruskal", k)):
        with col:
            st.subheader(name)
            st.metric("Total infrastructure cost", f"{r['total']:g}")
            st.dataframe(pd.DataFrame(r["edges"], columns=["From", "To", "Cost"]), width="stretch", hide_index=True)
            show(draw_network(net, pos, edges=r["edges"], color="#54A24B", title=f"{name} MST (cost {r['total']:g})", figsize=(6, 4.5)))
    st.success("Both algorithms give the same total cost." if abs(p["total"] - k["total"]) < 1e-9 else "Totals differ — check the network.")
    with st.expander("Algorithm steps"):
        st.write("**Prim**"); st.dataframe(pd.DataFrame(p["steps"]), hide_index=True, width="stretch")
        st.write("**Kruskal**"); st.dataframe(pd.DataFrame(k["steps"]), hide_index=True, width="stretch")


def page_compare():
    st.header("📊 Comparative Analysis")
    sizes = st.multiselect("Network sizes (intersections)", [10, 25, 50, 100, 200], default=[10, 25, 50, 100])
    reps = st.slider("Repetitions per measurement", 5, 100, 30)
    if st.button("Run experiments") and sizes:
        with st.spinner("Benchmarking..."):
            st.session_state.bench = run_benchmarks(sorted(sizes), reps)
    if "bench" not in st.session_state:
        return st.info("Press **Run experiments** to generate the comparison tables.")
    for name, df in st.session_state.bench.items():
        st.subheader(name)
        st.dataframe(df.round(4), width="stretch", hide_index=True)
        tcols = [c for c in df.columns if c.endswith("time (ms)")]
        st.line_chart(df.set_index("Intersections")[tcols])
    st.markdown("""
**Suitability for traffic management**
- **Dijkstra** is the best fit for live navigation (fast, non-negative travel times). **Bellman-Ford** is slower but robust and useful for re-checking after weight changes.
- **BFS** finds the fewest-road reachability layers; **DFS** is lightweight for exploring accessibility. Both are O(V + E).
- **Prim** suits dense networks, **Kruskal** suits sparse road maps; both give the same minimum cost.
""")


PAGES = {"Road Network": page_network, "Route Planning": page_route, "Traffic Analysis": page_traffic,
         "Network Connectivity": page_connectivity, "Infrastructure Planning": page_mst,
         "Comparative Analysis": page_compare}

st.sidebar.title("🚦 Smart City Traffic")
choice = st.sidebar.radio("Module", list(PAGES))
st.sidebar.metric("Intersections", net.num_nodes)
st.sidebar.metric("Roads", net.num_edges)
PAGES[choice]()
