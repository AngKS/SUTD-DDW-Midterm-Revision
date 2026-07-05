# ── Shared rendering helpers for the Streamlit array widgets ────────────────
# All graphviz/HTML view code lives here so Models/Algorithms.py stays focused
# on the sorting logic. Frames carry a ready-to-render "html" string (and an
# optional "graphviz" dot) so the page renderer stays generic across algorithms.
_COLORS = {
    "value":   "#1565c0",  # neutral array cell (blue)
    "left":    "#ef9a3d",  # left subarray (amber)
    "right":   "#1abc9c",  # right subarray (teal)
    "written": "#2e7d32",  # placed into sorted output (green)
    "pending": "#f5c98a",  # active merge window, not yet written (light amber)
    "empty":   "transparent",
}
_BOX = ("flex:0 0 auto;text-align:center;border-radius:6px;padding:6px 8px;"
        "margin:2px;font-size:13px;min-width:32px;")


def _box(value, bg, fg="#ffffff", index=None, dashed=False, dim=False, border=None):
    style = _BOX + f"background:{bg};color:{fg};"
    if dashed:
        style += "border:1px dashed #b0bec5;"
    if border:
        style += f"border:2px solid {border};"
    if dim:
        style += "opacity:.4;"
    idx = f"<br><small style='opacity:.7'>[{index}]</small>" if index is not None else ""
    val = "&nbsp;" if value is None else value
    return f"<div style='{style}'><b>{val}</b>{idx}</div>"


def _row(label, inner):
    return (f"<div style='margin:6px 0;'>"
            f"<div style='font-size:12px;color:#555;margin-bottom:2px;'>{label}</div>"
            f"<div style='display:flex;flex-wrap:wrap;align-items:flex-end;'>{inner}</div>"
            f"</div>")


# ── Bar chart (Bubble / Insertion default visualisation) ────────────────────
def bars_html(array, highlights, max_value, sorted_indices=()):
    # Horizontal bar chart as plain HTML divs (heights ∝ value). Compared /
    # swapped indices are red, locked-sorted indices green, the rest blue.
    # Lightweight so it auto-plays smoothly frame by frame, like the graphviz.
    sorted_set = set(sorted_indices)
    bars = []
    for index, value in enumerate(array):
        bar_height = max(4, round((value / max_value) * 200)) if max_value else 4
        if index in highlights:
            bar_color = "#c62828"
        elif index in sorted_set:
            bar_color = _COLORS["written"]
        else:
            bar_color = _COLORS["value"]
        bars.append(
            f"<div style='display:flex;flex-direction:column;align-items:center;"
            f"justify-content:flex-end;flex:0 0 auto;margin:0 1px;'>"
            f"<div style='font-size:10px;color:#555;'>{value}</div>"
            f"<div style='width:18px;height:{bar_height}px;background:{bar_color};"
            f"border-radius:3px 3px 0 0;'></div>"
            f"<div style='font-size:9px;color:#90a4ae;'>[{index}]</div>"
            f"</div>"
        )
    return (f"<div style='display:flex;flex-wrap:nowrap;align-items:flex-end;"
            f"overflow-x:auto;border-bottom:2px solid #ccc;padding-bottom:2px;'>"
            f"{''.join(bars)}</div>")


def sorted_row(array, sorted_set, label="Sorted"):
    # Accumulator row of locked elements (filled green) with empty dashed slots
    # for the not-yet-sorted positions — same idea as Heap's sorted output.
    cells = "".join(
        _box(value, _COLORS["written"], index=index) if index in sorted_set
        else _box(None, _COLORS["empty"], fg="#90a4ae", index=index, dashed=True)
        for index, value in enumerate(array)
    )
    return _row(label, cells)


def compare_phase(highlights):
    if len(highlights) >= 2:
        return f"Compare / swap indices {highlights[0]} & {highlights[1]}"
    if len(highlights) == 1:
        return f"Place value at index {highlights[0]}"
    return "Step"


