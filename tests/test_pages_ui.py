import time
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

# Captured before any monkeypatching so the fixture can still yield the GIL.
_REAL_SLEEP = time.sleep

ROOT = Path(__file__).resolve().parent.parent
HOME = str(ROOT / "Home.py")
EX1 = str(ROOT / "pages" / "1_Exercise_1.py")
EX2 = str(ROOT / "pages" / "2_Exercise_2.py")
EX3 = str(ROOT / "pages" / "3_Exercise_3.py")
EX4 = str(ROOT / "pages" / "4_Exercise_4.py")

# Exercise 1 now visualises ALL five implemented sorting algorithms.
ALGORITHMS = {"Bubble Sort", "Insertion Sort", "Heap Sort", "Merge Sort", "Quick Sort"}

# Generous timeout: sorting drives many AppTest reruns; CI machines are slow.
TIMEOUT = 60


@pytest.fixture(autouse=True)
def _instant_animation(monkeypatch):
    # Exercise 1 sleeps between animation frames (~12s total). Cap the shared
    # time.sleep so the frame loop is effectively instantaneous without turning
    # the test-thread poll into a GIL-hogging busy-wait.
    monkeypatch.setattr("time.sleep", lambda secs=0, *a, **k: _REAL_SLEEP(min(secs, 0.001)))


def run(path):
    return AppTest.from_file(path, default_timeout=TIMEOUT).run()


def button(at, label):
    """First button whose label contains ``label`` (fails clearly if absent)."""
    matches = [b for b in at.button if label in b.label]
    assert matches, f"expected a button containing '{label}', found {[b.label for b in at.button]}"
    return matches[0]


# ── Home page ───────────────────────────────────────────────────────────────
def test_home_renders_without_exception():
    assert not run(HOME).exception


def test_home_has_welcome_header():
    assert any("Welcome" in h.value for h in run(HOME).header)


def test_home_orients_across_all_four_sections():
    body = " ".join(m.value for m in run(HOME).markdown).lower()
    for word in ("sort", "complexity", "graph", "oop"):
        assert word in body


# ── Exercise 1: sorting visualizer (kept, now covers all 5 algorithms) ───────
def test_ex1_renders_without_exception():
    assert not run(EX1).exception


def test_ex1_has_title():
    assert any("Exercise 1" in t.value for t in run(EX1).title)


def test_ex1_algorithm_selectbox_covers_all_algorithms():
    at = run(EX1)
    assert len(at.selectbox) == 1
    assert at.selectbox[0].label == "Choose your Sorting Algorithm"
    assert set(at.selectbox[0].options) == ALGORITHMS


def test_ex1_sort_button_hidden_until_list_generated():
    assert "Sort Array" not in [b.label for b in run(EX1).button]


def _generate(at, size=8):
    at.slider[0].set_value(size).run()
    button(at, "Generate").click().run()
    return at


def test_ex1_generate_populates_state_and_reveals_sort():
    at = _generate(run(EX1), size=8)
    assert not at.exception
    assert len(at.session_state["generated_list"]) == 8
    assert "Sort Array" in [b.label for b in at.button]


@pytest.mark.parametrize("algorithm", sorted(ALGORITHMS))
def test_ex1_full_sort_journey_per_algorithm(algorithm):
    at = _generate(run(EX1), size=8)
    at.selectbox[0].set_value(algorithm).run()
    button(at, "Sort Array").click().run()
    assert not at.exception


def test_ex1_code_along_guide_renders_for_every_algorithm():
    from Models.SortGuide import GUIDES
    at = run(EX1)
    assert not at.exception
    # one guide tab + one code snippet per algorithm featured on the page
    assert len(GUIDES) == len(ALGORITHMS)
    assert {g["name"] for g in GUIDES} == ALGORITHMS
    assert any("code-along" in h.value.lower() for h in at.header)
    assert len(at.tabs) == len(GUIDES)
    assert len(at.code) >= len(GUIDES)            # a code snippet per algorithm


# ── Exercise 2: complexity quiz ──────────────────────────────────────────────
def test_ex2_renders_without_exception():
    assert not run(EX2).exception


def test_ex2_has_title_and_scoreboard():
    at = run(EX2)
    assert any("Complexity Quiz" in t.value for t in at.title)
    labels = [m.label for m in at.metric]
    assert {"Score", "Attempts", "Accuracy"} <= set(labels)


