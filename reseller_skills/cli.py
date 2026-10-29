"""CLI for the reseller skills pack. Every subcommand prints JSON."""

from __future__ import annotations

import argparse
import json
import sys

from . import condition, listing, price_floor, recap, redflags, shipping


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="reseller-skills",
        description="Plain-English reselling skills: grade, list, price, ship, screen, recap.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("grade-condition", help="grade an item's condition from notes")
    p.add_argument("--notes", required=True, help="free-form condition notes")

    p = sub.add_parser(
        "draft-listing",
        help="draft an honest listing (LLM optional; offline skeleton always works)",
    )
    p.add_argument("--title", required=True)
    p.add_argument("--category", default="")
    p.add_argument("--notes", default="")
    p.add_argument("--brand", default="")
    p.add_argument("--use-llm", action="store_true", help="polish the draft via the LLM endpoint")
    p.add_argument("--llm-url", default=None)
    p.add_argument("--llm-model", default=None)

    p = sub.add_parser("price-floor", help="lowest price that keeps your target profit")
    p.add_argument("--target-net", type=float, required=True, help="money you want in your pocket")
    p.add_argument("--marketplace-pct", type=float, default=0.13)
    p.add_argument("--payment-pct", type=float, default=0.029)
    p.add_argument("--payment-fixed", type=float, default=0.30)
    p.add_argument("--shipping", type=float, default=0.0)
    p.add_argument("--packaging", type=float, default=0.0)
    p.add_argument("--other", type=float, default=0.0)

    p = sub.add_parser("shipping-class", help="suggest a shipping service from weight/dims")
    p.add_argument("--weight-lb", type=float, default=None)
    p.add_argument("--weight-oz", type=float, default=None)
    p.add_argument("--length-in", type=float, default=None)
    p.add_argument("--width-in", type=float, default=None)
    p.add_argument("--height-in", type=float, default=None)
    p.add_argument("--item-type", default="")

    p = sub.add_parser("red-flag-asks", help="scan a buyer message for scam patterns")
    p.add_argument("--message", required=True, help="the buyer's message text")

    p = sub.add_parser("month-recap", help="turn a ledger CSV into a month profit recap")
    p.add_argument("--csv", required=True, help="path to ledger CSV")
    p.add_argument("--month", default=None, help="e.g. 2026-10")

    args = parser.parse_args(argv)

    try:
        result = _dispatch(args)
    except (ValueError, FileNotFoundError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0


def _dispatch(args) -> dict:
    if args.command == "grade-condition":
        return condition.grade_item_notes(args.notes)
    if args.command == "draft-listing":
        if not args.use_llm:
            return listing.build_draft(args.title, args.category, args.notes, args.brand)
        kwargs = {}
        if args.llm_url:
            kwargs["base_url"] = args.llm_url
        if args.llm_model:
            kwargs["model"] = args.llm_model
        return listing.draft_with_llm(args.title, args.category, args.notes, **kwargs)
    if args.command == "price-floor":
        return price_floor.price_floor(
            target_net=args.target_net,
            marketplace_pct=args.marketplace_pct,
            payment_pct=args.payment_pct,
            payment_fixed=args.payment_fixed,
            shipping=args.shipping,
            packaging=args.packaging,
            other_costs=args.other,
        )
    if args.command == "shipping-class":
        return shipping.suggest_shipping(
            weight_lb=args.weight_lb,
            weight_oz=args.weight_oz,
            length_in=args.length_in,
            width_in=args.width_in,
            height_in=args.height_in,
            item_type=args.item_type,
        )
    if args.command == "red-flag-asks":
        return redflags.scan_buyer_message(args.message)
    if args.command == "month-recap":
        with open(args.csv, encoding="utf-8") as f:
            return recap.summarize_ledger(csv_text=f.read(), month=args.month)
    raise ValueError(f"unknown command: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
