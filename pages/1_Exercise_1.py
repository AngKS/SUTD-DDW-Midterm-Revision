import time
import streamlit as st
from datetime import datetime
from library import gen_random_int, create_string
from Models.Algorithms import BubbleSort, InsertionSort, HeapSort, MergeSort, QuickSort
from Models.SortGuide import GUIDES
from Utilities.Metrics import measure_sort, render_sort_metrics, set_runtime_caption

# set_page_config must be the first Streamlit command, so it lives at module
# top — before initialize() renders the algorithm selectbox.
st.set_page_config(page_title="Exercise 1", layout="wide")


def initialize():
    global sort_choice
    global sorting_algos
    # All five implemented sorting algorithms are visualisable here — the four
    # comparison sorts plus Quick Sort (Week 3's divide-and-conquer homework sort).
    sorting_algos = {
        "Bubble Sort": BubbleSort(),
        "Insertion Sort": InsertionSort(),
        "Heap Sort": HeapSort(),
        "Merge Sort": MergeSort(),
        "Quick Sort": QuickSort(),
    }
    st.title("Exercise 1 - Generate n-number random array")
    sort_choice = st.selectbox(
        "Choose your Sorting Algorithm",
        sorting_algos,
    )


def render_sort_guide():
    # ── Information & code-along guide (one tab per algorithm on this page) ──────
    st.divider()
    st.header("📚 Information & code-along guide")
    st.write(
        "A quick reference for every sort in the visualizer above — how it works, "
        "its best / average / worst-case complexity, and a Python implementation "
        "you can **code along** with."
    )
    tabs = st.tabs([g["name"] for g in GUIDES])
    for tab, guide in zip(tabs, GUIDES):
        with tab:
            st.markdown(f"**{guide['summary']}**")

            # Complexity at a glance — reuse the visualizer's native metric widgets.
            c_best, c_avg, c_worst, c_space = st.columns(4)
            c_best.metric("Best time", guide["best"])
            c_avg.metric("Average time", guide["average"])
            c_worst.metric("Worst time", guide["worst"])
            c_space.metric("Space", guide["space"])
            st.caption(f"Stable sort: {'✅ yes' if guide['stable'] else '❌ no'}")

            st.markdown("**How it works**")
            st.markdown(guide["how"])

            st.markdown("**Implementation** — code along 👇")
            st.code(guide["code"], language="python")


def generate(number, max_num):
    array = gen_random_int(number, int(datetime.now().timestamp()), max_num)
    st.session_state['generated_list'] = array
    st.session_state['numbers'] = create_string(array)


def clear():
    # Reset the generated input so the page returns to its empty starting state.
    st.session_state['generated_list'] = []
    st.session_state['numbers'] = ""


def main():
    

    if 'numbers' not in st.session_state:
        st.session_state['numbers'] = ""
    if 'generated_list' not in st.session_state:
        st.session_state['generated_list'] = []
    if 'numbers' not in st.session_state:
        st.session_state['numbers'] = ""
    if 'generated_list' not in st.session_state:
        st.session_state['generated_list'] = []

    # ── Random-array input (Exercise 1's identity) ──────────────────────────
    num_items = st.slider("Select number of items in array", 2, 50)
    col_generate, col_clear = st.columns(2)
    col_generate.button("Generate", on_click=generate, args=(num_items, 100),
                        use_container_width=True)
    col_clear.button("Clear", on_click=clear, use_container_width=True)

    if st.session_state['numbers']:
        st.write("Generated Numbers:", st.session_state['numbers'])
    st.badge(f"{st.session_state['generated_list']}")

    if st.session_state['generated_list'] and st.button("Sort Array"):
        algo = sorting_algos[sort_choice]

        # ── Post-sort metrics (rendered ABOVE the visualization) ─────────────
        # Time/trace the pure algorithm first, then surface the results as a row
        # of three native metric widgets before the animation plays below them.
        # The runtime subtitle is a live placeholder that ticks 0 → elapsed as
        # the animation advances.
        elapsed, peak = measure_sort(algo, st.session_state['generated_list'])
        runtime_box = render_sort_metrics(algo, elapsed, peak, live_runtime=True)

        result = algo.animate_sort(
            st.session_state['generated_list']
        )

        if isinstance(result, list):
            # ── Stepped frame animation (shared {phase, graphviz, html}) ─────
            # Each frame carries a ready-to-render "html" body and an optional
            # "graphviz" dot. Auto-play: redraw shared placeholders frame by
            # frame, aiming for a ~12s total run, clamped per-frame either way.
            total = len(result)
            delay = min(0.5, max(0.03, 12 / total))

            caption_box = st.empty()
            graph_box = st.empty()
            body_box = st.empty()

            for i, frame in enumerate(result):
                caption_box.caption(f"**Step {i + 1} / {total}:** {frame['phase']}")
                # Natural size (not container-width) so wide trees stay legible
                # and scroll horizontally instead of squishing to a thin strip.
                if frame.get("graphviz"):
                    graph_box.graphviz_chart(frame["graphviz"], use_container_width=False)
                else:
                    graph_box.empty()
                body_box.markdown(frame["html"], unsafe_allow_html=True)
                # Tick the runtime counter up in step with the animation.
                set_runtime_caption(runtime_box, elapsed * (i + 1) / total)
                time.sleep(delay)
        else:
            # ── Bar-chart animation fallback (Bubble / Insertion Sort) ───────
            st.plotly_chart(result)

        # Land on the exact measured runtime once the animation finishes.
        set_runtime_caption(runtime_box, elapsed)
        st.balloons()

    # The learning guide renders below the visualizer, whether or not a sort ran.
    render_sort_guide()


if __name__ == "__main__":
    initialize()
    main()
