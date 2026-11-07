"""Visualisation helpers (Task 9) - draw the road network and highlight results."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

BLUE, RED, GREEN, GREY = "#4C78A8", "#E45756", "#54A24B", "#B8B8B8"


def layout(net, seed=42):
    return nx.spring_layout(net.to_networkx(), seed=seed, k=1.6 / max(net.num_nodes, 1) ** 0.5)


def draw_network(net, pos=None, path=None, edges=None, order=None, title="",
                 color=RED, figsize=(7, 5), show_weights=None):
    """path   -> list of nodes to highlight as a route
       edges  -> list of (u, v[, w]) to highlight (e.g. MST roads)
       order  -> traversal order; nodes are numbered 1..k"""
    g = net.to_networkx()
    pos = pos or layout(net)
    fig, ax = plt.subplots(figsize=figsize)
    hl = set()
    if path:
        hl |= {frozenset(e) for e in zip(path, path[1:])}
    if edges:
        hl |= {frozenset(e[:2]) for e in edges}
    plain = [e for e in g.edges if frozenset(e) not in hl]
    marked = [e for e in g.edges if frozenset(e) in hl]
    nx.draw_networkx_edges(g, pos, edgelist=plain, edge_color=GREY, width=1.2, ax=ax)
    nx.draw_networkx_edges(g, pos, edgelist=marked, edge_color=color, width=3.5, ax=ax)

    colors = [BLUE] * g.number_of_nodes()
    nodes = list(g.nodes)
    if path:
        colors = [color if n in path else BLUE for n in nodes]
        for n, c in ((path[0], GREEN), (path[-1], "#F58518")):
            colors[nodes.index(n)] = c
    if order:
        colors = [GREEN if n == order[0] else BLUE for n in nodes]
    nx.draw_networkx_nodes(g, pos, node_color=colors, node_size=520 if g.number_of_nodes() <= 30 else 220, ax=ax)

    if g.number_of_nodes() <= 40:
        labels = {n: (f"{n}\n#{order.index(n) + 1}" if order and n in order else n) for n in nodes}
        lpos = {n: (x, y + 0.075) for n, (x, y) in pos.items()}
        nx.draw_networkx_labels(g, lpos, labels=labels, font_size=8, font_color="black", font_weight="bold", ax=ax)
    if show_weights is None:
        show_weights = g.number_of_edges() <= 40
    if show_weights:
        lbl = {(u, v): f"{d['weight']:g}" for u, v, d in g.edges(data=True)}
        nx.draw_networkx_edge_labels(g, pos, edge_labels=lbl, font_size=7, ax=ax)
    ax.set_title(title)
    ax.axis("off")
    fig.tight_layout()
    return fig
