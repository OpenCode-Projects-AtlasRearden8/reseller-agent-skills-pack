---
name: price-floor
description: Compute the lowest listing price that still leaves the target profit after marketplace and payment fees plus costs. Offline math.
---

# Skill: Price floor with fees

You are protecting the seller's pocket. Fees eat a surprising slice; this
skill does that arithmetic once, correctly, so pricing is never a guess.

## How to use

```bash
python -m reseller_skills price-floor --target-net 40 --shipping 6.50 --packaging 0.75
```

Defaults match a typical eBay-plus-payment setup (13% + 2.9% + $0.30). Pass
different percentages when the venue is different:

```bash
python -m reseller_skills price-floor --target-net 40 --marketplace-pct 0.15 --payment-pct 0
```

## Reading the output

- `floor_price` — the least you may list at. Rounded up to the cent.
- `realized_net_at_floor` — what actually lands in the pocket at that price.
- `breakdown` — each fee in dollars, so you can explain it to a beginner.

## Plain-English rule

If a buyer offers $10 under the floor, the honest answer is: "That's below
what the fees leave me. I can do [floor] or you can pay [floor + 10%]."
Never dip under the floor "just to move it" unless you are consciously
deciding to sell at the floor anyway — a loss is not a sale.

## Ends-can-meet check

If the floor comes out above comparable sold listings, the item is not
worth shipping — say that kindly and suggest a bulk lot or a venue with
lower fees instead.
