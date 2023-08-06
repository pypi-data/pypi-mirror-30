from codeviking.astro.units import Mass


def test_calc():
    assert Mass.g.calc(7, Mass.kg) == 7000
    assert Mass.Earth.calc(1, Mass.Sol) == 332942.63420515053


def test_from_kg():
    assert Mass.g.from_kg(2) == 2000
    assert Mass.kg.from_kg(2) == 2
    assert Mass.Sol.from_kg(1.9884E30) == 1
    assert Mass.Jupiter.from_kg(1.8985219E27) == 1
    assert Mass.Earth.from_kg(5.9722E24) == 1


def test_to_kg():
    assert Mass.g.to_kg(1) == 0.001
    assert Mass.kg.to_kg(1) == 1
    assert Mass.Sol.to_kg(1) == 1.9884E30
    assert Mass.Jupiter.to_kg(1) == 1.8985219E27
    assert Mass.Earth.to_kg(1) == 5.9722E24
