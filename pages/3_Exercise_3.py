"""Exercise 3 — Graphs & Graph Traversal (Singapore MRT theme).

A guided visualizer that teaches:
  • how a graph works — vertices, edges, adjacency (stations, lines, connections);
  • BFS with a QUEUE and DFS with a STACK, stepped one frontier-operation at a time;
  • the initial network map, the evolving frontier / visited set / visit order,
    and the eventual BFS & DFS spanning trees — all drawn with st.graphviz_chart.
"""
import pandas as pd
import streamlit as st

from Models.Graph import build_mrt_graph, edge_lines, bfs, dfs, DEFAULT_START
from Utilities.TransitView import (
    network_dot, spanning_tree_dot, traversal_node_states,
    frontier_html, order_html, visited_html, legend_html,
)

st.set_page_config(page_title="Exercise 3 — MRT Graph Traversal", layout="wide")

GRAPH = build_mrt_graph()
EDGE_LINES = edge_lines()

BFS_CODE = """def bfs(graph, start):
    queue = deque([start])        # the frontier (FIFO)
    visited = {start}
    while queue:
        v = queue.popleft()       # take from the FRONT
        for u in graph.neighbors(v):
            if u not in visited:
                visited.add(u)
                queue.append(u)   # add to the BACK"""

DFS_CODE = """def dfs(graph, start):
    stack = [start]               # the frontier (LIFO)
    visited = set()
    while stack:
        v = stack.pop()           # take from the TOP
        if v in visited:
            continue
        visited.add(v)
        for u in graph.neighbors(v):
            if u not in visited:
                stack.append(u)   # push onto the TOP"""


# ── Step-through control (slider + prev/next, all via session_state) ─────────
def _bump(step_key, delta, n):
    st.session_state[step_key] = max(0, min(st.session_state.get(step_key, 0) + delta, n - 1))


def step_controls(algo_key, n):
    step_key = f"{algo_key}_step"
    st.session_state.setdefault(step_key, 0)
    st.session_state[step_key] = max(0, min(st.session_state[step_key], n - 1))  # clamp
    c_prev, c_slider, c_next = st.columns([1, 6, 1])
    c_prev.button("◀ Prev", key=f"{algo_key}_prev", on_click=_bump,
                  args=(step_key, -1, n), use_container_width=True,
                  disabled=st.session_state[step_key] == 0)
    c_next.button("Next ▶", key=f"{algo_key}_next", on_click=_bump,
                  args=(step_key, +1, n), use_container_width=True,
                  disabled=st.session_state[step_key] == n - 1)
    if n > 1:
        with c_slider:
            st.slider("Step", min_value=0, max_value=n - 1, key=step_key,
                      label_visibility="collapsed")
    return st.session_state[step_key]


def render_traversal(algo_key, result, kind, tree_accent):
    steps = result["steps"]
    n = len(steps)
    idx = step_controls(algo_key, n)
    step = steps[idx]

    st.caption(f"**Step {idx + 1} of {n}**")
    st.info(step["note"])

    # Graph coloured by state, with the spanning tree grown so far bolded.
    states = traversal_node_states(GRAPH.vertices, step)
    st.graphviz_chart(
        network_dot(GRAPH, EDGE_LINES, node_states=states, tree_edges=step["tree_edges"]),
        use_container_width=True,
    )

    # Frontier + bookkeeping, using the shared chip style.
    st.markdown(frontier_html(step["frontier"], step["added"], kind), unsafe_allow_html=True)
    col_order, col_visited = st.columns(2)
    with col_order:
        st.markdown(order_html(step["order"]), unsafe_allow_html=True)
    with col_visited:
        st.markdown(visited_html(step["visited"]), unsafe_allow_html=True)

    # The eventual spanning tree (always the FINAL result).
    st.divider()
    st.markdown("#### 🌳 Spanning tree (final result)")
    st.caption(
        "The edges actually used to *discover* each station form a tree rooted at "
        "the start. Node badges show the visit order (#k)."
    )
    st.graphviz_chart(
        spanning_tree_dot(result["tree_edges"], result["order"], result["order"][0], tree_accent),
        use_container_width=True,
    )


