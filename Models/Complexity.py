"""Question generator for the time & space complexity quiz (Exercise 2).

Two kinds of randomly-generated questions, both purely data — the Streamlit page
in ``pages/2_Exercise_2.py`` renders and grades them:

1. **code**  — show a short function, ask for its **time** or **space**
   complexity as a single-answer multiple choice.
2. **relationship** — given two functions ``f(n)`` and ``g(n)``, select *every*
   asymptotic notation N (from O, o, Θ, Ω) for which ``f ∈ N(g)``.

Every question carries a short teaching ``explanation`` so a wrong (or right)
answer still explains *why*. Nothing here imports Streamlit, so the whole bank
is unit-testable in isolation.
"""
import random

# ── The classic complexity ladder, slowest-growing → fastest-growing ─────────
# Used both as the MCQ option pool for code questions and as the ordered set of
# growth classes for relationship questions (index == asymptotic rank).
LADDER = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n²)", "O(n³)", "O(2ⁿ)"]


# ── Code-snippet bank ────────────────────────────────────────────────────────
# Each snippet declares BOTH its time and space complexity plus a plain-English
# reason for each, so a single snippet can seed either a time or a space question.
SNIPPETS = [
    {
        "title": "Return the first element",
        "code": "def first(arr):\n    return arr[0]",
        "time": "O(1)", "space": "O(1)",
        "time_explain": "A single index lookup runs in the same time no matter how "
                        "long `arr` is — constant time.",
        "space_explain": "No new data structure is allocated; only the input is "
                         "referenced — constant extra space.",
    },
    {
        "title": "Sum every element",
        "code": "def total(arr):\n    s = 0\n    for x in arr:\n        s += x\n    return s",
        "time": "O(n)", "space": "O(1)",
        "time_explain": "The loop runs once per element, so work grows linearly "
                        "with n.",
        "space_explain": "Only the accumulator `s` is stored, regardless of n — "
                         "constant extra space.",
    },
    {
        "title": "Double every element into a new list",
        "code": "def doubled(arr):\n    out = []\n    for x in arr:\n        out.append(x * 2)\n    return out",
        "time": "O(n)", "space": "O(n)",
        "time_explain": "One append per element → linear time.",
        "space_explain": "`out` grows to hold n elements, so the extra memory scales "
                         "with n — linear space.",
    },
    {
        "title": "Count matching pairs",
        "code": ("def count_pairs(arr):\n    count = 0\n    for i in range(len(arr)):\n"
                 "        for j in range(i + 1, len(arr)):\n            if arr[i] == arr[j]:\n"
                 "                count += 1\n    return count"),
        "time": "O(n²)", "space": "O(1)",
        "time_explain": "Every element is compared with every later element — about "
                        "n²/2 comparisons, which is O(n²).",
        "space_explain": "Only a single counter is kept — constant extra space.",
    },
    {
        "title": "Binary search in a sorted list",
        "code": ("def contains(sorted_arr, target):\n    lo, hi = 0, len(sorted_arr) - 1\n"
                 "    while lo <= hi:\n        mid = (lo + hi) // 2\n"
                 "        if sorted_arr[mid] == target:\n            return True\n"
                 "        if sorted_arr[mid] < target:\n            lo = mid + 1\n"
                 "        else:\n            hi = mid - 1\n    return False"),
        "time": "O(log n)", "space": "O(1)",
        "time_explain": "Each step halves the search range, so it finishes in about "
                        "log₂(n) steps — logarithmic time.",
        "space_explain": "Only a few index variables are used — constant extra space.",
    },
    {
        "title": "Detect a duplicate by sorting first",
        "code": ("def has_duplicate(arr):\n    s = sorted(arr)\n"
                 "    for i in range(1, len(s)):\n        if s[i] == s[i - 1]:\n"
                 "            return True\n    return False"),
        "time": "O(n log n)", "space": "O(n)",
        "time_explain": "`sorted()` costs O(n log n), which dominates the single "
                        "O(n) scan that follows.",
        "space_explain": "`sorted()` returns a brand-new list of n elements — linear "
                         "extra space.",
    },
    {
        "title": "Build an n × n matrix",
        "code": ("def build_matrix(n):\n    matrix = []\n    for i in range(n):\n"
                 "        row = []\n        for j in range(n):\n"
                 "            row.append(i * j)\n        matrix.append(row)\n    return matrix"),
        "time": "O(n²)", "space": "O(n²)",
        "time_explain": "The nested loops execute n × n times → quadratic time.",
        "space_explain": "The result stores n rows of n values = n² cells — quadratic "
                         "space.",
    },
    {
        "title": "Naïve recursive Fibonacci",
        "code": ("def fib(n):\n    if n < 2:\n        return n\n"
                 "    return fib(n - 1) + fib(n - 2)"),
        "time": "O(2ⁿ)", "space": "O(n)",
        "time_explain": "Each call spawns two more calls with no memoisation, so the "
                        "call count roughly doubles each level — exponential time.",
        "space_explain": "Only one root-to-leaf path is on the call stack at a time, "
                         "and it is at most n deep — linear space.",
    },
    {
        "title": "Triple nested loop",
        "code": ("def triples(arr):\n    count = 0\n    for i in arr:\n        for j in arr:\n"
                 "            for k in arr:\n                count += 1\n    return count"),
        "time": "O(n³)", "space": "O(1)",
        "time_explain": "Three loops each over n elements → n³ iterations, cubic time.",
        "space_explain": "Just one counter is stored — constant extra space.",
    },
    {
        "title": "Halving work inside a linear loop",
        "code": ("def work(arr):\n    n = len(arr)\n    steps = 0\n"
                 "    for i in range(n):\n        j = n\n        while j > 1:\n"
                 "            j //= 2\n            steps += 1\n    return steps"),
        "time": "O(n log n)", "space": "O(1)",
        "time_explain": "The outer loop runs n times; the inner loop halves j each "
                        "time, so it runs log n times — together n · log n.",
        "space_explain": "Only counters are used — constant extra space.",
    },
    {
        "title": "Collect the distinct values",
        "code": ("def unique(arr):\n    seen = set()\n    for x in arr:\n"
                 "        seen.add(x)\n    return list(seen)"),
        "time": "O(n)", "space": "O(n)",
        "time_explain": "Each element is added to the set once (O(1) average per "
                        "add) → linear time overall.",
        "space_explain": "In the worst case every element is distinct, so the set "
                         "holds up to n items — linear space.",
    },
    {
        "title": "Look at the middle element",
        "code": "def midpoint(arr):\n    n = len(arr)\n    return arr[n // 2] if n else None",
        "time": "O(1)", "space": "O(1)",
        "time_explain": "One length check and one index lookup — constant time, "
                        "independent of n.",
        "space_explain": "No extra structure is built — constant space.",
    },
]


