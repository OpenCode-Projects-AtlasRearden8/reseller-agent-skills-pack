"""Price floor math: the least you can charge and still keep your target.

Fee model (all offline, all plain arithmetic):
    price - marketplace_fee - payment_fee - direct_costs = your pocket

    marketplace_fee = price * marketplace_pct          (e.g. eBay 13%)
    payment_fee     = price * payment_pct + payment_fixed (e.g. 2.9% + $0.30)

    direct_costs     = shipping + packaging + other one-off costs
    target_net       = what you want left in your pocket

    net = price * (1 - marketplace_pct - payment_pct) - payment_fixed - direct_costs
    =>  price = (target_net + payment_fixed + direct_costs) / (1 - marketplace_pct - payment_pct)
"""

from __future__ import annotations


def price_floor(
    target_net: float,
    marketplace_pct: float = 0.13,
    payment_pct: float = 0.029,
    payment_fixed: float = 0.30,
    shipping: float = 0.0,
    packaging: float = 0.0,
    other_costs: float = 0.0,
) -> dict:
    """Return the minimum list price to clear target_net after fees and costs."""
    _validate(
        target_net=target_net,
        marketplace_pct=marketplace_pct,
        payment_pct=payment_pct,
        payment_fixed=payment_fixed,
        shipping=shipping,
        packaging=packaging,
        other_costs=other_costs,
    )
    den = 1.0 - marketplace_pct - payment_pct
    numerator = target_net + payment_fixed + shipping + packaging + other_costs
    floor = numerator / den
    # Listings are usually in cents; round UP so the floor is never understated.
    floor_cents = _ceil_cents(floor)
    actual_net = _net_at(
        floor_cents, marketplace_pct, payment_pct, payment_fixed,
        shipping, packaging, other_costs,
    )
    return {
        "floor_price": floor_cents,
        "floor_unrounded": round(floor, 2),
        "target_net": round(target_net, 2),
        "realized_net_at_floor": round(actual_net, 2),
        "fee_pct_total": round(den and (marketplace_pct + payment_pct), 4),
        "breakdown": {
            "marketplace_fee": round(floor_cents * marketplace_pct, 2),
            "payment_fee": round(floor_cents * payment_pct + payment_fixed, 2),
            "shipping": round(shipping, 2),
            "packaging": round(packaging, 2),
            "other_costs": round(other_costs, 2),
        },
        "advice": _advice(actual_net, target_net),
    }


def _net_at(price, m_pct, p_pct, p_fixed, ship, pack, other):
    return price * (1.0 - m_pct - p_pct) - p_fixed - ship - pack - other


def _ceil_cents(x: float) -> float:
    import math
    return math.ceil(x * 100.0) / 100.0


def _validate(**kw) -> None:
    target = kw["target_net"]
    if isinstance(target, (int, float)) and target < 0:
        raise ValueError("target_net cannot be negative; you should never plan to lose money on purpose.")
    for name in ("marketplace_pct", "payment_pct"):
        v = kw[name]
        if not 0.0 <= v <= 0.90:
            raise ValueError(f"{name} must be between 0 and 0.90, got {v}")
    for name in ("payment_fixed", "shipping", "packaging", "other_costs"):
        v = kw[name]
        if v < 0:
            raise ValueError(f"{name} cannot be negative")
    if 1.0 - kw["marketplace_pct"] - kw["payment_pct"] <= 0.0:
        raise ValueError("fees total 100% or more of the sale price; no price works")


def _advice(net, target) -> str:
    if net >= target:
        return (
            "This is your floor: list at or above it. Listing lower eats your profit; "
            "a slow sale at the floor beats a fast sale at a loss."
        )
    return "Listing below this price loses money after fees."
