from engine.models import Point
from engine.distance import build_matrix
from engine.baseline import nearest_neighbor, registration_order


def _make_points():
    return [
        Point(id=0, name="Depot", lat=-7.321, lon=112.718, demand_kg=0),
        Point(id=1, name="P1", lat=-7.302, lon=112.724, demand_kg=90),
        Point(id=2, name="P2", lat=-7.298, lon=112.715, demand_kg=120),
        Point(id=3, name="P3", lat=-7.309, lon=112.731, demand_kg=80),
        Point(id=4, name="P4", lat=-7.294, lon=112.709, demand_kg=110),
    ]


def _get_matrix_and_demands(points):
    matrix = build_matrix(points, mode="haversine")
    demands = [p.demand_kg for p in points]
    return matrix, demands


def test_nearest_neighbor_visits_all():
    points = _make_points()
    matrix, demands = _get_matrix_and_demands(points)
    solution = nearest_neighbor(matrix, demands, capacity=500, vehicles=2)
    visited = []
    for route in solution.routes:
        inner = route.sequence[1:-1]
        visited.extend(inner)
    assert sorted(visited) == [1, 2, 3, 4]


def test_nearest_neighbor_capacity_respected():
    points = _make_points()
    matrix, demands = _get_matrix_and_demands(points)
    capacity = 200
    solution = nearest_neighbor(matrix, demands, capacity=capacity, vehicles=4)
    for route in solution.routes:
        assert route.load_kg <= capacity


def test_nearest_neighbor_positive_distance():
    points = _make_points()
    matrix, demands = _get_matrix_and_demands(points)
    solution = nearest_neighbor(matrix, demands, capacity=500, vehicles=2)
    assert solution.total_km > 0


def test_registration_order_visits_all():
    points = _make_points()
    matrix, demands = _get_matrix_and_demands(points)
    solution = registration_order(matrix, demands, capacity=500, vehicles=2)
    visited = []
    for route in solution.routes:
        inner = route.sequence[1:-1]
        visited.extend(inner)
    assert sorted(visited) == [1, 2, 3, 4]


def test_registration_order_capacity_respected():
    points = _make_points()
    matrix, demands = _get_matrix_and_demands(points)
    capacity = 200
    solution = registration_order(matrix, demands, capacity=capacity, vehicles=4)
    for route in solution.routes:
        assert route.load_kg <= capacity
