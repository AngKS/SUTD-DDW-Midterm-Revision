"""A runnable ``Fraction`` class for Exercise 4's live OOP demo.

Deliberately written in the DDW house style so it doubles as a worked example:
assert-validated ``__init__``, single-underscore attributes behind ``@property``,
a ``@classmethod`` alternative constructor, a ``@staticmethod`` helper, and the
dunder methods (``__str__``/``__repr__``/``__eq__``/``__lt__``/``__add__``) that
let objects behave like built-in numbers. Pure Python, so it is unit-testable.
"""
from math import gcd


class Fraction:
    count = 0  # class attribute — shared across every instance

    def __init__(self, numerator, denominator=1):
        assert isinstance(numerator, int) and isinstance(denominator, int), \
            "numerator and denominator must be integers"
        assert denominator != 0, "denominator must not be zero"
        # keep the sign on the numerator, then reduce by the gcd
        if denominator < 0:
            numerator, denominator = -numerator, -denominator
        divisor = gcd(abs(numerator), denominator) or 1
        self._numerator = numerator // divisor
        self._denominator = denominator // divisor
        Fraction.count += 1

    # ── Encapsulated, read-only views of the internal state ─────────────────
    @property
    def numerator(self):
        return self._numerator

    @property
    def denominator(self):
        return self._denominator

    def to_float(self):
        return self._numerator / self._denominator

    # ── Alternative constructor / namespaced helper ─────────────────────────
    @classmethod
    def from_string(cls, text):
        """Build from a string: ``Fraction.from_string("3/4")``."""
        text = text.strip()
        if "/" in text:
            num, den = text.split("/", 1)
            return cls(int(num), int(den))
        return cls(int(text))

    @staticmethod
    def is_valid_denominator(value):
        return isinstance(value, int) and value != 0

    # ── Dunder methods: make the object work with built-in syntax ───────────
    def __str__(self):
        if self._denominator == 1:
            return f"{self._numerator}"
        return f"{self._numerator}/{self._denominator}"

    def __repr__(self):
        return f"Fraction({self._numerator}, {self._denominator})"

    def __eq__(self, other):
        return (self._numerator, self._denominator) == (other._numerator, other._denominator)

    def __lt__(self, other):
        # cross-multiply — denominators are always positive after reduction
        return self._numerator * other._denominator < other._numerator * self._denominator

    def __add__(self, other):
        numerator = self._numerator * other._denominator + other._numerator * self._denominator
        denominator = self._denominator * other._denominator
        return Fraction(numerator, denominator)

    def __hash__(self):
        return hash((self._numerator, self._denominator))
