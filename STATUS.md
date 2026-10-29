# STATUS.md — reseller-agent-skills-pack

Built: 2026-10-29 by Asdale Dynamics, LLC

## What was built

A pack of six plain-English agent skills for reselling side hustles, in the
everyday-agent-skills-pack conventions (skill folder + `SKILL.md` with YAML
frontmatter, backed by deterministic local tools any MCP-capable agent can run):

1. **grade-condition** — grades an item 1–5 from messy notes, honors
   negation ("no cracks" ≠ cracks), downgrades conflicting cue
   ("sealed but opened"), returns honest disclosure lines.
2. **draft-listing** — builds a truthful listing skeleton offline; optional
   tone polish via any OpenAI-compatible endpoint. LLM may not add facts;
   falls back to the untouched skeleton on any endpoint error.
3. **price-floor** — solves the minimum list price for a target net after
   marketplace %, payment % + fixed, shipping, packaging, other costs.
   Floor always rounds *up* to the cent; verifies realized net ≥ target.
4. **shipping-class** — rule-based service suggestion (poly mailer, Media
   Mail eligibility, Ground Advantage, Priority, oversize/freight warnings)
   plus fragile/lithium/hazard cautions.
5. **red-flag-asks** — scans buyer messages for 8 scam-pattern families
   (overpayment, off-platform pay, address switch, bypass protections, …),
   ranks by severity, hands back ready-to-send refusal scripts.
6. **month-recap** — parses a simple ledger CSV (sign-based, flexible
   headers, `kind` column optional), totals sales/costs/refunds/net,
   per-platform breakdown, top 5 costs, plain-English summary sentences
   and margin bands.

Components: `reseller_skills/` package (six tool modules + tiny keyless LLM
client `llm.py` + JSON CLI), `skills/` (6 SKILL.md files), `tests/` (49 tests),
`examples/` (two ledger CSVs), README, MIT LICENSE.

## How to run

```bash
python -m pytest                     # test suite
python -m reseller_skills --help     # all commands, JSON output
# e.g.
python -m reseller_skills price-floor --target-net 40 --shipping 6.50
python -m reseller_skills month-recap --csv examples/ledger-example.csv --month 2026-10
```

Optional LLM (draft polish only): start a local, keyless OpenAI-compatible
server (`ollama serve`, default `http://localhost:11434/v1`, model
`llama3.1:8b`) and add `--use-llm` to `draft-listing`. The pack explicitly
refuses API keys — by design, not by omission.

## Verification results

- `python -m pytest` → **49 passed** (all offline, < 1 s).
- CLI smoke tests run: `grade-condition`, `price-floor`, `shipping-class`,
  `red-flag-asks`, `month-recap` all return valid JSON.
- `pip install -e .` succeeds; console script `reseller-skills` works.
- `python -c "import reseller_skills"` clean.
- LLM failure-mode test confirms a dead endpoint raises a friendly
  `LlmError` and `draft-listing` falls back to the offline skeleton.

## Known gaps

- Shipping logic is USPS-lean guidance with starting-point language — real
  rates still come from the carrier at label time (stated in all outputs).
- Condition grading is keyword-based (English only); odd phrasings can
  under-detect damage, so the SKILL.md asks the agent to restate the worst
  flaw in its own words too.
- Price floor supports one fee tier (no per-category store fees, ad fees,
  or taxes); percentages are user-supplied.
- Ledger recap expects sign-based CSV (sales +, costs −) and skips malformed
  rows with a reason; no non-CSV ledger import yet.
- The local-*month* filter parses ISO-like dates; non-ISO date formats are
  excluded from month filters rather than crashing.
