---
name: draft-listing
description: Draft a complete, honest marketplace listing from a title, notes, and graded condition. Offline skeleton always; optional LLM polish.
---

# Skill: Draft an honest listing

You are writing a marketplace listing (eBay, Poshmark, Facebook Marketplace)
that a buyer can trust at first read.

## How to use

1. Get three facts from the human: the plain title, the item's condition
   notes, and the category.
2. Build the offline skeleton (no network, no invented facts):

   ```bash
   python -m reseller_skills draft-listing --title "Timex Weekender watch" \
     --category Jewelry & Watches --notes "runs strong, scratched crystal, band 20mm"
   ```

3. If a local LLM is reachable (default Ollama at http://localhost:11434/v1),
   ask for a *tone pass* only — never a rewrite that can add facts:

   ```bash
   python -m reseller_skills draft-listing --title "..." --notes "..." --use-llm
   ```

## LLM rules (non-negotiable)

- The system prompt forbids invented details; if the polished body adds a
  fact that was not in the skeleton, discard that sentence.
- If the endpoint is unreachable, ship the skeleton. It is already good.
- The agent may soften language ("scratched crystal" -> "shows light marks on
  the crystal, kept honest in photo 3") but may not remove disclosures.

## Tone guide

- Short sentences. No emojis. No "MUST GO!!" shouting.
- Flaws on their own bullet lines; the worst flaw is mentioned twice: early
  in the description and in a photo caption.
- End with what's included, shipping, and a one-line return-style promise:
  "Ships tracked from Indiana in 1 business day."
