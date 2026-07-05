"""Exercise 4 — Object-Oriented Programming (OOP).

A hands-on OOP revision station (Weeks 4–5): a live ``Fraction`` object whose
methods respond as you change its inputs, followed by concept tabs — classes,
encapsulation, dunder methods, inheritance, polymorphism and the special
techniques (properties, abstract methods, classmethod/staticmethod) — each with
runnable example code.
"""
import streamlit as st

from Models.OOPDemo import Fraction
from Models.OOPGuide import GUIDES

st.set_page_config(page_title="Exercise 4 — OOP", layout="wide")


def fraction_playground():
    st.write(
        "Change the numbers and watch the **object's methods** respond. Every line "
        "below is driven by the same `Fraction` class — the dunder methods are what "
        "let `str()`, `+`, `<` and `==` work on your own type."
    )
    left, right = st.columns(2)
    with left:
        n1 = st.number_input("f₁ numerator", value=1, step=1, key="oop_n1")
        d1 = st.number_input("f₁ denominator", value=2, step=1, key="oop_d1")
    with right:
        n2 = st.number_input("f₂ numerator", value=3, step=1, key="oop_n2")
        d2 = st.number_input("f₂ denominator", value=4, step=1, key="oop_d2")

    try:
        f1 = Fraction(int(n1), int(d1))
        f2 = Fraction(int(n2), int(d2))
    except AssertionError as exc:
        st.error(f"❌ Invalid fraction — the `assert` in `__init__` fired: **{exc}**")
        return

    session = (
        f">>> f1 = Fraction({int(n1)}, {int(d1)})\n"
        f">>> f2 = Fraction({int(n2)}, {int(d2)})\n"
        f">>> str(f1)              # __str__   -> {str(f1)!r}   (auto-reduced by gcd)\n"
        f">>> str(f2)              # __str__   -> {str(f2)!r}\n"
        f">>> str(f1 + f2)         # __add__   -> {str(f1 + f2)!r}\n"
        f">>> f1 < f2              # __lt__    -> {f1 < f2}\n"
        f">>> f1 == f2             # __eq__    -> {f1 == f2}\n"
        f">>> f1.to_float()        # method    -> {round(f1.to_float(), 4)}\n"
        f">>> repr(f1)             # __repr__  -> {repr(f1)!r}"
    )
    st.code(session, language="python")
    st.caption(
        "Notice: the fraction **auto-reduces** in `__init__` (e.g. `2/4 → 1/2`), and "
        "`f1 + f2` returns a **brand-new** `Fraction` — the operands are never mutated."
    )


def concepts():
    st.subheader("📖 Concepts & special techniques")
    tabs = st.tabs([g["name"] for g in GUIDES])
    for tab, guide in zip(tabs, GUIDES):
        with tab:
            st.markdown(f"**{guide['summary']}**")
            st.markdown(guide["points"])
            if guide.get("technique"):
                st.info(guide["technique"])
            st.markdown("**Example — read it, then try it yourself** 👇")
            st.code(guide["code"], language="python")


def main():
    st.title("Exercise 4 — Object-Oriented Programming 🧱")
    st.write(
        "OOP bundles **data** (attributes) and **behaviour** (methods) into **objects** — "
        "the backbone of **Weeks 4–5**. Play with a live class first, then walk the core "
        "concepts and the special techniques that make Python objects powerful. *(You've "
        "already met this: every sort in Exercise 1 is a subclass of a `SortAlgorithm` "
        "base class.)*"
    )

    st.subheader("🧪 Live demo — a `Fraction` class")
    fraction_playground()

    st.divider()
    concepts()


if __name__ == "__main__":
    main()
