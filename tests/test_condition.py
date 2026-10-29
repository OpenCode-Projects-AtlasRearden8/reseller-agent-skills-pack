import pytest

from reseller_skills.condition import grade_item_notes


def test_clean_working_item_is_good():
    r = grade_item_notes("works fine, light scuffs on the base, no cracks")
    assert r["score"] == 3 or r["score"] == 4
    assert r["label"]


def test_broken_item_is_parts():
    r = grade_item_notes("screen cracked, does not work, unit won't turn on")
    assert r["score"] == 1
    assert r["label"] == "For Parts or Not Working"
    assert any("crack" in d for d in r["disclosures"])


def test_sealed_item_is_new():
    r = grade_item_notes("brand new in box, factory sealed, never opened")
    assert r["score"] == 5
    assert r["label"] == "New"


def test_conflicting_seal_downgrades():
    r = grade_item_notes("sealed box but I opened it to check, only used once")
    assert r["score"] < 5
    assert any("conflicting cue" in s for s in r["signals"])


def test_empty_notes_is_none_not_crash():
    r = grade_item_notes("   ")
    assert r["score"] is None
    assert r["confidence"] == "none"


def test_disclosures_list_mentioned_defects():
    r = grade_item_notes("small dent on lid, rust on one screw, otherwise fine")
    joined = " ".join(r["disclosures"])
    assert "dent" in joined and "rust" in joined


def test_score_never_leaves_range():
    r = grade_item_notes(
        "broken shattered cracked torn stained warped dented rust mold leak fried"
    )
    assert r["score"] == 1
