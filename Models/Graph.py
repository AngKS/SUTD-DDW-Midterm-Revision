"""Graph model + BFS/DFS traversal traces for Exercise 3 (MRT theme).

Pure data/logic — no Streamlit — so BFS and DFS are unit-testable. The MRT map
is a deliberately small, connected subgraph of Singapore's rail network. Stations
are **vertices**; two stations are joined by an **edge** when they are adjacent
stops along a real MRT line (intermediate stops are contracted away). Interchange
stations give the graph cycles, which is what makes BFS and DFS produce visibly
different spanning trees.

BFS is implemented with a **queue** (FIFO) and DFS with a **stack** (LIFO). Both
record a step-by-step trace of the frontier, the visited set, the visit order and
the spanning-tree edges discovered so far, so the page can animate them.
"""
from collections import deque


class Graph:
    """A simple undirected graph backed by an adjacency map (insertion-ordered)."""

    def __init__(self):
        self._adj = {}

    def add_vertex(self, v):
        self._adj.setdefault(v, [])

    def add_edge(self, u, v):
        self.add_vertex(u)
        self.add_vertex(v)
        if v not in self._adj[u]:
            self._adj[u].append(v)
        if u not in self._adj[v]:
            self._adj[v].append(u)

    def neighbors(self, v):
        """Neighbours of ``v`` in a fixed, teachable order (alphabetical)."""
        return sorted(self._adj[v])

    @property
    def vertices(self):
        return sorted(self._adj)

    @property
    def edges(self):
        """Each undirected edge once, as a sorted ``(u, v)`` tuple."""
        seen = set()
        for u in self._adj:
            for v in self._adj[u]:
                seen.add(tuple(sorted((u, v))))
        return sorted(seen)

    def degree(self, v):
        return len(self._adj[v])


# ── Singapore MRT subgraph ───────────────────────────────────────────────────
# Official line colours (used for edge colouring in the map).
LINE_COLORS = {
    "NSL": "#d42e12",   # North-South   (red)
    "EWL": "#009645",   # East-West     (green)
    "NEL": "#9900aa",   # North-East    (purple)
    "CCL": "#fa9e0d",   # Circle        (orange)
    "DTL": "#005ec4",   # Downtown      (blue)
}

# Rough west→east (x) / south→north (y) positions, used as neato layout hints so
# the schematic resembles the real map.
MRT_STATIONS = {
    "Jurong East":     (0.5, 6.0),
    "Bishan":          (5.5, 8.5),
    "Botanic Gardens": (3.8, 6.8),
    "Buona Vista":     (2.2, 3.5),
    "HarbourFront":    (3.5, 1.0),
    "Outram Park":     (4.6, 2.6),
    "Chinatown":       (5.2, 3.4),
    "Serangoon":       (7.2, 7.8),
    "Dhoby Ghaut":     (5.6, 5.0),
    "City Hall":       (6.6, 4.0),
    "Raffles Place":   (6.4, 2.9),
    "Marina Bay":      (7.0, 1.8),
}

# (station A, station B, [lines serving that hop]). Each is a real adjacency
# between the chosen hub stations along the named line(s).
MRT_EDGES = [
    ("Jurong East",     "Buona Vista",     ["EWL"]),
    ("Buona Vista",     "Outram Park",     ["EWL"]),
    ("Outram Park",     "Raffles Place",   ["EWL"]),
    ("Raffles Place",   "City Hall",       ["EWL", "NSL"]),
    ("Jurong East",     "Bishan",          ["NSL"]),
    ("Bishan",          "Dhoby Ghaut",     ["NSL"]),
    ("Dhoby Ghaut",     "City Hall",       ["NSL"]),
    ("Raffles Place",   "Marina Bay",      ["NSL"]),
    ("HarbourFront",    "Outram Park",     ["NEL"]),
    ("Outram Park",     "Chinatown",       ["NEL"]),
    ("Chinatown",       "Dhoby Ghaut",     ["NEL"]),
    ("Dhoby Ghaut",     "Serangoon",       ["NEL"]),
    ("HarbourFront",    "Buona Vista",     ["CCL"]),
    ("Buona Vista",     "Botanic Gardens", ["CCL"]),
    ("Botanic Gardens", "Bishan",          ["CCL"]),
    ("Bishan",          "Serangoon",       ["CCL"]),
    ("Serangoon",       "Dhoby Ghaut",     ["CCL"]),
    ("Botanic Gardens", "Chinatown",       ["DTL"]),
]

DEFAULT_START = "Jurong East"


