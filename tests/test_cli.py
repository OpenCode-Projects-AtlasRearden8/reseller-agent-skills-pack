import json
import subprocess
import sys

from reseller_skills.cli import main


def run_cli(*args, expect_ok=True):
    p = subprocess.run(
        [sys.executable, "-m", "reseller_skills", *args],
        capture_output=True, text=True,
    )
    assert p.returncode == (0 if expect_ok else 2), p.stderr + p.stdout
    if not expect_ok:
        return json.loads(p.stdout)
    return json.loads(p.stdout)


def test_grade_condition_cli():
    out = run_cli("grade-condition", "--notes", "sealed, never opened")
    assert out["score"] == 5


def test_price_floor_cli():
    out = run_cli("price-floor", "--target-net", "40", "--shipping", "6")
    assert out["floor_price"] > 40
    assert out["realized_net_at_floor"] >= 40


def test_shipping_cli():
    out = run_cli("shipping-class", "--weight-oz", "5", "--item-type", "navy tie")
    assert out["suggestion"]


def test_redflag_cli():
    out = run_cli("red-flag-asks", "--message", "pay via gift card, url=https://x")
    assert any(f["flag_id"] == "risky-pay-methods" for f in out["flags"])


def test_month_recap_cli(tmp_path):
    csv = tmp_path / "ledger.csv"
    csv.write_text(
        "date,description,category,platform,amount\n"
        "2026-10-01,sale 1,inventory,ebay,20.00\n"
        "2026-10-02,cost,inventory,ebay,-5.00\n"
    )
    out = run_cli("month-recap", "--csv", str(csv), "--month", "2026-10")
    assert out["net"] == 15.0


def test_error_returns_json_and_code_2():
    out = run_cli("price-floor", "--target-net", "-5", expect_ok=False)
    assert "error" in out
