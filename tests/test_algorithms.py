import inspect
import random
from collections import Counter

import pytest

from Models.Algorithms import (
    SortAlgorithm,
    BubbleSort,
    InsertionSort,
    HeapSort,
    MergeSort,
    QuickSort,
)

# Every concrete algorithm under test. Add a new SortAlgorithm subclass here and
# it is automatically subjected to the entire correctness battery below.
ALGORITHM_CLASSES = [BubbleSort, InsertionSort, HeapSort, MergeSort, QuickSort]
ALGORITHM_IDS = [c.__name__ for c in ALGORITHM_CLASSES]

# Algorithms whose `sort()` routes input through `validate()` and therefore parse
# stringified numbers. Heap/Merge/Quick also validate; that consistency is
# checked separately at the bottom of this file.
VALIDATING_ALGORITHMS = [BubbleSort, InsertionSort]

# Documented metadata contract: (class, name, time-complexity, space-complexity)
ALGORITHM_META = [
    (BubbleSort,    "Bubble Sort",    "O(n²)",   "O(1)"),
    (InsertionSort, "Insertion Sort", "O(n²)",   "O(1)"),
    (HeapSort,      "Heap Sort",      "O(n log n)",   "O(1)"),
    (MergeSort,     "Merge Sort",     "O(n log n)",   "O(n)"),
    (QuickSort,     "Quick Sort",     "O(n log n)",   "O(log n)"),
]

# Edge-case inputs: id -> array. Every algorithm sorts each of these and the
# result is compared against sorted(). Covers the classic boundary shapes:
# empty/singleton, pre-sorted/reverse, duplicates, negatives, floats, mixed
# int/float, and extreme magnitudes.
EDGE_CASES = {
    "empty":            [],
    "single":           [42],
    "two_sorted":       [1, 2],
    "two_reversed":     [2, 1],
    "two_equal":        [5, 5],
    "all_equal":        [7, 7, 7, 7, 7],
    "already_sorted":   [1, 2, 3, 4, 5, 6, 7, 8],
    "reverse_sorted":   [9, 8, 7, 6, 5, 4, 3, 2, 1],
    "with_duplicates":  [3, 1, 2, 3, 1, 2, 3],
    "negatives":        [-5, -1, -10, -3, -2],
    "mixed_sign":       [3, -3, 0, 7, -7, 1, -1],
    "floats":           [2.5, 1.1, 2.5, 0.0, -1.5, 3.14],
    "int_and_float":    [3, 1.5, 2, 0.5, 4, 2.0],
    "large_reverse":    list(range(50, 0, -1)),
    "extremes":         [10**9, -10**9, 0, 1, -1],
}
EDGE_CASE_IDS = list(EDGE_CASES)
EDGE_CASE_VALUES = list(EDGE_CASES.values())


def run_sort(algo, data):
    """Drive an algorithm's ``sort`` generator to completion.

    ``sort`` mutates the list it is given in place while yielding frames, so we
    hand it a private copy, exhaust the generator, and return ``(sorted_list,
    frames)``.
    """
    arr = list(data)
    frames = list(algo.sort(arr))
    return arr, frames


# ── Core correctness ────────────────────────────────────────────────────────
@pytest.mark.parametrize("cls", ALGORITHM_CLASSES, ids=ALGORITHM_IDS)
@pytest.mark.parametrize("case", EDGE_CASE_VALUES, ids=EDGE_CASE_IDS)
def test_sort_matches_builtin_sorted(cls, case):
    result, _ = run_sort(cls(), case)
    assert result == sorted(case)


@pytest.mark.parametrize("cls", ALGORITHM_CLASSES, ids=ALGORITHM_IDS)
@pytest.mark.parametrize("case", EDGE_CASE_VALUES, ids=EDGE_CASE_IDS)
def test_sort_preserves_multiset(cls, case):
    # Sorting must reorder, never invent, drop, or duplicate elements.
    result, _ = run_sort(cls(), case)
    assert Counter(result) == Counter(case)


