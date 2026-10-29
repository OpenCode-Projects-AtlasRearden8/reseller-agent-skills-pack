"""Red-flag buyer asks: scan a buyer's message before you answer.

Offline, deterministic string matching. A hit is a *warning*, not a crime,
but several hits together usually mean: politely decline and move on.
"""

from __future__ import annotations

from dataclasses import dataclass

_FLAG_RULES: list[tuple[str, str, list[str]]] = [
    (
        "overpayment",
        "high",
        [
            "overpay", "more than the price", "extra back", "send the difference",
            "refund the extra", "i'll send extra", "remind me of the balance",
        ],
    ),
    (
        "take-it-off-platform",
        "high",
        [
            "off ebay", "off etsy", "off the app", "outside the platform", "directly",
            "let's do this privately", "skip the fee", "email me at", "text me at",
        ],
    ),
    (
        "risky-pay-methods",
        "high",
        [
            "zelle", "venmo", "cashapp", "cash app", "western union", "moneygram",
            "gift card", "google play card", "itunes card", "crypto", "bitcoin",
            "usdt", "money order",
        ],
    ),
    (
        "address-switch",
        "high",
        [
            "ship to a different", "different address", "my nephew's address",
            "my office address", "forward it to", "reship", "re-ship", "my agent will pick",
            "my mover", "my courier",
        ],
    ),
    (
        "bypass-protections",
        "high",
        [
            "mark as gift", "declare a lower", "lower the value", "don't include a receipt",
            "turn off authentication", "skip authentication", "remove authentication",
            "no tracking needed",
        ],
    ),
    (
        "urgency-pressure",
        "medium",
        [
            "right now", "cash today", "selling tomorrow", "first person who says yes",
            "hold it without paying", "in the next hour",
        ],
    ),
    (
        "vague-buyer",
        "low",
        [
            "is this available", "still available", "whats your lowest",
            "what's your lowest", "how low can you go", "final answer",
        ],
    ),
    (
        "overseas-wire-plot",
        "high",
        [
            "my secretary", "my client will pay", "seafarer", "on deployment",
            "shipping company will contact you", "escrow fee",
        ],
    ),
]


def scan_buyer_message(message: str) -> dict:
    """Scan a buyer message; return sorted flags with plain-English guidance."""
    lower = (message or "").lower()
    flags = []
    for rule_id, severity, phrases in _FLAG_RULES:
        hits = [p for p in phrases if p in lower]
        if hits:
            flags.append(
                {
                    "flag_id": rule_id,
                    "severity": severity,
                    "matched": hits,
                    "say_this": _script(rule_id),
                }
            )
    _rank = {"high": 3, "medium": 2, "low": 1}
    flags.sort(key=lambda f: -_rank[f["severity"]])
    return {
        "flags": flags,
        "verdict": _verdict(flags),
        "note": (
            "These are patterns, not proof. Scammers copy real buyers' words; a single "
            "medium/low hit is usually fine. Two or more high hits: decline politely "
            "and relist. On-platform, buyer-pays-first, ship-after-payment. Never hand "
            "out personal payment details."
        ),
    }


def _verdict(flags) -> str:
    if any(f["severity"] == "high" for f in flags):
        return "stop: at least one high-severity pattern matched; decline or proceed on-platform only"
    if any(f["severity"] == "medium" for f in flags):
        return "caution: pressure language present; require online payment before shipping"
    return "clear: no strong scam patterns found"


def _script(rule_id: str) -> str:
    scripts = {
        "overpayment": (
            "\"Thanks for the interest. I only sell through the platform at the listed "
            "price, and I refund overages to the original payment — but I'd rather not "
            "handle this off-platform.\""
        ),
        "take-it-off-platform": (
            "\"I keep all transactions on the platform. It protects us both.\""
        ),
        "risky-pay-methods": (
            "\"I only accept the platform's checkout. No direct transfers, gift cards, or crypto.\""
        ),
        "address-switch": (
            "\"I ship only to the address shown on the paid order.\""
        ),
        "bypass-protections": (
            "\"I ship exactly as the platform requires, with tracking and a normal label.\""
        ),
        "urgency-pressure": (
            "\"It's first paid, first sold. Once the order is placed, I will ship.\""
        ),
        "vague-buyer": (
            "\"Yes, it's available. Price is firm unless noted.\" (Haggle is normal; "
            "keep it on-platform and in writing.)"
        ),
        "overseas-wire-plot": (
            "\"I only sell through the platform and ship only once payment clears.\""
        ),
    }
    return scripts.get(rule_id, "Decline anything that feels off; keep it on-platform.")
