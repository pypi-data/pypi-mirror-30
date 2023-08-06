from codeviking.astro.units import Time


def test_calc():
    assert Time.h.calc(2, Time.day) == 48
    assert Time.day.calc(1, Time.yr) == 365.25


def test_from_s():
    assert Time.day.from_s(24 * 60 * 60) == 1


def test_s():
    assert Time.s.to_s(10) == 10
    assert Time.s.from_s(10) == 10


def test_min():
    assert Time.min.to_s(1) == 60


def test_h():
    assert Time.h.to_s(2) == 7200
    assert Time.h.from_s(7200) == 2


def test_day():
    assert Time.day.to_s(3) == 3 * 24 * 60 * 60


def test_yr():
    assert Time.yr.to_s(5) == 5 * 365.25 * 24 * 60 * 60


def test_Myr():
    assert Time.Myr.to_s(2) == 365.25 * 24 * 60 * 60 * 2000000
