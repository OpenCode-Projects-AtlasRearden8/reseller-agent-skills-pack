---
name: red-flag-asks
description: Scan a buyer's message for scam patterns (overpayment, off-platform pay, address switches) and give ready-made replies. Offline.
---

# Skill: Flag red-flag buyer asks

You are the bouncer. Read the buyer's message, run the scanner, and reply
politely-firm using the ready-made scripts.

## How to use

```bash
python -m reseller_skills red-flag-asks --message "Can you take Zelle? I'll send extra for shipping to my nephew's address"
```

## Verdicts

- `stop` (high severity) — decline or continue on-platform only. Two or more
  high hits = decline outright.
- `caution` (medium) — pressure language; payment must post online and clear
  before mailing.
- `clear` — proceed normally. Haggle is not a scam.

## The patterns (why they work)

- Overpayment + "send the difference back" = a fake check that bounces after
  you refund real money.
- Off-platform payment (Zelle, Venmo, crypto, gift cards) = no buyer
  protection for either side, and no appeal path.
- Address switches and "my mover will collect it" = spoofed-shipping
  refunds where the real buyer claims non-delivery.
- "Mark as gift / declare lower value" = customs fraud; you get the fine.

## Reply stance

From `say_this`, not improvised. Firm in one line, no long explanations.
If it smells wrong: "I only sell through the platform at the listed price."
Then block, relist, move on. Never argue with a scammer; they rehearse.
