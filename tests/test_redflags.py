from reseller_skills.redflags import scan_buyer_message


def test_clean_message_is_clear():
    r = scan_buyer_message("Hi, is this still available? Would you take 40?")
    # vague haggling is normal, not a scam
    assert r["verdict"].startswith("clear") or r["verdict"].startswith("caution")


def test_overpayment_flag():
    r = scan_buyer_message("I'll pay 200 and you send the extra back to me")
    ids = [f["flag_id"] for f in r["flags"]]
    assert "overpayment" in ids
    assert r["verdict"].startswith("stop")


def test_off_platform_pay_flag():
    r = scan_buyer_message("can we do this off ebay, I'll send Zelle")
    ids = [f["flag_id"] for f in r["flags"]]
    assert "risky-pay-methods" in ids
    assert "take-it-off-platform" in ids


def test_address_switch_flag():
    r = scan_buyer_message("ship to a different address please, my courier will handle it")
    ids = [f["flag_id"] for f in r["flags"]]
    assert "address-switch" in ids


def test_scripts_present_for_each_flag():
    r = scan_buyer_message("deadline: pay right now, first person wins")
    for f in r["flags"]:
        assert f["say_this"].strip()


def test_empty_message_is_clear():
    r = scan_buyer_message("")
    assert r["flags"] == []
    assert r["verdict"].startswith("clear")


def test_high_severity_sorted_first():
    r = scan_buyer_message("is this available right now? also can we go direct via zelle")
    assert r["flags"][0]["severity"] in ("high",)
