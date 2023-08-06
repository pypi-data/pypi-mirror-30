from codeviking.math.interval import RI


def test_RI():
    i = RI(-2, .83)
    assert -2.1 not in i
    assert -2.0 in i
    assert 0.8 in i
    assert 0.831 not in i


def test_RI_constrain():
    i = RI(-3.0, 1.0)
    assert i.constrain(0.8) == 0.8
    assert i.constrain(-33.0) == -3.0
    assert i.constrain(2.0) == 1.0


def test_RI_alpha():
    i = RI(-3.0, 1.0)
    assert i.alpha(-4.0) == -0.25
    assert i.alpha(3.0) == 1.5
    assert i.alpha(0.0) == 0.75


def test_RI_interpolate():
    i = RI(-3.0, 1.0)
    assert i.interpolate(0.0) == -3.0
    assert i.interpolate(0.5) == -1.0
    assert i.interpolate(1.0) == 1.0


def test_RI_is_empty():
    i0 = RI.empty
    assert i0.is_empty
    i1 = RI(10, -1)
    assert i1.is_empty


def test_RI_equal():
    i0 = (1, -1)
    assert RI.empty == i0
    i1 = RI(5, 10)
    i2 = RI(5, 10)
    assert i1 == i2
    assert i1 == (5, 10)


def test_intersection():
    i0 = RI(-1, 1)
    i1 = RI(0, 6)
    i2 = RI(5, 10)
    assert i0.intersection(i1) == RI(0, 1)
    assert i0.intersection(i2).is_empty
    assert i1.intersection(i2) == RI(5, 6)
    assert i0.intersection((-1, 0)) == (-1, 0)


def test_intersects():
    i0 = RI(-1, 1)
    i1 = RI(0, 6)
    i2 = RI(5, 10)
    assert i0.intersects(i1)
    assert not i0.intersects(i2)
    assert i1.intersects(i2)
    assert i0.intersects((-1, 0))
    assert not i0.intersects(RI.empty)
    assert not RI.empty.intersects(RI.empty)
