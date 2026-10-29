from reseller_skills.shipping import suggest_shipping


def test_light_item_means_poly_mailer():
    r = suggest_shipping(weight_oz=6, item_type="phone case")
    assert "Ground Advantage" in r["suggestion"]
    assert any("mailer" in x for x in r["reasons"])


def test_book_suggests_media_mail():
    r = suggest_shipping(weight_lb=2.0, item_type="hardcover book")
    assert "Media Mail" in r["suggestion"]


def test_board_game_not_media_mail():
    r = suggest_shipping(weight_lb=3.0, item_type="board game")
    assert "Media Mail" not in r["suggestion"]


def test_midweight_priority():
    r = suggest_shipping(weight_lb=12.0, item_type="kitchen appliance")
    assert "Priority" in r["suggestion"]


def test_heavy_item_gets_quote_warning():
    r = suggest_shipping(weight_lb=55, item_type="subwoofer")
    assert "quote" in r["suggestion"].lower() or "Freight" in r["suggestion"]


def test_no_weight_gives_note_not_crash():
    r = suggest_shipping(item_type="mug")
    assert r["suggestion"] is None
    assert "packed weight" in r["note"]


def test_glassware_cautions():
    r = suggest_shipping(weight_lb=2.0, item_type="glass bowl")
    assert any("double-box" in c for c in r["cautions"])


def test_lithium_cautions():
    r = suggest_shipping(weight_lb=1.0, item_type="lithium battery pack")
    assert any("Lithium" in c for c in r["cautions"])


def test_oversized_dims_flagged():
    r = suggest_shipping(weight_lb=10, length_in=60, width_in=8, height_in=6, item_type="wall art")
    assert any("oversize" in i for i in r["reasons"]) or "Large" in r["suggestion"]
