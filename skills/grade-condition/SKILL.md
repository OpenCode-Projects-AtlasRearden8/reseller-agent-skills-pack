---
name: grade-condition
description: Turn messy item notes into an honest condition grade (1-5) with disclosure lines. Use before listing anything.
---

# Skill: Grade an item's condition from notes

You are grading an item Dylan (or any reseller) described in their own rough
notes. Your job: one honest condition label, nothing fancier, nothing scary.

## How to use

1. Collect the item's notes (voice-memo transcript, a text message to
   yourself, anything).
2. Run the deterministic grader — it is offline and instant:

   ```bash
   python -m reseller_skills grade-condition --notes "small scratch on lid, works fine"
   ```

3. Present the score and label, then say out loud which of the returned
   `signals` and `disclosures` must be repeated in the buyer-facing listing.

## The 5-point scale (plain English)

- 5 New — sealed or literally never used
- 4 Like New — used maybe once, no marks worth mentioning
- 3 Good — normal used; works; honest wear
- 2 Fair — visible wear, light problems you must disclose
- 1 For Parts or Not Working — say so first, price it low

## Honesty rules

- Never upgrade a grade because a sale feels good. A return costs more than
  a lower starting price.
- If the notes conflict ("sealed, but I opened it"), report the conflict and
  grade the *worse* reading.
- If your confidence is "low", ask the human for one more detail: *does it
  work, and what is the single worst flaw?*

## When the agent writes about it

Use wording like: "Condition: Good (used) — light scuffs on the base, shown
in photo 4. Works as it should." One sentence, flaws included, no apology.
