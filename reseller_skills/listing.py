"""Honest listing drafter: build a truthful draft you can paste and tighten.

Two layers:
    build_draft()   deterministic skeleton, fully offline, no invention.
    draft_with_llm() optional polish via any OpenAI-compatible endpoint
                    (default: local Ollama, no key). Falls back to the
                    skeleton on any error so you always get something.
"""

from __future__ import annotations

import textwrap

from . import condition as _condition
from . import llm


def build_draft(
    title: str,
    category: str,
    notes: str,
    name_brand: str = "",
    item_props: dict | None = None,
    shipping_note: str = "",
) -> dict:
    """Deterministic, offline listing skeleton. Never invents a fact."""
    grade = _condition.grade_item_notes(notes)
    props = item_props or {}
    prop_lines = [f"{k}: {v}" for k, v in props.items() if str(v).strip()]

    truth_lines = list(grade["disclosures"])
    if not truth_lines and grade["score"] in (2, 1):
        truth_lines = [
            "Disclose: notes suggest significant wear; write out every defect here."
        ]

    body_lines = []
    body_lines.append(f"What you get: one {title}.")
    if name_brand:
        body_lines.append(f"Brand: {name_brand}.")
    body_lines.append(
        f"Condition: {grade['label']} — this is my honest read of the notes, "
        "check the photos."
    )
    if notes.strip():
        body_lines.append("From my notes: " + " ".join(notes.strip().split()))
    if truth_lines:
        body_lines.append("")
        body_lines.append("Full disclosure:")
        body_lines.extend(f"- {t}" for t in truth_lines)
    if prop_lines:
        body_lines.append("")
        body_lines.append("Details:")
        body_lines.extend(f"- {p}" for p in prop_lines)
    if shipping_note:
        body_lines.append("")
        body_lines.append(f"Shipping: {shipping_note}")

    body = "\n".join(body_lines)

    punchy = f"[{grade['label']}] {title}" if grade["score"] in (1, 2, 3) else title
    before = grade["score"] not in (4, 5)

    tips = [
        "Title style that performs: [Condition] + Brand + Model + Size + 1 key word.",
        "Put your worst flaw on its own line, centered, so nobody misses it.",
        "Photograph every disclosed defect. One defect photo beats ten hero shots.",
        "Never write 'perfect' unless it is. Buyers forgive flaws, not surprises.",
    ]

    return {
        "title": punchy,
        "title_needs_condition_prefix": before,
        "category_suggestion": category or "",
        "body": body,
        "grade": grade["score"],
        "grade_label": grade["label"],
        "disclosures": truth_lines,
        "checklist": grade["checklist"],
        "tips": tips,
    }


def draft_with_llm(
    title: str,
    category: str,
    notes: str,
    *,
    base_url: str = llm.DEFAULT_BASE_URL,
    model: str = llm.DEFAULT_MODEL,
) -> dict:
    """Skeleton first (always), then an optional LLM rewrite of the body."""
    draft = build_draft(title, category, notes)
    skeleton = draft["body"]
    system = (
        "You are a careful marketplace copywriter. You may only use facts given "
        "to you. You never invent features, measurements, authenticity, or "
        "condition details. Invented claims are forbidden."
    )
    prompt = textwrap.dedent(f"""\
        Rewrite this listing body so it's warm, honest, and scannable.
        Keep every disclosed flaw and add nothing new. Plain sentences, no emojis,
        no ALL CAPS, no marketing fluff, max 150 words.

        Title: {title}
        Draft: {skeleton}
    """)
    try:
        polished = llm.chat(prompt, base_url=base_url, model=model, system=system)
    except llm.LlmError as exc:
        draft["llm"] = {"used": False, "error": str(exc)}
        draft["body"] = skeleton
    else:
        draft["llm"] = {"used": True, "base_url": base_url, "model": model}
        draft["body"] = polished.strip() or skeleton
    return draft