# ── Growth classes for relationship questions ────────────────────────────────
# Index == asymptotic rank (slowest-growing first). Each class carries a few
# equivalent surface forms (same Θ-class, different coefficients / lower-order
# terms) so the same order can be shown two visibly-different ways.
GROWTH = [
    ("constant",      ["7", "25", "100"]),
    ("logarithmic",   ["log n", "3 log n", "log n + 5"]),
    ("linear",        ["n", "2n + 3", "n + 12"]),
    ("linearithmic",  ["n log n", "4n log n", "2n log n + n"]),
    ("quadratic",     ["n²", "3n² + n", "n² + 6n + 9"]),
    ("cubic",         ["n³", "2n³", "n³ + n²"]),
    ("exponential",   ["2ⁿ", "2ⁿ + n³"]),
]

# The four notations the quiz asks about, with human-readable descriptions.
NOTATIONS = [
    ("O", "O(g) — grows no faster than g (upper bound)"),
    ("o", "o(g) — grows strictly slower than g (ratio f/g → 0)"),
    ("Θ", "Θ(g) — grows at the same rate as g (tight bound)"),
    ("Ω", "Ω(g) — grows no slower than g (lower bound)"),
]
NOTATION_LABELS = {sym: label for sym, label in NOTATIONS}
LABEL_TO_SYMBOL = {label: sym for sym, label in NOTATIONS}


