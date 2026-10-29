import pytest

from reseller_skills import listing
from reseller_skills.llm import LlmError, chat


def test_skeleton_offline_contains_notes_and_disclosure():
    d = listing.build_draft(
        title="Kenwood KDC-BT282U car stereo",
        category="Electronics",
        notes="works great, one small scratch on faceplate",
        name_brand="Kenwood",
        item_props={"Wiring harness": "included", "Year": "2019"},
        shipping_note="Ships tracked in a padded box.",
    )
    assert "Kenwood" in d["body"]
    assert "scratch" in d["body"]
    assert "works great" in d["body"].lower()
    assert "Wiring harness: included" in d["body"]
    assert d["grade"] == 3
    assert any("scratch" in t for t in d["disclosures"])


def test_worse_items_need_condition_prefix():
    d = listing.build_draft("Old camera", "Electronics", "lens cracked, sd door broken")
    assert d["title"].startswith("[")
    assert d["grade"] == 1


def test_no_fabrication_from_empty_notes():
    d = listing.build_draft("Plain mug", "Home", "")
    assert d["grade"] is None
    assert "one Plain mug" in d["body"]


def test_grade_1_or_2_gets_disclosure_placeholder():
    d = listing.build_draft("Old camera", "Electronics", "heavy wear, works? unsure")
    assert d["disclosures"], "low grade without keyword disclosures needs a nudge"


def test_llm_chat_rejects_api_keys():
    with pytest.raises(LlmError):
        chat("hello", api_key="sk-nope")


def test_llm_chat_fails_cleanly_when_no_server():
    # Nothing on this port; must raise LlmError, not urllib's raw error.
    with pytest.raises(LlmError):
        chat("hello", base_url="http://127.0.0.1:9/v1", timeout=2)


def test_draft_with_llm_falls_back_to_skeleton():
    d = listing.draft_with_llm(
        "Plain mug", "Home", "", base_url="http://127.0.0.1:9/v1"
    )
    assert d["llm"]["used"] is False
    assert "error" in d["llm"]
    assert d["body"], "fallback body must exist"