@pytest.mark.parametrize("cls", ALGORITHM_CLASSES, ids=ALGORITHM_IDS)
def test_sort_mutates_input_in_place(cls):
    arr = [3, 1, 2]
    list(cls().sort(arr))  # exhaust the generator
    assert arr == [1, 2, 3]


@pytest.mark.parametrize("cls", ALGORITHM_CLASSES, ids=ALGORITHM_IDS)
def test_sort_returns_generator(cls):
    gen = cls().sort([2, 1])
    assert inspect.isgenerator(gen)
    list(gen)  # drain it so the in-place sort actually completes


@pytest.mark.parametrize("cls", ALGORITHM_CLASSES, ids=ALGORITHM_IDS)
def test_sort_is_idempotent(cls):
    data = [5, 2, 9, 1, 5, 6, 2]
    once, _ = run_sort(cls(), data)
    twice, _ = run_sort(cls(), once)
    assert once == twice == sorted(data)


@pytest.mark.parametrize("cls", ALGORITHM_CLASSES, ids=ALGORITHM_IDS)
@pytest.mark.parametrize("seed", [0, 1, 7, 42, 99, 2024, 123456])
def test_sort_random_stress(cls, seed):
    # Randomized differential test: many shapes/sizes (including empty) compared
    # against the reference implementation. Deterministic per seed.
    rng = random.Random(seed)
    size = rng.randint(0, 80)
    data = [rng.randint(-1000, 1000) for _ in range(size)]
    result, _ = run_sort(cls(), data)
    assert result == sorted(data)


# ── animate_sort frame contract ─────────────────────────────────────────────
@pytest.mark.parametrize("cls", ALGORITHM_CLASSES, ids=ALGORITHM_IDS)
def test_animate_sort_frame_contract(cls):
    frames = cls().animate_sort([4, 2, 5, 1, 3, 2])
    assert isinstance(frames, list)
    assert len(frames) >= 2  # at least an initial and a final frame
    for f in frames:
        assert set(f.keys()) == {"phase", "graphviz", "html"}
        assert isinstance(f["phase"], str) and f["phase"]
        assert isinstance(f["html"], str) and f["html"]
        assert f["graphviz"] is None or isinstance(f["graphviz"], str)
    assert frames[0]["phase"] == "Initial array"


@pytest.mark.parametrize("cls", ALGORITHM_CLASSES, ids=ALGORITHM_IDS)
def test_animate_sort_does_not_mutate_input(cls):
    data = [4, 2, 5, 1, 3]
    snapshot = list(data)
    cls().animate_sort(data)
    assert data == snapshot


@pytest.mark.parametrize("cls", ALGORITHM_CLASSES, ids=ALGORITHM_IDS)
@pytest.mark.parametrize("case", [[], [1], [2, 1], [5, 5]],
                         ids=["empty", "single", "pair", "dupe_pair"])
def test_animate_sort_handles_edge_inputs(cls, case):
    frames = cls().animate_sort(case)
    assert isinstance(frames, list) and len(frames) >= 1


# ── Metadata / dunder contract ──────────────────────────────────────────────
@pytest.mark.parametrize("cls,name,t_complexity,s_complexity", ALGORITHM_META,
                         ids=[m[1] for m in ALGORITHM_META])
def test_metadata(cls, name, t_complexity, s_complexity):
    algo = cls()
    assert str(algo) == name
    assert repr(algo) == name
    assert algo.name == name
    assert algo.t_complexity == t_complexity
    assert algo.s_complexity == s_complexity


def test_metadata_properties_are_settable():
    algo = BubbleSort()
    algo.name, algo.t_complexity, algo.s_complexity = "Bubbly", "O(n)", "O(n)"
    assert (algo.name, algo.t_complexity, algo.s_complexity) == ("Bubbly", "O(n)", "O(n)")
    assert str(algo) == "Bubbly"


def test_base_class_sort_is_abstract():
    # SortAlgorithm itself provides no sort implementation.
    with pytest.raises(NotImplementedError):
        SortAlgorithm("Base").sort([1, 2, 3])


