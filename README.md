# reseller-agent-skills-pack

Plain-English agent skills for reselling side hustles — the kind of help a
friend would give you before you list that thrift-store lamp on eBay.
Six skills, one Python tool belt, zero cloud dependencies.

**By Asdale Dynamics, LLC** — part of the everyday-agent-skills-pack family
of skill packs that load into any MCP-capable agent.

## What's in the pack

Each skill is a folder in `skills/` with a `SKILL.md` written in plain
English (what it does, when to use it, how to run it) plus a deterministic
Python tool it can call. The tools work fully offline; only the optional
listing polish uses an LLM.

| Skill folder | What it does | Tool command |
|---|---|---|
| `grade-condition` | Grades an item from your rough notes: 1 (parts) to 5 (new), plus the disclosure lines you owe the buyer | `grade-condition --notes "..."` |
| `draft-listing` | Drafts an honest listing — skeleton always, optional LLM tone pass | `draft-listing --title ... --notes ...` |
| `price-floor` | Lowest price that still pays you after fees and costs | `price-floor --target-net 40 --shipping 6.50` |
| `shipping-class` | Poly mailer vs box vs Priority vs Media Mail — with hazard cautions | `shipping-class --weight-lb 3.2 --item-type "book"` |
| `red-flag-asks` | Scans a buyer message for scam patterns and hands you a polite refusal script | `red-flag-asks --message "..."` |
| `month-recap` | Turns your ledger CSV into a plain-English profit recap | `month-recap --csv ledger.csv --month 2026-10` |

## The everyday-agent-skills-pack conventions

- Each skill lives in `skills/<skill-name>/SKILL.md`.
- `SKILL.md` starts with YAML frontmatter: `name` and `description` (an MCP
  or skill-loader agent uses these to decide when to reach for the skill).
- The body is written for the agent: purpose, steps, example command, and
  hard rules (like *never invent a condition fact*).
- Deterministic work happens in the local Python tools, not in the model.
  The model explains, drafts, and stays honest; the tools do math and matching.
- Skills never require the network. When an LLM is genuinely useful (drafting
  prose), it points at any OpenAI-compatible endpoint with **no API key** —
  default is local Ollama at `http://localhost:11434/v1`.

## Install & run

```bash
# from the repo folder (Python 3.9+, nothing to install except tests)
python -m pytest                    # run the test suite
python -m reseller_skills --help    # see every command

# examples
python -m reseller_skills grade-condition --notes "small scratch on lid, works fine"
python -m reseller_skills price-floor --target-net 40 --shipping 6.50
python -m reseller_skills shipping-class --weight-oz 6 --item-type "paperback book"
python -m reseller_skills red-flag-asks --message "I'll Venmo you extra to ship to a different address"
python -m reseller_skills month-recap --csv examples/ledger-example.csv --month 2026-10

# optional: polish a draft with a local LLM (start one first, e.g. `ollama serve`)
python -m reseller_skills draft-listing --title "Timex Weekender" \
  --category "Jewelry & Watches" --notes "runs strong, scratched crystal" --use-llm
```

## The ledger CSV format

```
date,description,category,platform,amount
2026-10-03,sold Wonder bag,inventory,ebay,45.00
2026-10-03,item cost,inventory,ebay,-12.00
2026-10-10,mail stamps,supplies,offline,-4.90
```

Sales positive, costs negative. An optional `kind` column can force a row to
`expense`, but the sign already tells the tool everything it needs.
`examples/ledger-example.csv` shows a full month.

## Honesty guarantees (the boring but important part)

- The condition grader never upgrades a grade. Conflicting notes ("sealed,
  but I opened it") grade to the *worse* reading.
- The listing drafter may not invent facts. The LLM prompt forbids added
  details, and if the model misbehaves you still have the untouched skeleton.
- Pricing shows the fee breakdown in dollars, so you can always explain
  where the money went.
- No secrets: the pack never takes an API key, never calls out to your
  accounts, and stores nothing personal. Your CSV stays in your folder.
- Bookkeeping ≠ tax advice. A professional does your taxes; this just makes
  the numbers readable.

## Development

```bash
python -m pytest        # 49 tests, all offline, < 1 second
```

Structure: `reseller_skills/` (tools + CLI), `skills/` (agent-facing
SKILL.md files), `tests/`, `examples/`.

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Asdale Dynamics, LLC.
Created for beginner-friendly, local-first AI tooling. Learn more about AI
"like a friend would" at dylanasdale.github.io and in *The Massive AI Manual*.
