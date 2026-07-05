"""Correctness battery for the complexity-quiz question generator."""
import random

import pytest

from Models.Complexity import (
    LADDER, SNIPPETS, GROWTH, NOTATIONS, NOTATION_LABELS,
    make_code_question, make_relationship_question, new_question, is_correct,
)

# Reverse-lookup: each surface form ("3n² + n", "log n", …) → its asymptotic rank.
FORM_TO_RANK = {form: rank for rank, (_, forms) in enumerate(GROWTH) for form in forms}


def test_ladder_and_snippets_wellformed():
    assert LADDER[0] == "O(1)" and LADDER[-1] == "O(2ⁿ)"
    for s in SNIPPETS:
        assert s["time"] in LADDER and s["space"] in LADDER
        assert s["time_explain"] and s["space_explain"] and s["code"]


# ── Code questions ───────────────────────────────────────────────────────────
def test_code_question_is_gradable():
    rng = random.Random(1)
    for _ in range(200):
        q = make_code_question(rng)
        assert q["kind"] == "code"
        assert q["dimension"] in ("time", "space")
        assert q["answer"] in q["options"]
        assert 2 <= len(q["options"]) <= 5
        assert len(q["options"]) == len(set(q["options"]))     # no dup options
        assert is_correct(q, q["answer"]) is True
        wrong = next(o for o in q["options"] if o != q["answer"])
        assert is_correct(q, wrong) is False


# ── Relationship questions ───────────────────────────────────────────────────
def test_relationship_answer_matches_growth_ranks():
    rng = random.Random(2)
    valid_sets = [{"O", "o"}, {"O", "Θ", "Ω"}, {"Ω"}]
    for _ in range(400):
        q = make_relationship_question(rng)
        assert q["kind"] == "relationship"
        assert set(q["correct"]) in valid_sets
        rf, rg = FORM_TO_RANK[q["f"]], FORM_TO_RANK[q["g"]]
        if rf < rg:
            expected = {"O", "o"}
        elif rf > rg:
            expected = {"Ω"}
        else:
            expected = {"O", "Θ", "Ω"}
        assert set(q["correct"]) == expected, (q["f"], q["g"], rf, rg)


def test_relationship_grading_via_labels():
    rng = random.Random(3)
    q = make_relationship_question(rng)
    correct_labels = [NOTATION_LABELS[s] for s in q["correct"]]
    assert is_correct(q, correct_labels) is True
    # Any strict subset / superset is wrong.
    assert is_correct(q, []) is False
    all_labels = [label for _, label in NOTATIONS]
    if set(q["correct"]) != {sym for sym, _ in NOTATIONS}:
        assert is_correct(q, all_labels) is False


def test_relationship_covers_all_three_categories():
    rng = random.Random(4)
    seen = {frozenset(make_relationship_question(rng)["correct"]) for _ in range(300)}
    assert seen == {frozenset({"O", "o"}), frozenset({"O", "Θ", "Ω"}), frozenset({"Ω"})}


# ── Mixed generation ─────────────────────────────────────────────────────────
def test_new_question_mixes_both_kinds():
    rng = random.Random(5)
    kinds = {new_question(rng)["kind"] for _ in range(100)}
    assert kinds == {"code", "relationship"}


def test_seeded_generation_is_reproducible():
    a = new_question(random.Random(42))
    b = new_question(random.Random(42))
    assert a == b


def test_every_question_has_a_prompt_and_explanation():
    rng = random.Random(6)
    for _ in range(100):
        q = new_question(rng)
        assert q["prompt"] and q["explanation"] and q["title"]
