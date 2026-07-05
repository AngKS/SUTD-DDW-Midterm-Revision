"""Tests for the Exercise 4 OOP demo class and guide content."""
import pytest

from Models.OOPDemo import Fraction
from Models.OOPGuide import GUIDES


# ── Fraction: construction, validation, reduction ────────────────────────────
def test_fraction_reduces_on_construction():
    assert (Fraction(2, 4).numerator, Fraction(2, 4).denominator) == (1, 2)
    assert (Fraction(6, 3).numerator, Fraction(6, 3).denominator) == (2, 1)


def test_fraction_normalises_sign_to_numerator():
    f = Fraction(1, -2)
    assert (f.numerator, f.denominator) == (-1, 2)
    assert str(f) == "-1/2"


def test_fraction_rejects_zero_denominator():
    with pytest.raises(AssertionError):
        Fraction(1, 0)


def test_fraction_rejects_non_integer():
    with pytest.raises(AssertionError):
        Fraction(1.5, 2)


# ── Dunder methods ───────────────────────────────────────────────────────────
def test_str_and_repr():
    assert str(Fraction(1, 2)) == "1/2"
    assert str(Fraction(3, 1)) == "3"          # whole numbers drop the denominator
    assert repr(Fraction(1, 2)) == "Fraction(1, 2)"


def test_equality_and_hash_collapse_equivalent_fractions():
    assert Fraction(1, 2) == Fraction(2, 4)
    assert len({Fraction(1, 2), Fraction(2, 4), Fraction(3, 6)}) == 1   # __hash__ + __eq__


def test_ordering_enables_sorting():
    assert Fraction(1, 2) < Fraction(3, 4)
    ordered = sorted([Fraction(3, 4), Fraction(1, 2), Fraction(2, 3)])
    assert [str(f) for f in ordered] == ["1/2", "2/3", "3/4"]


def test_addition_returns_new_fraction_without_mutating():
    a, b = Fraction(1, 2), Fraction(1, 3)
    total = a + b
    assert total == Fraction(5, 6)
    assert (a.numerator, a.denominator) == (1, 2)   # operands untouched
    assert (b.numerator, b.denominator) == (1, 3)


def test_to_float():
    assert Fraction(1, 4).to_float() == 0.25


# ── Alternative constructor / static helper / class attribute ────────────────
def test_from_string_classmethod():
    assert Fraction.from_string("3/4") == Fraction(3, 4)
    assert Fraction.from_string(" 5 ") == Fraction(5, 1)


def test_static_helper_and_class_counter():
    assert Fraction.is_valid_denominator(2) is True
    assert Fraction.is_valid_denominator(0) is False
    before = Fraction.count
    Fraction(1, 2)
    Fraction(3, 4)
    assert Fraction.count == before + 2         # shared class attribute increments


# ── Guide content ────────────────────────────────────────────────────────────
def test_guide_entries_are_complete():
    assert len(GUIDES) >= 6
    names = [g["name"] for g in GUIDES]
    assert len(names) == len(set(names))         # unique tab names
    for g in GUIDES:
        assert g["name"] and g["summary"] and g["points"] and g["code"]


@pytest.mark.parametrize("guide", GUIDES, ids=[g["name"] for g in GUIDES])
def test_every_guide_snippet_is_valid_python(guide):
    # Compile (syntax-check) every example so a broken snippet fails CI, not a student.
    compile(guide["code"], f"<guide:{guide['name']}>", "exec")


def test_guide_covers_the_core_oop_concepts():
    blob = " ".join(g["name"] + g["points"] + g["code"] for g in GUIDES).lower()
    for concept in ["property", "super(", "notimplementederror", "classmethod",
                    "staticmethod", "__str__", "__lt__", "assert"]:
        assert concept in blob, f"guide is missing {concept}"
