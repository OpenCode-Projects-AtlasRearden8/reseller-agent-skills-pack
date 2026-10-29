import math

import pytest

from reseller_skills.price_floor import price_floor


def test_basic_floor_matches_formula():
    r = price_floor(target_net=100.0)
    # (100 + 0.30) / (1 - 0.13 - 0.029)
    expected = math.ceil((100.30 / 0.841) * 100) / 100
    assert r["floor_price"] == pytest.approx(expected)
    assert r["realized_net_at_floor"] >= 100.0


def test_floor_never_undershoots_target():
    for net in (10, 40, 250.67):
        r = price_floor(target_net=net, shipping=6.5, packaging=0.75)
        assert r["realized_net_at_floor"] >= net - 0.01


def test_costs_raise_the_floor():
    base = price_floor(target_net=50)
    with_ship = price_floor(target_net=50, shipping=10)
    assert with_ship["floor_price"] > base["floor_price"]


def test_reject_negative_target():
    with pytest.raises(ValueError):
        price_floor(target_net=-5)


def test_reject_absurd_fee():
    with pytest.raises(ValueError):
        price_floor(target_net=20, marketplace_pct=0.99)


def test_100pct_fees_impossible():
    with pytest.raises(ValueError):
        price_floor(target_net=20, marketplace_pct=0.5, payment_pct=0.5)
