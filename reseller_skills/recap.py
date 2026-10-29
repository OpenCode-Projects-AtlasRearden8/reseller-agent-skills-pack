"""Month recap: turn a simple ledger CSV into a plain-English profit summary.

Ledger CSV (headers flexible, order does not matter):
    date,description,category,platform,amount

    amount convention: sales positive, costs negative (or use a `kind`
    column: sale/expense and positive amounts for both).

Example row:
    2026-10-14,sold vintage lamp,inventory,ebay,-25.00

Run: python -m reseller_skills recap --csv ledger.csv --month 2026-10
"""

from __future__ import annotations

import csv
import datetime as _dt
import io
from dataclasses import dataclass


def summarize_ledger(
    csv_text: str | None = None,
    csv_path: str | None = None,
    month: str | None = None,
) -> dict:
    """Summarize a reselling ledger for a month (or all time)."""
    if csv_text is None:
        if csv_path is None:
            raise ValueError("pass either csv_text or csv_path")
        with open(csv_path, newline="", encoding="utf-8") as f:
            csv_text = f.read()

    reader = csv.DictReader(io.StringIO(csv_text))
    headers = [h.strip().lower() for h in (reader.fieldnames or [])]
    if not headers:
        raise ValueError("CSV has no header row")
    for need in ("amount",):
        if need not in headers:
            raise ValueError(f"CSV needs an 'amount' column; found {[h for h in headers]}")

    @dataclass
    class Row:
        date: str
        description: str
        category: str
        platform: str
        kind: str
        amount: float

    rows: list[Row] = []
    skipped: list[str] = []

    for i, raw in enumerate(reader, start=2):
        flat = {k.strip().lower(): v for k, v in raw.items() if k}
        amount_raw = (flat.get("amount") or "").replace("$", "").replace(",", "").strip()
        if not amount_raw:
            skipped.append(f"line {i}: no amount (skipped)")
            continue
        try:
            amount = float(amount_raw)
        except ValueError:
            skipped.append(f"line {i}: unreadable amount '{amount_raw}' (skipped)")
            continue

        date = (flat.get("date") or "").strip()
        kind = (flat.get("kind") or "").strip().lower()
        category = (flat.get("category") or "").strip().lower()
        description = (flat.get("description") or "").strip()
        platform = (flat.get("platform") or "").strip().lower() or "unknown"

        # Sign-based bookkeeping: money in is a sale, money out is a cost.
        # A `kind` column may override the sign (e.g. force "expense").
        if not kind:
            kind = "sale" if amount >= 0 else "expense"
        elif kind.startswith("exp") or kind.startswith("cost"):
            kind = "expense"
        if kind == "expense" and amount > 0:
            amount = -amount
        if kind in ("sale", "revenue", "income"):
            if amount < 0:
                kind = "refund-like"
        rows.append(Row(date, description, category, platform, kind, amount))

    if month:
        rows = [r for r in rows if _in_month(r.date, month)]

    sales = sum(
        r.amount for r in rows
        if r.kind.startswith("sale") or (r.kind == "refund-like" and r.amount >= 0)
    )
    refunds = sum(r.amount for r in rows if r.kind == "refund-like" and r.amount < 0)
    expenses = sum(r.amount for r in rows if r.kind == "expense" and r.amount < 0)

    by_platform: dict[str, dict] = {}
    for r in rows:
        p = by_platform.setdefault(r.platform, {"sales": 0.0, "expenses": 0.0, "sales_count": 0})
        if r.kind == "expense":
            p["expenses"] += r.amount
        else:
            p["sales"] += r.amount
            if r.amount > 0:
                p["sales_count"] += 1

    biggest_costs = sorted(
        [r for r in rows if r.kind == "expense"],
        key=lambda r: r.amount,
    )[:5]
    biggest_costs = [
        {"date": r.date, "description": r.description, "category": r.category, "amount": round(r.amount, 2)}
        for r in biggest_costs
    ]

    net = sales + refunds + expenses
    expenses = abs(expenses)
    margin = round(net / sales * 100, 1) if sales else None

    summary_sentences = [
        f"Income was ${sales:,.2f} and costs were ${expenses:,.2f}.",
        f"Net for the period was ${net:,.2f}.",
    ]
    if margin is not None:
        summary_sentences.append(f"That's a {margin}% margin — {margin_plaintext(margin)}.")
    if refunds < 0:
        summary_sentences.append(f"Refunds/corrections reduced the total by ${abs(refunds):,.2f}.")

    return {
        "month": month or "all rows",
        "rows_included": len(rows),
        "rows_skipped": skipped,
        "sales": round(sales, 2),
        "expenses": round(expenses, 2),
        "refunds": round(refunds, 2),
        "net": round(net, 2),
        "margin_pct": margin,
        "sales_count": sum(1 for r in rows if r.kind.startswith("sale") and r.amount > 0),
        "by_platform": {k: {kk: round(vv, 2) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in by_platform.items()},
        "biggest_costs": biggest_costs,
        "summary_sentences": summary_sentences,
        "note": (
            "Plain bookkeeping reminder: net here is cash coming in minus cash going "
            "out. For taxes, talk to a professional; keep the CSV as your starting record."
        ),
    }


def margin_plaintext(margin: float) -> str:
    if margin >= 40:
        return "healthy for a side hustle"
    if margin >= 20:
        return "workable; watch your fees and shipping costs"
    if margin >= 0:
        return "thin; raise prices or trim costs"
    return "negative; you're paying to sell"


def _in_month(date_str: str, month: str) -> bool:
    month = month.strip()
    fmts = ["%Y-%m", "%m/%Y", "%Y/%m", "%b %Y", "%B %Y"]
    target = None
    for fmt in fmts:
        try:
            target = _dt.datetime.strptime(month, fmt).date()
            break
        except ValueError:
            continue
    if target is None:
        raise ValueError(f"unrecognized month format: {month!r} (use e.g. 2026-10)")
    try:
        d = _dt.datetime.fromisoformat(date_str).date()
    except ValueError:
        return False
    return (d.year, d.month) == (target.year, target.month)
