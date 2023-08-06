from codeviking.astro.units import Distance


def test_calc():
    assert Distance.R_Sol.calc(7, Distance.pc) == 310474961.4345264
    assert Distance.R_Earth.calc(1, Distance.R_Jupiter) == 11.24653913918953


def test_from_m():
    assert Distance.R_Sol.from_m(1) == 1.4374011786689664e-09
    assert Distance.R_Jupiter.from_m(1) == 1.3987579029821518e-08
    assert Distance.R_Earth.from_m(1) == 1.5731185502139441e-07
    assert Distance.pc.from_m(1) == 3.240779289960431e-17
    assert Distance.lyr.from_m(1) == 1.0570008340246154e-16
    assert Distance.AU.from_m(1) == 6.684587122268445e-12
    assert Distance.km.from_m(1) == 0.001
    assert Distance.m.from_m(1) == 1
    assert Distance.cm.from_m(1) == 100
    assert Distance.mm.from_m(1) == 1000


def test_to_m():
    assert Distance.R_Sol.to_m(1) == 6.957E8
    assert Distance.R_Jupiter.to_m(1) == 7.1492E7
    assert Distance.R_Earth.to_m(1) == 6.3568E6
    assert Distance.pc.to_m(1) == 3.085677581e16
    assert Distance.lyr.to_m(1) == 9.4607304725808e15
    assert Distance.AU.to_m(1) == 1.495978707e11
    assert Distance.km.to_m(1) == 1000
    assert Distance.m.to_m(1) == 1
    assert Distance.cm.to_m(1) == 0.01
    assert Distance.mm.to_m(1) == 0.001
