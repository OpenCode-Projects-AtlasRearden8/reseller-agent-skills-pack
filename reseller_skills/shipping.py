"""Shipping class suggestion: plain rules to pick a carrier service.

Offline, deterministic, US-domestic lean (USPS + ground). Always double-check
the final quote on the carrier's site; these are starting points, not rates.
"""

from __future__ import annotations

_OZ_PER_LB = 16.0
_MEDIA_WORDS = [
    "book", "books", "dvd", "cd", "vinyl", "record", "blu-ray", "bluray",
    "game disc", "instruction manual", "sheet music", "magazine", "hardcover",
    "paperback",
]


def suggest_shipping(
    weight_lb: float | None = None,
    weight_oz: float | None = None,
    length_in: float | None = None,
    width_in: float | None = None,
    height_in: float | None = None,
    item_type: str = "",
    declared_value: float | None = None,
) -> dict:
    """Suggest a shipping class/service from weight, dims, and item type."""
    lb = weight_lb
    if lb is None and weight_oz is not None:
        lb = weight_oz / _OZ_PER_LB
    item = (item_type or "").lower()

    cautions: list[str] = []
    if "battery" in item or "lithium" in item:
        cautions.append(
            "Lithium batteries: these often can't fly in some services and have "
            "label rules. Ground service and a sealed-terminal check come first."
        )
    if any(w in item for w in ("glass", "ceramic", "porcelain")):
        cautions.append(
            "Fragile: double-box, pad every face, and note it in the listing photos."
        )
    if "perfume" in item or "aerosol" in item or "lighter" in item:
        cautions.append("Hazardous/flammable: USPS has strict ground-only rules; check before listing.")

    is_media = any(w in item for w in _MEDIA_WORDS)

    if lb is None:
        no_weight_note = "Not enough info: give a packed weight (item + box)."
        return {
            "suggestion": None,
            "note": no_weight_note,
            "reasons": [],
            "cautions": cautions,
            "tip": (
                "Free boxes beat $1 savings; USPS flat-rate can win on dense, heavy, "
                "small items, while your own padded envelope usually wins on light, small ones."
            ),
        }

    dim_issues = []
    if all(v is not None for v in (length_in, width_in, height_in)):
        dim_issues = _dim_notes(float(length_in), float(width_in), float(height_in))

    decision_class, reasons = _decide(lb, is_media, dim_issues, declared_value, item)

    return {
        "suggestion": decision_class,
        "note": None,
        "reasons": reasons,
        "cautions": cautions,
        "tip": (
            "Free boxes beat $1 savings; USPS flat-rate can win on dense, heavy, "
            "small items, while your own padded envelope usually wins on light, small ones."
        ),
    }


def _decide(lb: float, is_media: bool, dim_issues: list, declared_value, item: str):
    reasons = []
    oversized = bool(dim_issues)

    if lb <= 0.75 and not oversized:
        reasons.append("Under ~12 oz packed: cheapest lane is a poly mailer, not a box.")
        return "USPS Ground Advantage (letter/large-envelope tier, poly mailer)", reasons

    if is_media and lb <= 70 and not any(
        k in item for k in ("board game", "encyclop", "yearbook", "photos", "art print")
    ):
        reasons.append("Qualifying media (books, discs, manuals) is slow but very cheap in Media Mail.")
        return "USPS Media Mail (if it qualifies), else Ground Advantage", reasons

    if lb <= 5 and not oversized:
        reasons.append("Small dense parcel: your own box with Ground Advantage usually wins.")
        return "USPS Ground Advantage (own box) — compare 5 lb flat rate", reasons

    if lb <= 20 and not oversized:
        reasons.append("Mid-weight: Priority Mail flat-rate boxes avoid any dim-weight math.")
        return "USPS Priority Mail (flat rate if dense and small)", reasons

    if oversized:
        reasons.append("Oversized dims: cubic/oversize rules and dim weight apply.")
        if lb <= 70:
            return "USPS Priority Mail Large — get a real quote", reasons
        return "Freight or 'Parcel Select Ground - large item' — quote it before listing", reasons

    reasons.append("Heavy parcel: check 'oversized/heavy-tier' rates before you promise shipping.")
    if lb <= 70:
        return "USPS Ground Advantage / Parcel Select (heavy tier) — quote it", reasons
    return "Freight (over 70 lb needs carrier-specific handling)", reasons


def _dim_notes(l: float, w: float, h: float) -> list:
    issues = []
    if max(l, w, h) > 30:
        issues.append("any side over 30 inches is oversize for most services")
    # USPS: length = longest side, girth = 2 * (width + height) of the two shorter sides.
    length = max(l, w, h)
    girth = 2.0 * ((l + w + h) - length)
    combined = length + girth
    if combined > 108:
        issues.append("length + girth exceeds USPS 108-inch limit")
    elif combined > 96:
        issues.append("length + girth is in the 96-108 inch 'big surcharge' zone")
    return issues
