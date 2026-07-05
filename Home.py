import streamlit as st

st.set_page_config(page_title="DDW Midterm Revision", page_icon="🧮", layout="wide")


st.header("Welcome to the DDW 10.020 Midterm Revision app 🧮")

st.write(
    "Four interactive revision stations for the midterm — a sorting-algorithm "
    "**visualizer**, a **complexity quiz**, a **graph-traversal guide**, and an "
    "**OOP workshop**. Pick an exercise from the sidebar, or use the shortcuts below."
)

row1_left, row1_right = st.columns(2)
row2_left, row2_right = st.columns(2)

with row1_left:
    st.subheader("1 · Sorting Visualizer")
    st.write(
        "Generate a random array and watch **Bubble, Insertion, Heap, Merge** and "
        "**Quick** sort run step by step, with live time & space complexity metrics — "
        "plus a code-along guide for each algorithm."
    )
    st.page_link("pages/1_Exercise_1.py", label="Open Exercise 1", icon="🔢")

with row1_right:
    st.subheader("2 · Complexity Quiz")
    st.write(
        "Random questions on **Big-O (O), little-o (o), Θ and Ω** — read a code "
        "snippet's time/space cost, or classify how two functions grow. Scored, "
        "with an explanation after every answer."
    )
    st.page_link("pages/2_Exercise_2.py", label="Open Exercise 2", icon="⏱️")

with row2_left:
    st.subheader("3 · Graph Traversal (MRT)")
    st.write(
        "Learn **graphs, BFS (queue) and DFS (stack)** on a small Singapore MRT map. "
        "Step through the frontier and visited set, then compare the two spanning trees."
    )
    st.page_link("pages/3_Exercise_3.py", label="Open Exercise 3", icon="🚇")

with row2_right:
    st.subheader("4 · Object-Oriented Programming")
    st.write(
        "Build a live **`Fraction`** object, then walk **classes, encapsulation, dunder "
        "methods, inheritance & polymorphism** — with runnable example code and the "
        "special techniques (properties, abstract methods, class/static methods)."
    )
    st.page_link("pages/4_Exercise_4.py", label="Open Exercise 4", icon="🧱")

st.divider()
st.caption(
    "Built with Streamlit · reuses the sorting-app engine from the original "
    "Mini Project 1. Everything is randomly generated, so revise as many rounds as you like."
)