def test_ex2_starts_with_a_question_in_state():
    at = run(EX2)
    q = at.session_state["cq_question"]
    assert q["kind"] in ("code", "relationship")
    assert at.session_state["cq_total"] == 0


def _answer_correctly(at):
    from Models.Complexity import NOTATION_LABELS
    q = at.session_state["cq_question"]
    if q["kind"] == "code":
        at.radio[0].set_value(q["answer"]).run()
    else:
        at.multiselect[0].set_value([NOTATION_LABELS[s] for s in q["correct"]]).run()
    return at


def test_ex2_correct_answer_scores_and_gives_feedback():
    at = _answer_correctly(run(EX2))
    button(at, "Submit answer").click().run()
    assert not at.exception
    assert at.session_state["cq_total"] == 1
    assert at.session_state["cq_correct"] == 1
    assert at.session_state["cq_answered"] is True
    assert len(at.success) >= 1


def test_ex2_submitting_without_choosing_warns_and_does_not_score():
    at = run(EX2)
    button(at, "Submit answer").click().run()
    assert not at.exception
    assert at.session_state["cq_total"] == 0
    assert len(at.warning) >= 1


def test_ex2_next_question_advances_and_resets_answered():
    at = run(EX2)
    button(at, "Skip / New question").click().run()
    assert at.session_state["cq_num"] == 1
    assert at.session_state["cq_answered"] is False
    assert not at.exception


def test_ex2_reset_score_zeroes_the_scoreboard():
    at = _answer_correctly(run(EX2))
    button(at, "Submit answer").click().run()
    button(at, "Reset score").click().run()
    assert at.session_state["cq_total"] == 0
    assert at.session_state["cq_correct"] == 0
    assert not at.exception


# ── Exercise 3: MRT graph & traversal visualizer ─────────────────────────────
def test_ex3_renders_without_exception():
    assert not run(EX3).exception


def test_ex3_title_mentions_graph_traversal():
    assert any("Graph" in t.value and "Traversal" in t.value for t in run(EX3).title)


def test_ex3_has_start_selectbox_and_three_tabs():
    at = run(EX3)
    assert len(at.selectbox) == 1
    assert at.selectbox[0].label == "Start station"
    assert len(at.tabs) == 3
    assert len(at.slider) == 2                      # a Step slider per traversal


def test_ex3_next_step_advances_bfs_frontier():
    at = run(EX3)
    assert at.session_state["bfs_step"] == 0
    nexts = [b for b in at.button if b.label == "Next ▶"]
    assert nexts
    nexts[0].click().run()
    assert not at.exception
    assert at.session_state["bfs_step"] == 1


def test_ex3_changing_start_resets_step_counters():
    at = run(EX3)
    [b for b in at.button if b.label == "Next ▶"][0].click().run()
    assert at.session_state["bfs_step"] == 1
    at.selectbox[0].set_value("Bishan").run()
    assert not at.exception
    assert at.session_state["bfs_step"] == 0
    assert at.session_state["dfs_step"] == 0


# ── Exercise 4: OOP concepts + live Fraction demo ────────────────────────────
def test_ex4_renders_without_exception():
    assert not run(EX4).exception


def test_ex4_title_mentions_oop():
    assert any("Object-Oriented" in t.value for t in run(EX4).title)


def test_ex4_has_fraction_inputs_and_concept_tabs():
    from Models.OOPGuide import GUIDES
    at = run(EX4)
    assert len(at.number_input) == 4                 # two fractions × (num, den)
    assert len(at.tabs) == len(GUIDES)               # one tab per concept
    assert len(at.code) >= len(GUIDES) + 1           # each concept snippet + live demo


def test_ex4_live_demo_updates_on_input_change():
    at = run(EX4)
    at.number_input[0].set_value(2).run()            # f1 numerator
    at.number_input[1].set_value(4).run()            # f1 denominator -> reduces to 1/2
    assert not at.exception
    demo = " ".join(c.value for c in at.code)
    assert "Fraction(2, 4)" in demo                  # the REPL echoes the live values


def test_ex4_zero_denominator_triggers_assertion_error_message():
    at = run(EX4)
    at.number_input[1].set_value(0).run()            # f1 denominator = 0
    assert not at.exception                          # handled gracefully, not a crash
    assert len(at.error) >= 1
