from datetime import datetime

from src.main import date, foo


def test_foo():
    assert foo() == "foo"


def test_date():
    assert date() == datetime(2020, 1, 1)
