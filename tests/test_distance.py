import pytest
from engine.models import Point
from engine.distance import haversine, build_matrix


SURABAYA = Point(id=0, name="A", lat=-7.2575, lon=112.7521, demand_kg=0)
JAKARTA = Point(id=1, name="B", lat=-6.2088, lon=106.8456, demand_kg=0)
KNOWN_DISTANCE_KM = 664.0  # approximate haversine


def test_haversine_known_value():
    dist = haversine(SURABAYA, JAKARTA)
    assert abs(dist - KNOWN_DISTANCE_KM) < 5.0


def test_haversine_same_point():
    dist = haversine(SURABAYA, SURABAYA)
    assert dist == pytest.approx(0.0, abs=1e-9)


def test_build_matrix_diagonal_zero():
    points = [SURABAYA, JAKARTA]
    matrix = build_matrix(points, mode="haversine")
    assert matrix[0][0] == pytest.approx(0.0, abs=1e-9)
    assert matrix[1][1] == pytest.approx(0.0, abs=1e-9)


def test_build_matrix_symmetric():
    points = [SURABAYA, JAKARTA]
    matrix = build_matrix(points, mode="haversine")
    assert matrix[0][1] == pytest.approx(matrix[1][0], abs=1e-9)


def test_build_matrix_three_points():
    c = Point(id=2, name="C", lat=-7.0, lon=110.0, demand_kg=0)
    points = [SURABAYA, JAKARTA, c]
    matrix = build_matrix(points, mode="haversine")
    for i in range(3):
        assert matrix[i][i] == pytest.approx(0.0, abs=1e-9)
    for i in range(3):
        for j in range(3):
            assert matrix[i][j] == pytest.approx(matrix[j][i], abs=1e-9)