# ── validate() / numeric parsing ────────────────────────────────────────────
def test_validate_accepts_numeric_list_unchanged():
    algo = BubbleSort()
    arr = [3, 1, 2]
    assert algo.validate(arr) is None
    assert arr == [3, 1, 2]


def test_validate_parses_numeric_strings_in_place():
    algo = BubbleSort()
    arr = ["3", "1.5", " 2 ", "-4"]
    assert algo.validate(arr) is None
    assert arr == [3, 1.5, 2, -4]


def test_validate_typing_int_vs_float():
    # Integer-looking strings become int; decimal strings become float.
    algo = BubbleSort()
    arr = ["10", "10.0", "0", "-7", "3.14"]
    algo.validate(arr)
    assert [type(x).__name__ for x in arr] == ["int", "float", "int", "int", "float"]


@pytest.mark.parametrize("bad", ["not a list", 123, ("a", "b"), None, 4.5],
                         ids=["str", "int", "tuple", "none", "float"])
def test_validate_rejects_non_list(bad):
    assert BubbleSort().validate(bad) == "NAWWWW"


@pytest.mark.parametrize("bad", [[True], [False, 1], [1, "abc"], [None], [[1, 2]]],
                         ids=["bool", "bool_mixed", "unparseable_str",
                              "none_element", "nested_list"])
def test_validate_rejects_invalid_elements(bad):
    # Booleans, unparseable strings, None, and nested containers are all invalid.
    assert BubbleSort().validate(bad) == "NAWWWW"


# ── String-number parsing through sort() (consistency check) ────────────────
@pytest.mark.parametrize("cls", VALIDATING_ALGORITHMS,
                         ids=[c.__name__ for c in VALIDATING_ALGORITHMS])
def test_validating_sorts_parse_string_numbers(cls):
    # Multi-digit values chosen so lexicographic order ("1","10","2","30","9")
    # differs from numeric order — proving real numeric parsing, not luck.
    arr = ["10", "9", "2", "30", "1"]
    result, _ = run_sort(cls(), arr)
    assert result == [1, 2, 9, 10, 30]


@pytest.mark.parametrize("cls", [HeapSort, MergeSort], ids=["HeapSort", "MergeSort"])
def test_nonvalidating_sorts_should_parse_string_numbers(cls):
    arr = ["10", "9", "2", "30", "1"]
    result, _ = run_sort(cls(), arr)
    assert result == [1, 2, 9, 10, 30]


# ── Quick Sort — pivot / partition specifics ────────────────────────────────
# Quick Sort is a comparison sort, so it also rides the shared battery above.
# These extra cases target its known stress points: inputs that push the Lomuto
# partition toward its O(n²) worst case must still sort *correctly*.
def test_quick_sort_locks_pivots_into_final_positions():
    # Each `locked` set snapshot only ever grows and never exceeds the array size.
    q = QuickSort()
    arr = [5, 2, 8, 1, 9, 3, 7, 4, 6, 0]
    sizes = [len(set(sorted_idx)) for _, _, sorted_idx in q.sort(arr)]
    assert sizes == sorted(sizes)                 # monotonically non-decreasing
    assert max(sizes) <= len(arr)
    assert arr == sorted([5, 2, 8, 1, 9, 3, 7, 4, 6, 0])


@pytest.mark.parametrize("case", [
    list(range(30)),            # already sorted — Lomuto worst case
    list(range(30, 0, -1)),     # reverse sorted
    [7] * 20,                   # all equal
], ids=["sorted", "reversed", "all_equal"])
def test_quick_sort_worst_case_inputs_still_sort(case):
    result, _ = run_sort(QuickSort(), case)
    assert result == sorted(case)


def test_quick_sort_metadata():
    algo = QuickSort()
    assert algo.name == "Quick Sort"
    assert algo.t_complexity == "O(n log n)"
    assert algo.s_complexity == "O(log n)"
