"""Graphviz DOT builders + frontier/visited render helpers for Exercise 3.

Kept separate from ``Models/Graph.py`` (which stays pure topology/logic) so the
page renderer is generic. Reuses the sort-visualizer palette and the ``_box`` /
``_row`` chip helpers from :mod:`Utilities.GraphView` so the MRT view shares the
project's existing visual language.
"""
from Models.Graph import MRT_STATIONS, LINE_COLORS
from Utilities.GraphView import _box, _row, _COLORS

# Full MRT line names for the legend.
LINE_NAMES = {
    "NSL": "North-South", "EWL": "East-West", "NEL": "North-East",
    "CCL": "Circle", "DTL": "Downtown",
}

# Traversal-state node styling: (fill, font). Mirrors the sort views' red/green.
STATE_STYLE = {
    "unvisited": ("#eceff1", "#37474f"),
    "frontier":  ("#ef9a3d", "#ffffff"),   # amber — discovered, waiting in the frontier
    "visited":   ("#2e7d32", "#ffffff"),   # green — processed
    "current":   ("#c62828", "#ffffff"),   # red   — being processed this step
}


def traversal_node_states(vertices, step):
    """Map every vertex → state string from a traversal ``step`` snapshot."""
    order_set = set(step["order"])
    frontier_set = set(step["frontier"])
    current = step["current"]
    states = {}
    for v in vertices:
        if v == current:
            states[v] = "current"
        elif v in order_set:
            states[v] = "visited"
        elif v in frontier_set:
            states[v] = "frontier"
        else:
            states[v] = "unvisited"
    return states


def network_dot(graph, edge_line_map, node_states=None, tree_edges=None):
    """Build the MRT map as a Graphviz DOT string.

    ``node_states`` None → the plain network map (interchanges highlighted, every
    edge drawn in its MRT line colour). Otherwise a traversal step: nodes coloured
    by state and the discovered spanning-tree edges (``tree_edges``) drawn bold in
    their line colour while the rest fade to grey.
    """
    tree_set = {frozenset(e) for e in (tree_edges or [])}
    out = [
        "graph MRT {",
        "  layout=neato; overlap=false; sep=\"+18\"; splines=true;",
        "  bgcolor=\"transparent\";",
        '  node [shape=box, style="rounded,filled", fontname="Helvetica",'
        ' fontsize=11, penwidth=1.4, margin="0.16,0.08"];',
        "  edge [penwidth=2];",
    ]
    for v in graph.vertices:
        x, y = MRT_STATIONS[v]
        pos = f"{x * 60:.0f},{y * 60:.0f}"
        if node_states is None:
            interchange = graph.degree(v) >= 3
            fill = "#cfe8ff" if interchange else "#ffffff"
            font, border = "#12324f", "#455a64"
        else:
            fill, font = STATE_STYLE[node_states.get(v, "unvisited")]
            border = "#111111" if node_states.get(v) == "current" else "#607d8b"
        out.append(f'  "{v}" [label="{v}", fillcolor="{fill}", '
                   f'fontcolor="{font}", color="{border}", pos="{pos}"];')
    for u, v in graph.edges:
        key = frozenset((u, v))
        codes = edge_line_map.get(key, [])
        colors = ":".join(LINE_COLORS.get(c, "#90a4ae") for c in codes) or "#90a4ae"
        if node_states is None:
            attrs = f'color="{colors}", penwidth=3'
        elif key in tree_set:
            attrs = f'color="{colors}", penwidth=4'
        else:
            attrs = 'color="#cfd8dc", penwidth=1.2'
        out.append(f'  "{u}" -- "{v}" [{attrs}];')
    out.append("}")
    return "\n".join(out)


def spanning_tree_dot(tree_edges, order, start, accent="#1565c0"):
    """Rooted spanning tree (dot engine, top-down). Nodes carry their visit rank."""
    rank = {n: i + 1 for i, n in enumerate(order)}
    nodes = {start}
    for p, c in tree_edges:
        nodes.add(p)
        nodes.add(c)
    out = [
        "digraph Tree {",
        "  rankdir=TB; bgcolor=\"transparent\"; nodesep=0.35; ranksep=0.5;",
        '  node [shape=box, style="rounded,filled", fontname="Helvetica",'
        ' fontsize=11, penwidth=1.4, color="#607d8b", margin="0.16,0.08"];',
        f'  edge [color="{accent}", penwidth=2, arrowsize=0.8];',
    ]
    for n in sorted(nodes):
        k = rank.get(n)
        klabel = f"\\n#{k}" if k else ""
        if n == start:
            fill, font = "#c62828", "#ffffff"
        else:
            fill, font = "#2e7d32", "#ffffff"
        out.append(f'  "{n}" [label="{n}{klabel}", fillcolor="{fill}", fontcolor="{font}"];')
    for p, c in tree_edges:
        out.append(f'  "{p}" -> "{c}";')
    out.append("}")
    return "\n".join(out)


# ── Frontier / visited / order chips (reuse the sort-visualizer chip style) ──
def _empty(label):
    return _row(label, "<span style='color:#90a4ae;font-style:italic;'>empty</span>")


def frontier_html(nodes, added, kind):
    """Render the queue (kind='queue') or stack (kind='stack') as a row of chips.

    Newly enqueued/pushed nodes this step are outlined in red.
    """
    if kind == "queue":
        label = "Queue &nbsp;·&nbsp; front ⟵⟶ back &nbsp;·&nbsp; <b>dequeue from the FRONT (left)</b>"
    else:
        label = "Stack &nbsp;·&nbsp; bottom ⟵⟶ top &nbsp;·&nbsp; <b>pop from the TOP (right)</b>"
    if not nodes:
        return _empty(label)
    added_left = list(added)
    chips = []
    for n in nodes:
        just_added = n in added_left
        if just_added:
            added_left.remove(n)
        chips.append(_box(
            n,
            _COLORS["pending"] if just_added else _COLORS["left"],
            fg="#5d4037" if just_added else "#ffffff",
            border="#c62828" if just_added else None,
        ))
    return _row(label, "".join(chips))


def order_html(order):
    """Numbered visit-order chips (the traversal output)."""
    if not order:
        return _empty("Visit order (traversal output)")
    chips = "".join(_box(f"{i + 1}. {n}", _COLORS["written"]) for i, n in enumerate(order))
    return _row("Visit order (traversal output)", chips)


def visited_html(visited):
    """The visited/discovered set as green chips (order-independent)."""
    if not visited:
        return _empty("Visited / discovered set")
    chips = "".join(_box(n, _COLORS["written"]) for n in sorted(visited))
    return _row("Visited / discovered set", chips)


def legend_html():
    """Inline MRT line-colour legend."""
    swatches = []
    for code, color in LINE_COLORS.items():
        swatches.append(
            f"<span style='display:inline-block;width:14px;height:14px;border-radius:3px;"
            f"background:{color};vertical-align:middle;margin-right:4px;'></span>"
            f"<span style='font-size:13px;'>{LINE_NAMES[code]} ({code})</span>"
        )
    return ("<div style='display:flex;flex-wrap:wrap;gap:14px;margin:2px 0 4px;'>"
            + "".join(f"<span>{s}</span>" for s in swatches) + "</div>")
