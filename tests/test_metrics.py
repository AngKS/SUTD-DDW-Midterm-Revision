import time
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

# Captured before any monkeypatching so the fixture can still yield the GIL.
_REAL_SLEEP = time.sleep

from Models.Algorithms import BubbleSort, InsertionSort, HeapSort, MergeSort
from Utilities.Metrics import format_duration, format_bytes, measure_sort

ROOT = Path(__file__).resolve().parent.parent
EX1 = str(ROOT / "pages" / "1_Exercise_1.py")

TIMEOUT = 60
METRIC_LABELS = {"Sort Algorithm", "Time Complexity", "Space Complexity"}


@pytest.fixture(autouse=True)
def _instant_animation(monkeypatch):
    # Cap the inter-frame sleeps so sort journeys finish instantly. We must NOT
    # replace time.sleep with a pure no-op: AppTest runs the page on a worker
    # thread while the test thread polls in a `time.sleep(0.001)` loop. A no-op
    # turns that poll into a GIL-hogging busy-wait that starves the worker, so a
    # heavy page render never completes and the run hits the 60s timeout.
    # Capping (instead of zeroing) keeps the poll's tiny sleeps real — yielding
    # the GIL — while collapsing the page's long animation delays to ~instant.
    monkeypatch.setattr("time.sleep", lambda secs=0, *a, **k: _REAL_SLEEP(min(secs, 0.001)))

def run(path):
    return AppTest.from_file(path, default_timeout=TIMEOUT).run()


def button(at, label):
    matches = [b for b in at.button if b.label == label]
    assert matches, f"expected a '{label}' button, found {[b.label for b in at.button]}"
    return matches[0]


# ── Pure helpers: format_duration ───────────────────────────────────────────
@pytest.mark.parametrize("seconds,expected", [
    (5e-9,     "5 ns"),
    (1.23e-4,  "123.0 µs"),
    (0.5,      "500.00 ms"),
    (2.5,      "2.50 s"),
])
def test_format_duration(seconds, expected):
    assert format_duration(seconds) == expected


# ── Pure helpers: format_bytes ──────────────────────────────────────────────
@pytest.mark.parametrize("n,expected", [
    (0,              "0 B"),
    (512,            "512 B"),
    (2048,           "2.0 KB"),
    (5 * 1024**2,    "5.0 MB"),
    (3 * 1024**3,    "3.0 GB"),
])
def test_format_bytes(n, expected):
    assert format_bytes(n) == expected


# ── Pure helpers: measure_sort ──────────────────────────────────────────────
@pytest.mark.parametrize("cls", [BubbleSort, InsertionSort, HeapSort, MergeSort])
def test_measure_sort_returns_nonnegative_pair_without_mutating(cls):
    data = [5, 3, 8, 1, 9, 2, 7, 4, 6, 0]
    snapshot = list(data)
    elapsed, peak = measure_sort(cls(), data)
    assert data == snapshot          # caller's list is never touched
    assert elapsed >= 0 and peak >= 0


def test_measure_sort_reflects_space_complexity():
    # Merge Sort (O(n) auxiliary) should allocate a measurably larger peak than
    # the in-place Bubble Sort (O(1)) on the same sizeable input.
    data = list(range(400, 0, -1))
    _, peak_bubble = measure_sort(BubbleSort(), data)
    _, peak_merge = measure_sort(MergeSort(), data)
    assert peak_merge > peak_bubble


# ── Exercise 1: metrics appear after sorting; Clear resets state ─────────────
def _ex1_generate(at, size=8):
    at.slider[0].set_value(size).run()
    button(at, "Generate").click().run()
    return at


def test_ex1_has_clear_button():
    assert "Clear" in [b.label for b in run(EX1).button]


# The code-along guide below the visualizer also renders st.metric widgets
# (best/average/worst/space per algorithm), so these tests filter to the three
# *sort* metrics by their labels rather than counting every metric on the page.
def _sort_metrics(at):
    return [m for m in at.metric if m.label in METRIC_LABELS]


@pytest.mark.parametrize("algorithm",
                         ["Bubble Sort", "Insertion Sort", "Heap Sort", "Merge Sort", "Quick Sort"])
def test_ex1_sort_shows_three_metrics(algorithm):
    at = _ex1_generate(run(EX1), size=8)
    at.selectbox[0].set_value(algorithm).run()
    button(at, "Sort Array").click().run()
    assert not at.exception
    metrics = _sort_metrics(at)
    assert {m.label for m in metrics} == METRIC_LABELS
    # The algorithm metric headlines with the chosen sort's name.
    algo_metric = next(m for m in metrics if m.label == "Sort Algorithm")
    assert algo_metric.value == algorithm


def test_ex1_clear_resets_generated_list():
    at = _ex1_generate(run(EX1), size=8)
    assert at.session_state["generated_list"]
    button(at, "Clear").click().run()
    assert not at.exception
    assert at.session_state["generated_list"] == []
    assert at.session_state["numbers"] == ""
    # With nothing generated, the Sort action disappears again.
    assert "Sort Array" not in [b.label for b in at.button]


def test_ex1_metrics_absent_before_sorting():
    # No sort yet -> none of the three *sort* metrics are shown (the code-along
    # guide's complexity metrics further down the page are ignored here).
    assert _sort_metrics(_ex1_generate(run(EX1), size=8)) == []

# NOTE: Exercise 2 (now a complexity quiz) and Exercise 3 (now an MRT graph
# visualizer) no longer run sorts, so their metric-row tests were removed. Their
# new behaviour is covered in tests/test_pages_ui.py. The Metrics helpers above
# and Exercise 1's metric row remain fully exercised here.
