from reseller_skills.recap import summarize_ledger

CSV = """date,description,category,platform,amount
2026-10-03,sold Wonder bag,inventory,ebay,45.00
2026-10-03,item cost,inventory,ebay,-12.00
2026-10-10,mail stamps,supplies,offline,-4.90
2026-10-20,sold hoodie,inventory,poshmark,30.00
2026-09-15,old sale (other month),inventory,ebay,99.00
penske,line with no amount,inventory,ebay,
oops,line with bad amount,inventory,ebay,abc
"""


def test_month_filter_and_totals():
    r = summarize_ledger(csv_text=CSV, month="2026-10")
    assert r["rows_included"] == 4
    assert r["sales"] == 75.0
    assert r["expenses"] == 16.90
    assert r["net"] == 58.10
    assert r["sales_count"] == 2


def test_platform_breakdown():
    r = summarize_ledger(csv_text=CSV, month="2026-10")
    assert r["by_platform"]["ebay"]["sales"] == 45.0
    assert r["by_platform"]["ebay"]["expenses"] == -12.0
    assert r["by_platform"]["poshmark"]["sales"] == 30.0
    assert r["by_platform"]["offline"]["expenses"] == -4.9


def test_bad_rows_skipped_with_reasons():
    r = summarize_ledger(csv_text=CSV, month="2026-10")
    assert len(r["rows_skipped"]) == 2
    assert all("skipped" in s for s in r["rows_skipped"])


def test_summary_sentences_written():
    r = summarize_ledger(csv_text=CSV, month="2026-10")
    assert any("Net" in s for s in r["summary_sentences"])
    assert r["margin_pct"] is not None


def test_margin_plaintext_bands():
    from reseller_skills.recap import margin_plaintext
    assert "healthy" in margin_plaintext(50)
    assert "workable" in margin_plaintext(25)
    assert "thin" in margin_plaintext(5)
    assert "negative" in margin_plaintext(-10)


def test_requires_amount_column():
    with pytest.raises(ValueError):
        summarize_ledger(csv_text="date,description\n2026-10-01,hi\n")


def test_month_formats_accepted():
    r = summarize_ledger(csv_text=CSV, month="10/2026")
    assert r["rows_included"] == 4


import pytest  # noqa: E402  (kept at bottom to keep CSV at top)