def build_mrt_graph():
    """Return the MRT subgraph as a :class:`Graph`."""
    g = Graph()
    for name in MRT_STATIONS:
        g.add_vertex(name)
    for u, v, _lines in MRT_EDGES:
        g.add_edge(u, v)
    return g


def edge_lines():
    """Map of ``frozenset({u, v}) -> [line codes]`` for edge colouring."""
    return {frozenset((u, v)): lines for u, v, lines in MRT_EDGES}


# ── Traversal traces ─────────────────────────────────────────────────────────
def _snapshot(action, current, frontier, visited, order, tree_edges, added, note):
    """One immutable step of a traversal, as plain copyable data."""
    return {
        "action": action,          # "init" | "visit" | "skip"
        "current": current,        # node dequeued/popped this step (None on init)
        "frontier": list(frontier),
        "visited": list(visited),
        "order": list(order),
        "tree_edges": list(tree_edges),
        "added": list(added),      # enqueued (BFS) / pushed (DFS) this step
        "note": note,
    }


def bfs(graph, start):
    """Breadth-first search using a **queue** (FIFO).

    Nodes are marked visited when **enqueued** (so each is queued at most once).
    The queue is displayed front→back: the next node out is at the FRONT (left).
    """
    visited = {start}
    parent = {start: None}
    queue = deque([start])
    order = []
    tree_edges = []
    steps = [_snapshot(
        "init", None, queue, visited, order, tree_edges, [start],
        f"Enqueue the start station **{start}** and mark it visited. "
        f"The queue is our frontier — BFS always takes from the FRONT.",
    )]

    while queue:
        v = queue.popleft()
        order.append(v)
        added = []
        for u in graph.neighbors(v):
            if u not in visited:
                visited.add(u)
                parent[u] = v
                queue.append(u)
                tree_edges.append((v, u))
                added.append(u)
        if added:
            note = (f"Dequeue **{v}** (front) and visit it. Its unvisited neighbours "
                    f"**{', '.join(added)}** are enqueued to the BACK and marked visited.")
        else:
            note = (f"Dequeue **{v}** (front) and visit it. All its neighbours are "
                    f"already visited, so nothing new is enqueued.")
        steps.append(_snapshot("visit", v, queue, visited, order, tree_edges, added, note))

    return {"order": order, "parent": parent, "tree_edges": tree_edges, "steps": steps}


def dfs(graph, start):
    """Depth-first search using a **stack** (LIFO).

    Nodes are marked visited when **popped** (textbook iterative DFS). A node can
    sit on the stack more than once; when a popped node was already visited we
    simply skip it. The stack is displayed bottom→top: the next node out is on
    TOP (right). Neighbours are pushed in reverse-alphabetical order so the
    alphabetically-first neighbour ends up on top and is explored next.
    """
    parents = {}                      # final parent once a node is visited
    visited = set()
    order = []
    tree_edges = []
    # Stack of (node, parent) so each DFS tree edge is unambiguous.
    stack = [(start, None)]
    steps = [_snapshot(
        "init", None, [start], visited, order, tree_edges, [start],
        f"Push the start station **{start}** onto the stack. "
        f"The stack is our frontier — DFS always takes from the TOP.",
    )]

    while stack:
        v, par = stack.pop()
        frontier_nodes = [node for node, _ in stack]
        if v in visited:
            steps.append(_snapshot(
                "skip", v, frontier_nodes, visited, order, tree_edges, [],
                f"Pop **{v}** — but it was already visited, so we skip it and pop again.",
            ))
            continue
        visited.add(v)
        parents[v] = par
        order.append(v)
        if par is not None:
            tree_edges.append((par, v))
        added = []
        for u in reversed(graph.neighbors(v)):
            if u not in visited:
                stack.append((u, v))
                added.append(u)
        added_display = list(reversed(added))   # show in the order they'll come off
        frontier_nodes = [node for node, _ in stack]
        if added_display:
            note = (f"Pop **{v}** (top) and visit it. Push its unvisited neighbours "
                    f"**{', '.join(added_display)}** — the last pushed sits on top and "
                    f"is explored next (that's what makes DFS go deep).")
        else:
            note = (f"Pop **{v}** (top) and visit it. It has no unvisited neighbours, "
                    f"so we backtrack by popping the next node on the stack.")
        steps.append(_snapshot("visit", v, frontier_nodes, visited, order,
                               tree_edges, added_display, note))

    return {"order": order, "parent": parents, "tree_edges": tree_edges, "steps": steps}


def traverse(graph, start, algorithm):
    """Dispatch to :func:`bfs` or :func:`dfs` by name ('BFS' or 'DFS')."""
    return bfs(graph, start) if algorithm.upper() == "BFS" else dfs(graph, start)