def _mc_options(answer, rng, k=4):
    """Return ``answer`` plus up to ``k-1`` distinct distractors from LADDER, shuffled."""
    distractors = [c for c in LADDER if c != answer]
    rng.shuffle(distractors)
    options = [answer] + distractors[: max(0, k - 1)]
    rng.shuffle(options)
    return options


def make_code_question(rng):
    """A 'what is the complexity of this code?' single-answer MCQ."""
    snippet = rng.choice(SNIPPETS)
    dimension = rng.choice(["time", "space"])
    answer = snippet[dimension]
    explanation = snippet[f"{dimension}_explain"]
    return {
        "kind": "code",
        "title": snippet["title"],
        "dimension": dimension,
        "code": snippet["code"],
        "prompt": f"What is the **{dimension} complexity** of this function?",
        "options": _mc_options(answer, rng),
        "answer": answer,
        "explanation": f"**{answer}** — {explanation}",
    }


def _relationship_explanation(f, g, category):
    reminder = (
        "\n\n*Reminder (comparing f to g):* "
        "**O** = grows no faster · **o** = strictly slower · "
        "**Θ** = same rate · **Ω** = grows no slower."
    )
    if category == "slower":
        verdict = (f"**{f}** grows strictly slower than **{g}**, so "
                   "f ∈ O(g) ✓ and f ∈ o(g) ✓, but f ∉ Θ(g) ✗ and f ∉ Ω(g) ✗.")
    elif category == "same":
        verdict = (f"**{f}** and **{g}** grow at the same rate, so f ∈ Θ(g) ✓ — which "
                   "also makes f ∈ O(g) ✓ and f ∈ Ω(g) ✓ — but f ∉ o(g) ✗ "
                   "(a tight bound is never a *strict* upper bound).")
    else:  # faster
        verdict = (f"**{f}** grows strictly faster than **{g}**, so f ∈ Ω(g) ✓ only. "
                   "It is not bounded above by g, so f ∉ O(g) ✗ and f ∉ o(g) ✗, and it "
                   "is not the same rate, so f ∉ Θ(g) ✗.")
    return verdict + reminder


def make_relationship_question(rng):
    """A 'select every notation N such that f ∈ N(g)' multi-answer question."""
    category = rng.choice(["slower", "same", "faster"])
    if category == "same":
        rank = rng.randrange(len(GROWTH))
        forms = GROWTH[rank][1]
        f_disp, g_disp = rng.sample(forms, 2)
        correct = {"O", "Θ", "Ω"}
    else:
        rf, rg = rng.sample(range(len(GROWTH)), 2)
        if category == "slower" and rf > rg:
            rf, rg = rg, rf
        if category == "faster" and rf < rg:
            rf, rg = rg, rf
        f_disp = rng.choice(GROWTH[rf][1])
        g_disp = rng.choice(GROWTH[rg][1])
        correct = {"O", "o"} if category == "slower" else {"Ω"}
    return {
        "kind": "relationship",
        "title": "Classify the growth relationship",
        "f": f_disp,
        "g": g_disp,
        "prompt": (f"Given **f(n) = {f_disp}** and **g(n) = {g_disp}**, select **every** "
                   "notation N for which **f(n) ∈ N(g(n))**."),
        "options": [label for _, label in NOTATIONS],
        "correct": correct,
        "explanation": _relationship_explanation(f_disp, g_disp, category),
    }


def new_question(rng=None):
    """Return a fresh random question (either kind, ~50/50)."""
    rng = rng or random.Random()
    if rng.random() < 0.5:
        return make_code_question(rng)
    return make_relationship_question(rng)


def is_correct(question, response):
    """Grade a ``response`` against ``question``.

    - code:         ``response`` is the chosen option string.
    - relationship: ``response`` is an iterable of selected option *labels*.
    """
    if question["kind"] == "code":
        return response == question["answer"]
    selected = {LABEL_TO_SYMBOL.get(label, label) for label in (response or [])}
    return selected == set(question["correct"])