# ── Page ──────────────────────────────────────────────────────────────────────
def main():
    st.title("Exercise 3 — Graphs & Graph Traversal 🚇")
    st.write(
        "Ride the Singapore MRT to learn **graphs**. Each **station** is a "
        "*vertex*; two stations are joined by an **edge** when a train runs "
        "directly between them. We'll explore the map with the two classic "
        "traversals: **BFS** (a queue) and **DFS** (a stack)."
    )

    # ── (a) How a graph works ─────────────────────────────────────────────────
    with st.expander("📘 How does a graph work? (vertices, edges, adjacency)", expanded=True):
        st.markdown(
            "- **Vertex (node):** a point in the network → here, an **MRT station**.\n"
            "- **Edge (link):** a connection between two vertices → a **direct train hop** "
            "between adjacent stations.\n"
            "- **Adjacency:** two vertices are *adjacent* (neighbours) if an edge joins "
            "them. A station's neighbours are simply the stops one hop away.\n"
            "- **Interchange:** a station on ≥ 2 lines has many neighbours (high **degree**) "
            "— these create the *cycles* that make BFS and DFS diverge.\n\n"
            "This mini-map has **12 stations** and **17 connections**. We visit a station's "
            "neighbours in **alphabetical order** so every run is predictable."
        )
        adj = pd.DataFrame(
            [
                {"Station": v, "Neighbours (adjacent stations)": ", ".join(GRAPH.neighbors(v)),
                 "Degree": GRAPH.degree(v)}
                for v in GRAPH.vertices
            ]
        )
        st.dataframe(adj, use_container_width=True, hide_index=True)

    # ── (c) The initial network map (collapsed by default) ────────────────────
    with st.expander("🗺️ The network map", expanded=False):
        st.markdown(legend_html(), unsafe_allow_html=True)
        st.caption(
            "Edges are coloured by MRT line; **shaded stations are interchanges** "
            "(degree ≥ 3). Scroll to zoom, drag to pan. *(Schematic — not to geographic scale.)*"
        )
        st.graphviz_chart(network_dot(GRAPH, EDGE_LINES), use_container_width=True)

    # ── Start station (shared by both traversals) ─────────────────────────────
    st.subheader("Run a traversal")
    start = st.selectbox(
        "Start station", GRAPH.vertices,
        index=GRAPH.vertices.index(DEFAULT_START),
        help="Where the traversal begins — the root of the spanning tree.",
    )
    # Reset both step counters whenever the start station changes.
    if st.session_state.get("mrt_start_prev") != start:
        st.session_state["mrt_start_prev"] = start
        st.session_state["bfs_step"] = 0
        st.session_state["dfs_step"] = 0

    bfs_result = bfs(GRAPH, start)
    dfs_result = dfs(GRAPH, start)

    tab_bfs, tab_dfs, tab_compare = st.tabs(
        ["🟠 BFS — Queue (FIFO)", "🔵 DFS — Stack (LIFO)", "⚖️ BFS vs DFS"]
    )

    # ── (b) BFS with a queue ──────────────────────────────────────────────────
    with tab_bfs:
        st.markdown(
            "**Breadth-First Search** explores the map in *rings*: all stations one hop "
            "from the start, then two hops, and so on. It uses a **queue** — first in, "
            "first out — so the earliest-discovered station is expanded first."
        )
        st.code(BFS_CODE, language="python")
        st.markdown(
            f"Starting at **{start}**, step through each dequeue and watch neighbours "
            "join the **back** of the queue 👇"
        )
        render_traversal("bfs", bfs_result, kind="queue", tree_accent="#fa9e0d")

    # ── (b) DFS with a stack ──────────────────────────────────────────────────
    with tab_dfs:
        st.markdown(
            "**Depth-First Search** plunges as *deep* as it can down one path, then "
            "**backtracks**. It uses a **stack** — last in, first out — so the most "
            "recently discovered station is expanded next."
        )
        st.code(DFS_CODE, language="python")
        st.markdown(
            f"Starting at **{start}**, step through each pop and watch neighbours get "
            "**pushed** on top of the stack 👇"
        )
        render_traversal("dfs", dfs_result, kind="stack", tree_accent="#005ec4")

    # ── BFS vs DFS: concepts, complexity, and when to use each ────────────────
    with tab_compare:
        st.markdown(
            "Same graph, same start — **different frontier, different tree.** Both are "
            "**Week 6** traversals that visit every vertex exactly once; the data structure "
            "they use is what changes *the order* they explore in."
        )

        st.markdown("#### Core concepts (DDW)")
        st.markdown(
            "- **Vertex colours** track each station's state: **white** (undiscovered) → "
            "**grey** (discovered, waiting in the frontier) → **black** (finished). The maps "
            "in the other tabs draw these as **grey → amber → green**.\n"
            "- **BFS** records a **distance `d`** (fewest hops from the start) and a "
            "**predecessor** for every vertex, so its tree gives the **shortest path** in an "
            "unweighted graph.\n"
            "- **DFS** stamps a **discovery time `d`** and a **finish time `f`** on each vertex "
            "(the *parenthesis structure*) — the basis for topological sort, cycle detection "
            "and finding connected components."
        )

        st.markdown("#### Side-by-side")
        st.markdown(
            "| | **BFS** — Breadth-First | **DFS** — Depth-First |\n"
            "|---|---|---|\n"
            "| Frontier | **Queue** (FIFO) | **Stack** (LIFO) |\n"
            "| Explores | level by level, **nearest first** | one branch **deep**, then backtracks |\n"
            "| Tree shape | short & **bushy** | long & **deep** |\n"
            "| Bookkeeping | distance `d` + predecessor | discovery / finish `d` / `f` |\n"
            "| **Time** | **O(V + E)** | **O(V + E)** |\n"
            "| **Space** (frontier) | O(V) — the widest level | O(V) — the longest path / recursion depth |\n"
            "| Shortest path (unweighted)? | ✅ **yes** (fewest hops) | ❌ not guaranteed |"
        )
        st.caption(
            f"This map has **V = {len(GRAPH.vertices)}** stations and **E = {len(GRAPH.edges)}** "
            "connections, and each vertex/edge is touched once — so both run in **O(V + E)**, "
            "the *same asymptotic speed*. They differ in **memory shape**: BFS's queue swells "
            "on **wide/bushy** graphs (it holds a whole level at once), while DFS's stack grows "
            "on **deep** graphs (the current path). Which one reaches a *specific* target sooner "
            "depends on where it sits — BFS finds nearby targets fast; DFS can plunge to a deep "
            "one quickly but may wander first."
        )

        st.markdown("#### When to use which")
        use_bfs, use_dfs = st.columns(2)
        with use_bfs:
            st.markdown("**🟠 Reach for BFS when…**")
            st.markdown(
                "- You need the **fewest-stops route** between two stations (shortest path in "
                "an unweighted graph).\n"
                "- You want **everything within *k* hops** — e.g. *stations ≤ 2 stops from "
                "Dhoby Ghaut*.\n"
                "- **Nearest-first** matters: degrees of separation, a web crawler visiting the "
                "closest pages first, level-by-level broadcasting."
            )
        with use_dfs:
            st.markdown("**🔵 Reach for DFS when…**")
            st.markdown(
                "- You only need to know **whether a path exists / what's reachable** from a "
                "station.\n"
                "- **Cycle detection** — does the network contain a loop (e.g. the Circle "
                "Line)? — or splitting it into **connected components**.\n"
                "- **Ordering with dependencies** (topological sort) or **backtracking** search: "
                "maze / route solving, fully exploring one option before trying the next."
            )

        st.divider()
        st.markdown("#### The two spanning trees, side by side")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**BFS visit order** — short & bushy")
            st.markdown(order_html(bfs_result["order"]), unsafe_allow_html=True)
            st.graphviz_chart(
                spanning_tree_dot(bfs_result["tree_edges"], bfs_result["order"], start, "#fa9e0d"),
                use_container_width=True,
            )
        with c2:
            st.markdown("**DFS visit order** — long & deep")
            st.markdown(order_html(dfs_result["order"]), unsafe_allow_html=True)
            st.graphviz_chart(
                spanning_tree_dot(dfs_result["tree_edges"], dfs_result["order"], start, "#005ec4"),
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
