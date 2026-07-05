import time
import tracemalloc

import streamlit as st


def format_duration(seconds: float) -> str:
    """Human-readable wall-clock duration with an adaptive unit."""
    if seconds < 1e-6:
        return f"{seconds * 1e9:.0f} ns"
    if seconds < 1e-3:
        return f"{seconds * 1e6:.1f} µs"
    if seconds < 1.0:
        return f"{seconds * 1e3:.2f} ms"
    return f"{seconds:.2f} s"


def format_bytes(num_bytes: float) -> str:
    """Human-readable byte count with an adaptive binary unit."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            precision = 0 if unit == "B" else 1
            return f"{size:.{precision}f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def measure_sort(algo, array):
    """Run ``algo``'s pure ``sort`` generator on a copy of ``array`` and measure
    its runtime and peak extra memory.

    Only the algorithm itself is timed/traced — not the visualization frame
    building — so the numbers reflect the sort, not the rendering. Returns
    ``(elapsed_seconds, peak_bytes)``.
    """
    work = list(array)
    tracemalloc.start()
    start = time.perf_counter()
    try:
        for _ in algo.sort(work):
            pass
    finally:
        elapsed = time.perf_counter() - start
        _current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    return elapsed, peak


def render_sort_metrics(algo, elapsed=None, peak=None, live_runtime=False):
    """Draw the row of three native ``st.metric`` widgets for ``algo``.

    ``elapsed`` (seconds) and ``peak`` (bytes) come from ``measure_sort``; when
    omitted the corresponding subtitle is left blank.

    When ``live_runtime`` is True the runtime subtitle is rendered into an empty
    placeholder (seeded at 0) and that placeholder is **returned**, so the page
    can tick it upward via :func:`set_runtime_caption` while the visualization
    plays. Otherwise the final runtime is written statically and ``None`` is
    returned.
    """
    col_name, col_time, col_space = st.columns(3)

    with col_name:
        st.metric(label="Sort Algorithm", value=algo.name, help=algo.description)
        if algo.description:
            st.caption(algo.description)

    runtime_box = None
    with col_time:
        st.metric(
            label="Time Complexity",
            value=algo.t_complexity,
            help="Big-O time complexity. Subtitle is this run's measured runtime.",
        )
        if live_runtime:
            runtime_box = st.empty()
            set_runtime_caption(runtime_box, 0.0)   # start the counter at zero
        elif elapsed is not None:
            st.caption(f"Runtime: {format_duration(elapsed)}")

    with col_space:
        st.metric(
            label="Space Complexity",
            value=algo.s_complexity,
            help="Big-O auxiliary space. Subtitle is this run's measured peak memory.",
        )
        if peak is not None:
            st.caption(f"Peak memory used: {format_bytes(peak)}")

    return runtime_box


def set_runtime_caption(runtime_box, seconds):
    """Write the formatted runtime into a live placeholder from
    :func:`render_sort_metrics`. No-op if ``runtime_box`` is ``None``."""
    if runtime_box is not None:
        runtime_box.caption(f"Runtime: {format_duration(seconds)}")
