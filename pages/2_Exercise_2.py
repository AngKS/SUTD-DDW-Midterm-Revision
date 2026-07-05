"""Exercise 2 — Time & Space Complexity Quiz.

Randomly generated Big-O / little-o / Θ / Ω questions with scoring, immediate
feedback and a teaching explanation per answer. All question/answer/score state
lives in ``st.session_state`` so the app survives Streamlit's rerun-on-every-
interaction model.
"""
import streamlit as st

from Models.Complexity import new_question, is_correct
from Utilities.GraphView import _COLORS  # reuse the sort-visualizer palette

st.set_page_config(page_title="Exercise 2 — Complexity Quiz", layout="wide")


# ── Small styled cards (reuse the project's inline-style visual language) ─────
def _fn_card(label, expr, bg):
    return (
        f"<div style='flex:1;text-align:center;border-radius:10px;padding:14px 10px;"
        f"margin:4px;background:{bg};color:#fff;'>"
        f"<div style='font-size:12px;opacity:.85;letter-spacing:.5px;'>{label}</div>"
        f"<div style='font-size:26px;font-weight:700;margin-top:2px;'>{expr}</div></div>"
    )


# ── Session-state helpers ─────────────────────────────────────────────────────
def _init_state():
    ss = st.session_state
    ss.setdefault("cq_num", 0)          # increments per question; salts widget keys
    ss.setdefault("cq_correct", 0)
    ss.setdefault("cq_total", 0)
    ss.setdefault("cq_answered", False)
    ss.setdefault("cq_feedback", None)  # (was_correct, correct_text, explanation)
    ss.setdefault("cq_warn", False)
    if "cq_question" not in ss:
        ss["cq_question"] = new_question()


def _correct_text(question):
    if question["kind"] == "code":
        return question["answer"]
    return ", ".join(f"{s}(g)" for s in ["O", "o", "Θ", "Ω"] if s in question["correct"])


def submit():
    ss = st.session_state
    q = ss["cq_question"]
    resp = ss.get(f"cq_ans_{ss['cq_num']}")
    if not resp:                       # nothing chosen yet — don't score it
        ss["cq_warn"] = True
        return
    ss["cq_warn"] = False
    correct = is_correct(q, resp)
    ss["cq_total"] += 1
    if correct:
        ss["cq_correct"] += 1
    ss["cq_answered"] = True
    ss["cq_feedback"] = (correct, _correct_text(q), q["explanation"])


def next_question():
    ss = st.session_state
    ss["cq_num"] += 1
    ss["cq_question"] = new_question()
    ss["cq_answered"] = False
    ss["cq_feedback"] = None
    ss["cq_warn"] = False


def reset_score():
    ss = st.session_state
    ss["cq_correct"] = 0
    ss["cq_total"] = 0
    next_question()


# ── Page ──────────────────────────────────────────────────────────────────────
def main():
    _init_state()
    ss = st.session_state

    st.title("Exercise 2 — Time & Space Complexity Quiz")
    st.write(
        "Practise the four asymptotic notations from class. Questions are "
        "**randomly generated** — identify the complexity of a code snippet, or "
        "classify how one function grows relative to another. Every answer comes "
        "with a short explanation so you learn as you go."
    )

    with st.expander("📘 Quick guide — the four notations", expanded=False):
        st.markdown(
            "Think of comparing a function **f(n)** to a reference **g(n)**:\n\n"
            "| Notation | Meaning | Intuition |\n"
            "|---|---|---|\n"
            "| **O(g)** | upper bound | f grows **no faster** than g |\n"
            "| **o(g)** | *strict* upper bound | f grows **strictly slower** than g (f/g → 0) |\n"
            "| **Θ(g)** | tight bound | f grows at the **same rate** as g |\n"
            "| **Ω(g)** | lower bound | f grows **no slower** than g |\n\n"
            "Key links: **Θ ⇒ both O and Ω**. **o ⇒ O** (but not Θ, not Ω). "
            "**ω ⇒ Ω** (but not Θ, not O). A *strict* bound (o or ω) is never also tight (Θ)."
        )

    # ── Scoreboard ────────────────────────────────────────────────────────────
    total = ss["cq_total"]
    correct = ss["cq_correct"]
    accuracy = (correct / total * 100) if total else 0.0
    m1, m2, m3 = st.columns(3)
    m1.metric("Score", f"{correct} / {total}")
    m2.metric("Attempts", total)
    m3.metric("Accuracy", f"{accuracy:.0f}%")
    st.progress(min(1.0, accuracy / 100) if total else 0.0)
    st.divider()

    q = ss["cq_question"]
    n = ss["cq_num"]
    kind_label = "Code complexity" if q["kind"] == "code" else "Growth relationship"
    st.caption(f"Question #{n + 1} · {kind_label}")

    # ── Question body ─────────────────────────────────────────────────────────
    if q["kind"] == "code":
        st.markdown(f"**{q['title']}**")
        st.code(q["code"], language="python")
        st.markdown(q["prompt"])
        st.radio(
            "Your answer", q["options"], index=None,
            key=f"cq_ans_{n}", label_visibility="collapsed",
            disabled=ss["cq_answered"], horizontal=True,
        )
    else:
        st.markdown(
            f"<div style='display:flex;gap:8px;margin:6px 0 10px;'>"
            f"{_fn_card('f(n)', q['f'], _COLORS['left'])}"
            f"{_fn_card('g(n)', q['g'], _COLORS['right'])}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(q["prompt"])
        st.multiselect(
            "Select all notations that apply", q["options"],
            key=f"cq_ans_{n}", label_visibility="collapsed",
            disabled=ss["cq_answered"],
        )

    if ss["cq_warn"] and not ss["cq_answered"]:
        st.warning("Pick an answer before submitting.")

    # ── Actions ───────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1, 1, 1])
    if not ss["cq_answered"]:
        c1.button("✅ Submit answer", on_click=submit, type="primary",
                  use_container_width=True)
        c2.button("↻ Skip / New question", on_click=next_question,
                  use_container_width=True)
    else:
        c1.button("➡️ Next question", on_click=next_question, type="primary",
                  use_container_width=True)
    c3.button("🗑️ Reset score", on_click=reset_score, use_container_width=True)

    # ── Feedback ──────────────────────────────────────────────────────────────
    if ss["cq_answered"] and ss["cq_feedback"]:
        was_correct, correct_text, explanation = ss["cq_feedback"]
        st.divider()
        if was_correct:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Not quite — the correct answer is **{correct_text}**.")
        st.markdown(
            f"<div style='border-left:4px solid {_COLORS['value']};background:#f4f8fd;"
            f"padding:10px 14px;border-radius:0 8px 8px 0;'>{explanation}</div>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
