"""Condition grading: turn messy item notes into an honest condition grade.

Deterministic and offline. No LLM needed.

Grades (1-5) with eBay-style labels:
    5 New            sealed, unopened, pristine
    4 Like New       barely used, no marks worth mentioning
    3 Good           clearly used, normal wear, works as it should
    2 Fair           visible wear, light problems you must disclose
    1 Parts/Damaged  broken, missing pieces, does not work
"""

from __future__ import annotations

import re

GRADE_LABELS = {
    5: "New",
    4: "Like New",
    3: "Good (used)",
    2: "Fair (heavy wear)",
    1: "For Parts or Not Working",
}

# Words that scream damage. Weight trains the score down.
_DAMAGING = [
    ("not working", 6), ("doesn't work", 6), ("does not work", 6), ("won't turn on", 6),
    ("broken", 6), ("shattered", 6),
    ("smashed", 6), ("nonfunctional", 6), ("doesn't power", 6), ("no power", 5),
    ("doesn't read", 5), ("won't boot", 5), ("jammed", 5),
    ("crack", 4), ("shatter", 4), ("tear", 4), ("torn", 4), ("rip", 4), ("ripped", 4),
    ("dent", 4), ("dented", 4), ("stain", 4), ("stained", 4), ("warped", 4),
    ("missing part", 5), ("missing pieces", 5), ("missing cover", 4), ("missing battery cover", 4),
    ("water damage", 6), ("water damaged", 6), ("corrosion", 5), ("corroded", 5),
    ("rust", 5), ("mold", 5), ("smoke smell", 4), ("pet hair", 2), ("pet stains", 4),
    ("leak", 4), ("leaking", 4), ("fried", 5), ("snapped", 5), ("split", 4),
    ("heavy wear", 2), ("worn out", 3), (" faded", 1),  # leading spaces keep 'faded' word-safe
    ("scratch", 0.5), ("scuff", 0.5), ("chip", 1.5), ("peeling", 2.5),
]
_DAMAGE_WEIGHTS = {kw: w for kw, w in _DAMAGING if w > 0}

# Words that push the grade up.
_POSITIVE = [
    "sealed", "unopened", "new in box", "used once", "like new", "mint",
    "pristine", "excellent condition", "just tested", "tested working",
    "no marks", "no scratches", "no dents", "no stains", "freshly",
]

_WEAKEN = [
    "other than that", "apart from that", "works fine for its age", "roughly",
    "well used", "lovingly used", "perfect for parts", "condition unknown",
]

# Phrases like "no cracks" must not be read as "cracks".
_NEGATION_PREFIXES = ["no ", "not ", "without ", "never ", "zero "]

# Words that unambiguously mean "still sealed".
_SEALED_OK = [
    "unopened", "never opened", "not opened", "never been opened",
    "still sealed", "factory sealed", "brand new", "never used", "unused",
]

_TRUTH_TRAPS = [
    ("works perfectly, just", "half-honest phrase; disclose the rest of that sentence"),
    ("one small issue", "name the issue plainly in the listing"),
    ("minor flaw only", "a flaw is a flaw; list it in its own line"),
    ("too small to matter", "buyers decide what matters; disclose it"),
]


def grade_item_notes(notes: str) -> dict:
    """Grade an item from free-form condition notes.

    Returns a dict with score, label, signals, disclosures, and an
    honesty checklist. Never invents details that are not in the notes.
    """
    if not notes or not notes.strip():
        return {
            "score": None,
            "label": None,
            "signals": [],
            "disclosures": [],
            "checklist": [
                "No notes provided. Before listing, write down: does it work, "
                "every visible defect, every missing piece, why you're selling.",
            ],
            "confidence": "none",
        }

    text = " " + re.sub(r"\s+", " ", notes.lower()).strip() + " "

    def _is_negated(needle: str) -> bool:
        for prefix in _NEGATION_PREFIXES:
            if prefix + needle in text:
                return True
        return False

    def _has(needle: str) -> bool:
        return needle in text and not _is_negated(needle)

    signals: list[str] = []
    score = 3.0
    hits = 0

    for kw, weight in _DAMAGE_WEIGHTS.items():
        if _has(kw):
            signals.append(f"damage cue: '{kw}'")
            score -= weight
            hits += 1

    for kw in _POSITIVE:
        if _has(kw):
            signals.append(f"good cue: '{kw}'")
            score += 0.5
            hits += 1

    for kw in _SEALED_OK:
        if _has(kw):
            signals.append(f"sealed cue: '{kw}'")
            score += 1.0
            hits += 1

    for kw in _WEAKEN:
        if _has(kw):
            signals.append(f"hedge cue: '{kw}'")
            score -= 0.25
            hits += 1

    # "sealed" with "opened" in the same sentence is a classic mix-up.
    cleaned = text
    for ok in _SEALED_OK:
        cleaned = cleaned.replace(ok, " ")
    if "sealed" in cleaned and ("opened" in cleaned or "used" in cleaned):
        signals.append("conflicting cue: sealed but opened/used -> treat as opened")
        score -= 1.5
        hits += 1

    score = max(1.0, min(5.0, score))
    if score <= 1.6:
        clamped = 1
    elif score <= 2.4:
        clamped = 2
    elif score <= 3.4:
        clamped = 3
    elif score <= 4.4:
        clamped = 4
    else:
        clamped = 5

    disclosures = []
    for kw in _DAMAGE_WEIGHTS:
        if _has(kw):
            disclosure = f"Disclose: the notes mention '{kw}'."
            if disclosure not in disclosures:
                disclosures.append(disclosure)

    checklist = [
        "State plainly whether the item works, in the first two lines.",
        "List every defect as its own bullet, with its location.",
        "Photograph the worst spot; do not bury it in a group photo.",
        "If you would not be happy receiving it at this grade, lower the grade.",
    ]
    if clamped <= 2:
        checklist.append("Mark as 'For Parts or Not Working' unless fully functional.")

    confidence = "low" if hits <= 1 else ("medium" if hits <= 3 else "high")

    return {
        "score": clamped,
        "label": GRADE_LABELS[clamped],
        "signals": signals,
        "disclosures": disclosures,
        "checklist": checklist,
        "confidence": confidence,
    }