# ── Heap Sort views (binary-tree graphviz + sorted-output row) ──────────────
def heap_dot(array, highlights, heap_size):
    # Render ONLY the live heap region [0, heap_size) as a complete binary
    # tree (child = 2i+1 / 2i+2). Extracted elements are gone from the tree
    # entirely — they move into the sorted-output array below. Active nodes
    # red, remaining heap blue.
    lines = [
        "digraph G {",
        '  node [shape=circle, style=filled, fontname="Helvetica", fontcolor="white"];',
    ]
    if heap_size == 0:
        lines.append('  empty [shape=plaintext, style="", fontcolor="#90a4ae", label="(heap empty)"];')
    for node in range(heap_size):
        color = "#e53935" if node in highlights else "#1e88e5"
        lines.append(f'  {node} [label="{array[node]}\\n[{node}]", fillcolor="{color}"];')
    for node in range(heap_size):
        for child in (2 * node + 1, 2 * node + 2):
            if child < heap_size:
                lines.append(f"  {node} -> {child};")
    lines.append("}")
    return "\n".join(lines)


def heap_output(state, heap_size):
    # Sorted-output row shown below the tree: positions [heap_size, n) hold
    # extracted maxes (heap sort locks them at the tail, already ascending);
    # positions still inside the heap are empty (None).
    return [state[index] if index >= heap_size else None for index in range(len(state))]


def heap_output_html(output):
    cells = "".join(
        _box(value, _COLORS["written"], index=index) if value is not None
        else _box(None, _COLORS["empty"], fg="#90a4ae", index=index, dashed=True)
        for index, value in enumerate(output)
    )
    return _row("Sorted output", cells)


def heap_frame(state, highlights, heap_size, phase):
    return {
        "phase": phase,
        "graphviz": heap_dot(state, highlights, heap_size),
        "html": heap_output_html(heap_output(state, heap_size)),
    }


# ── Merge Sort views (recursion-tree graphviz + working-array row) ──────────
def merge_dot(array, nodes, merged, active):
    # Render the recursion tree discovered so far. Each node is labelled
    # with its current slice array[node_start:node_end]; active node red,
    # merged green, pending blue. Children derived deterministically via
    # mid = (node_start + node_end) // 2.
    lines = [
        "digraph G {",
        "  graph [ordering=out];",
        '  node [shape=box, style="rounded,filled", fontname="Helvetica", fontcolor="white"];',
    ]
    for node_id, (node_start, node_end) in nodes.items():
        values = ", ".join(str(value) for value in array[node_start:node_end])
        label = f"[{node_start},{node_end})\\n{values}"
        if node_id == active:
            color = "#e53935"
        elif node_id in merged:
            color = "#43a047"
        else:
            color = "#1e88e5"
        lines.append(f'  "{node_id}" [label="{label}", fillcolor="{color}"];')
    for node_id, (node_start, node_end) in nodes.items():
        if node_end - node_start > 1:
            mid = (node_start + node_end) // 2
            for child_start, child_end in ((node_start, mid), (mid, node_end)):
                child_id = f"{child_start}_{child_end}"
                if child_id in nodes:
                    lines.append(f'  "{node_id}" -> "{child_id}";')
    lines.append("}")
    return "\n".join(lines)


def merge_array_html(array, active_range, write_index, completed):
    # Working-array row below the tree. Colours:
    #   red   = the cell being written this step (active merge cursor)
    #   green = sorted — either written-so-far within the active merge, or
    #           part of an already-completed merge outside the active window
    #   blue  = pending (not yet merged into a sorted run)
    range_start, range_end = active_range if active_range else (-1, -1)
    cells = []
    for index, value in enumerate(array):
        if write_index is not None and index == write_index:
            cell_color = "#c62828"
        elif active_range and range_start <= index < range_end:
            cell_color = _COLORS["written"] if (write_index is not None and index < write_index) else _COLORS["value"]
        else:
            cell_color = _COLORS["written"] if completed[index] else _COLORS["value"]
        cells.append(_box(value, cell_color, index=index))
    return _row("Array", "".join(cells))
