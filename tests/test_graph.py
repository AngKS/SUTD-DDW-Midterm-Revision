"""Correctness battery for the MRT graph model and BFS/DFS traversals."""
import pytest

from Models.Graph import (
    Graph, build_mrt_graph, edge_lines, bfs, dfs, traverse,
    MRT_STATIONS, MRT_EDGES, DEFAULT_START,
)

GRAPH = build_mrt_graph()


# ── Graph structure ──────────────────────────────────────────────────────────
def test_mrt_graph_shape():
    assert len(GRAPH.vertices) == 12
    assert len(GRAPH.edges) == 17          # de-duplicated undirected edges
    assert DEFAULT_START in GRAPH.vertices


def test_every_station_has_coordinates_and_line_metadata():
    for v in GRAPH.vertices:
        assert v in MRT_STATIONS
    lines = edge_lines()
    for u, v in GRAPH.edges:
        assert frozenset((u, v)) in lines and lines[frozenset((u, v))]


def test_edges_are_undirected_and_neighbours_sorted():
    for v in GRAPH.vertices:
        assert GRAPH.neighbors(v) == sorted(GRAPH.neighbors(v))
        for u in GRAPH.neighbors(v):
            assert v in GRAPH.neighbors(u)   # symmetry


def test_add_edge_is_idempotent_and_symmetric():
    g = Graph()
    g.add_edge("A", "B")
    g.add_edge("A", "B")                     # duplicate — must not double up
    g.add_edge("B", "A")
    assert g.neighbors("A") == ["B"]
    assert g.neighbors("B") == ["A"]
    assert g.degree("A") == 1


# ── Traversal correctness (holds from any start) ─────────────────────────────
@pytest.mark.parametrize("start", GRAPH.vertices)
@pytest.mark.parametrize("fn", [bfs, dfs])
def test_traversal_visits_every_vertex_once(fn, start):
    result = fn(GRAPH, start)
    order = result["order"]
    assert order[0] == start
    assert set(order) == set(GRAPH.vertices)         # connected → reaches all
    assert len(order) == len(set(order))             # each visited exactly once


@pytest.mark.parametrize("start", GRAPH.vertices)
@pytest.mark.parametrize("fn", [bfs, dfs])
def test_spanning_tree_is_valid(fn, start):
    result = fn(GRAPH, start)
    tree = result["tree_edges"]
    assert len(tree) == len(GRAPH.vertices) - 1      # tree over n nodes has n-1 edges
    real = set(GRAPH.edges)
    for u, v in tree:
        assert tuple(sorted((u, v))) in real         # every tree edge is a real edge
    # The tree spans all vertices and is acyclic (n-1 edges + spans all ⇒ tree).
    nodes = {start}
    for u, v in tree:
        nodes.add(u)
        nodes.add(v)
    assert nodes == set(GRAPH.vertices)


def _parent_chain(parent, node):
    chain = []
    while node is not None:
        chain.append(node)
        node = parent.get(node)
    return chain


@pytest.mark.parametrize("start", GRAPH.vertices)
def test_bfs_gives_shortest_hop_distances(start):
    result = bfs(GRAPH, start)
    parent = result["parent"]
    # Independent shortest-hop BFS to compare against.
    from collections import deque
    dist = {start: 0}
    q = deque([start])
    while q:
        v = q.popleft()
        for u in GRAPH.neighbors(v):
            if u not in dist:
                dist[u] = dist[v] + 1
                q.append(u)
    for v in GRAPH.vertices:
        assert len(_parent_chain(parent, v)) - 1 == dist[v]


@pytest.mark.parametrize("start", GRAPH.vertices)
def test_dfs_has_no_cross_edges(start):
    # On an undirected graph, every non-tree edge of a valid DFS must connect a
    # node to one of its ancestors (a "back edge") — never two separate branches.
    result = dfs(GRAPH, start)
    parent = result["parent"]
    tree = {frozenset(e) for e in result["tree_edges"]}

    def is_ancestor(a, d):
        return a in _parent_chain(parent, d)

    for u, v in GRAPH.edges:
        if frozenset((u, v)) in tree:
            continue
        assert is_ancestor(u, v) or is_ancestor(v, u), (u, v)


# ── Step traces ──────────────────────────────────────────────────────────────
def test_bfs_step_trace_structure():
    steps = bfs(GRAPH, DEFAULT_START)["steps"]
    assert steps[0]["action"] == "init"
    assert steps[0]["added"] == [DEFAULT_START]
    assert steps[-1]["frontier"] == []               # queue drains to empty
    for s in steps:
        assert {"action", "current", "frontier", "visited", "order",
                "tree_edges", "added", "note"} <= set(s)
    # Only "visit" steps carry a current node in BFS.
    assert all(s["current"] is not None for s in steps if s["action"] == "visit")


def test_dfs_skip_steps_are_already_visited():
    result = dfs(GRAPH, DEFAULT_START)
    steps = result["steps"]
    for s in steps:
        if s["action"] == "skip":
            # the popped node was visited before this pop
            assert s["current"] in s["visited"]
    assert steps[-1]["frontier"] == []


def test_traversals_are_deterministic():
    assert bfs(GRAPH, DEFAULT_START)["order"] == bfs(GRAPH, DEFAULT_START)["order"]
    assert dfs(GRAPH, DEFAULT_START)["order"] == dfs(GRAPH, DEFAULT_START)["order"]


def test_known_orders_from_jurong_east():
    # Regression lock: alphabetical neighbour order fixes these exactly.
    assert bfs(GRAPH, "Jurong East")["order"] == [
        "Jurong East", "Bishan", "Buona Vista", "Botanic Gardens", "Dhoby Ghaut",
        "Serangoon", "HarbourFront", "Outram Park", "Chinatown", "City Hall",
        "Raffles Place", "Marina Bay",
    ]
    assert dfs(GRAPH, "Jurong East")["order"] == [
        "Jurong East", "Bishan", "Botanic Gardens", "Buona Vista", "HarbourFront",
        "Outram Park", "Chinatown", "Dhoby Ghaut", "City Hall", "Raffles Place",
        "Marina Bay", "Serangoon",
    ]


def test_bfs_and_dfs_diverge():
    assert bfs(GRAPH, "Jurong East")["order"] != dfs(GRAPH, "Jurong East")["order"]


def test_traverse_dispatch():
    assert traverse(GRAPH, "Bishan", "BFS")["order"] == bfs(GRAPH, "Bishan")["order"]
    assert traverse(GRAPH, "Bishan", "dfs")["order"] == dfs(GRAPH, "Bishan")["order"]
