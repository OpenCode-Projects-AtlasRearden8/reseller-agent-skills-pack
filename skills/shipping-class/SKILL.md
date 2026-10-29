---
name: shipping-class
description: Pick a sensible shipping service from packed weight, dims, and item type; flag hazard and fragile cautions. Offline rules.
---

# Skill: Suggest a shipping class

You are the calm voice that says "poly mailer, not a box" before the seller
overpays on shipping.

## How to use

```bash
python -m reseller_skills shipping-class --weight-lb 3.2 --length-in 12 --width-in 9 --height-in 4
python -m reseller_skills shipping-class --weight-oz 6 --item-type "paperback book"
```

## Rules the tool applies

- Under ~12 oz packed -> poly mailer, cheapest lane.
- Books/DVDs/vinyl/manuals -> Media Mail proposal, with the "does it
  qualify?" question asked out loud (Media Mail forbids other items mixed in).
- 1-5 lb normal box -> Ground Advantage; compare one flat-rate box.
- 5-20 lb or dense -> Priority, often flat rate.
- Oversized dims (long sides, girth over 96-108") -> surcharge zones; get a
  real quote before listing "free shipping".

## Cautions the tool raises

- Lithium batteries, glass, perfume/aerosol -> these have carrier rules;
  check before promising anything.

## Always

- Quote the packed weight (item + box + filler), never the naked item.
- Say "these are starting points, not rates" — final price comes from the
  carrier's calculator at label time.
