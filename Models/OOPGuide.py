"""Content for the Exercise 4 OOP guide — one entry per concept.

Pure data (no Streamlit). Each entry: a plain-English ``summary``, ``points``
(markdown bullets), an optional ``technique`` call-out for a "special technique",
and a runnable/illustrative ``code`` snippet in the DDW house style.
"""

GUIDES = [
    {
        "name": "Classes & Objects",
        "summary": "A class is a blueprint; an object is one instance of it, with its own data.",
        "points": (
            "- `class Fraction:` defines the blueprint — `Fraction(1, 2)` **instantiates** an object.\n"
            "- `__init__` is the **constructor**: it runs once at creation to set up the object's attributes.\n"
            "- `self` is the object itself; its data lives on it (`self._numerator`).\n"
            "- **Methods** are functions defined inside the class that act on `self`."
        ),
        "code": (
            "class Fraction:\n"
            "    def __init__(self, numerator, denominator=1):\n"
            "        self._numerator = numerator          # instance attribute\n"
            "        self._denominator = denominator\n"
            "\n"
            "    def to_float(self):                      # a method\n"
            "        return self._numerator / self._denominator\n"
            "\n"
            "half = Fraction(1, 2)      # instantiate an object\n"
            "print(half.to_float())     # 0.5"
        ),
    },
    {
        "name": "Encapsulation & Properties",
        "summary": "Hide the internal data behind a clean interface, and validate every change.",
        "points": (
            "- A single leading underscore (`self._x`) signals **“internal — don't touch directly.”**\n"
            "- `@property` turns a method into a **read-only attribute**: `frac.numerator` (no parentheses).\n"
            "- A **validated setter** guards writes so the object can never reach a bad state.\n"
            "- `assert` in `__init__` enforces the object's **invariants** up front (DDW convention)."
        ),
        "technique": "Special technique — the `@property` + setter pair keeps attribute-style "
                     "access (`obj.x`) while still running validation code on every read/write.",
        "code": (
            "class Account:\n"
            "    def __init__(self, balance=0):\n"
            "        assert balance >= 0, \"balance cannot start negative\"\n"
            "        self._balance = balance\n"
            "\n"
            "    @property\n"
            "    def balance(self):              # read:  account.balance\n"
            "        return self._balance\n"
            "\n"
            "    @balance.setter\n"
            "    def balance(self, value):       # write: account.balance = 100\n"
            "        assert value >= 0, \"balance cannot go negative\"\n"
            "        self._balance = value\n"
            "\n"
            "acc = Account(50)\n"
            "acc.balance = 80        # validated write\n"
            "# acc.balance = -5      # -> AssertionError!"
        ),
    },
    {
        "name": "Dunder (magic) methods",
        "summary": "“Double-underscore” methods let your objects plug into Python's built-in syntax.",
        "points": (
            "- `__str__` → what `str(obj)` / `print(obj)` shows (DDW uses an **f-string**).\n"
            "- `__repr__` → the unambiguous developer-facing view.\n"
            "- `__eq__` (`==`) and `__lt__` (`<`) → make objects **comparable** and **sortable**.\n"
            "- `__add__` (`+`), `__len__`, `__getitem__` (`[]`) → operator & container behaviour."
        ),
        "technique": "Special technique — define `__lt__` and Python can `sorted()` your objects "
                     "for free; define `__eq__` + `__hash__` and they work as set members and dict keys.",
        "code": (
            "class Fraction:\n"
            "    # ... __init__ sets self._numerator / self._denominator ...\n"
            "    def __str__(self):\n"
            "        return f\"{self._numerator}/{self._denominator}\"\n"
            "\n"
            "    def __eq__(self, other):\n"
            "        return (self._numerator * other._denominator\n"
            "                == other._numerator * self._denominator)\n"
            "\n"
            "    def __lt__(self, other):                     # enables sorting\n"
            "        return (self._numerator * other._denominator\n"
            "                < other._numerator * self._denominator)\n"
            "\n"
            "    def __add__(self, other):                    # enables f1 + f2\n"
            "        n = self._numerator * other._denominator + other._numerator * self._denominator\n"
            "        d = self._denominator * other._denominator\n"
            "        return Fraction(n, d)\n"
            "\n"
            "print(sorted([Fraction(3, 4), Fraction(1, 2)]))  # uses __lt__"
        ),
    },
    {
        "name": "Inheritance & super()",
        "summary": "A subclass reuses and extends a parent class instead of repeating code.",
        "points": (
            "- `class Circle(Shape):` — a Circle **is-a** Shape and inherits its methods.\n"
            "- `super().__init__(...)` runs the **parent's constructor**, so shared setup isn't duplicated.\n"
            "- A subclass can **override** a method to specialise it.\n"
            "- **You've seen this:** every sorter (`BubbleSort`, `QuickSort`, …) in Exercise 1 "
            "subclasses `SortAlgorithm` and calls `super().__init__()`."
        ),
        "code": (
            "class Shape:\n"
            "    def __init__(self, name):\n"
            "        self._name = name\n"
            "\n"
            "    def describe(self):\n"
            "        return f\"{self._name}: area = {self.area():.2f}\"\n"
            "\n"
            "class Circle(Shape):\n"
            "    def __init__(self, radius):\n"
            "        super().__init__(\"Circle\")     # run the parent constructor\n"
            "        self._radius = radius\n"
            "\n"
            "    def area(self):                    # specialise for circles\n"
            "        return 3.14159 * self._radius ** 2\n"
            "\n"
            "print(Circle(2).describe())            # Circle: area = 12.57"
        ),
    },
    {
        "name": "Polymorphism & Abstract methods",
        "summary": "One interface, many implementations — call the same method on different types.",
        "points": (
            "- A base method that raises `NotImplementedError` is an **abstract method**: it *demands* "
            "each subclass supply its own version.\n"
            "- Code can loop over a mixed list and call `.area()` without knowing each exact type — "
            "that's **polymorphism**.\n"
            "- **DDW example:** `SortAlgorithm.sort` raises `NotImplementedError`; each sort implements "
            "it differently, yet the page drives them all through the same interface."
        ),
        "technique": "Special technique — program to the *interface* (the base class), not the concrete "
                     "type. New subclasses slot in with zero changes to the calling code.",
        "code": (
            "class Shape:\n"
            "    def area(self):\n"
            "        raise NotImplementedError(\"subclasses must implement area()\")\n"
            "\n"
            "class Circle(Shape):\n"
            "    def __init__(self, r): self._r = r\n"
            "    def area(self): return 3.14159 * self._r ** 2\n"
            "\n"
            "class Rectangle(Shape):\n"
            "    def __init__(self, w, h): self._w, self._h = w, h\n"
            "    def area(self): return self._w * self._h\n"
            "\n"
            "shapes = [Circle(2), Rectangle(3, 4)]\n"
            "for s in shapes:                       # same call, different behaviour\n"
            "    print(round(s.area(), 2))          # 12.57  then  12"
        ),
    },
    {
        "name": "Class attrs, @classmethod & @staticmethod",
        "summary": "Data and helpers that belong to the class itself, not to any one instance.",
        "points": (
            "- A **class attribute** is shared by every instance — great for constants or counters.\n"
            "- `@classmethod` receives the class (`cls`) — ideal for **alternative constructors** "
            "like `from_string`.\n"
            "- `@staticmethod` receives neither `self` nor `cls` — a plain helper **namespaced** "
            "under the class."
        ),
        "technique": "Special technique — `@classmethod` alternative constructors (e.g. "
                     "`Fraction.from_string('3/4')`) give a class several tidy ways to be built.",
        "code": (
            "class Fraction:\n"
            "    count = 0                          # class attribute: shared by all instances\n"
            "\n"
            "    def __init__(self, numerator, denominator=1):\n"
            "        self._numerator, self._denominator = numerator, denominator\n"
            "        Fraction.count += 1            # every instance bumps the shared counter\n"
            "\n"
            "    @classmethod\n"
            "    def from_string(cls, text):        # alternative constructor\n"
            "        num, den = text.split(\"/\")\n"
            "        return cls(int(num), int(den))\n"
            "\n"
            "    @staticmethod\n"
            "    def is_valid(denominator):         # helper — no instance needed\n"
            "        return denominator != 0\n"
            "\n"
            "f = Fraction.from_string(\"3/4\")        # Fraction(3, 4)\n"
            "print(Fraction.count, Fraction.is_valid(0))   # 1 False"
        ),
    },
]
