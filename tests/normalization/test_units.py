from os_lem.units import parse_value


def test_parse_value_si_passthrough():
    assert parse_value(0.123) == 0.123


def test_parse_value_engineering_units():
    assert parse_value("100 cm") == 1.0
    assert parse_value("132 cm2") == 132e-4
    assert parse_value("18 l") == 18e-3
    assert parse_value("0.35 mH") == 0.35e-3
