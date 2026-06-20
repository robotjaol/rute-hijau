from engine.models import Point
from engine.distance import build_matrix
from engine.baseline import nearest_neighbor
from engine.optimizer import solve_cvrp


def _make_points():
    return [
        Point(id=0, name="Depot", lat=-7.321, lon=112.718, demand_kg=0),
        Point(id=1, name="P1", lat=-7.302, lon=112.724, demand_kg=90),
        Point(id=2, name="P2", lat=-7.298, lon=112.715, demand_kg=120),
        Point(id=3, name="P3", lat=-7.309, lon=112.731, demand_kg=80),
        Point(id=4, name="P4", lat=-7.294, lon=112.709, demand_kg=110),
        Point(id=5, name="P5", lat=-7.315, lon=112.705, demand_kg=95),
    ]


def test_cvrp_capacity_respected():
    points = _make_points()
    matrix = build_matrix(points, mode="haversine")
    demands = [p.demand_kg for p in points]
    capacity = 300
    solution = solve_cvrp(matrix, demands, capacity=capacity, vehicles=3)
    for route in solution.routes:
        assert route.load_kg <= capacity


def test_cvrp_not_exceeds_baseline():
    points = _make_points()
    matrix = build_matrix(points, mode="haversine")
    demands = [p.demand_kg for p in points]
    capacity = 400
    vehicles = 2

    baseline = nearest_neighbor(matrix, demands, capacity=capacity, vehicles=vehicles)
    optimized = solve_cvrp(matrix, demands, capacity=capacity, vehicles=vehicles)
    assert optimized.total_km <= baseline.total_km + 0.1


def test_cvrp_vehicle_count():
    points = _make_points()
    matrix = build_matrix(points, mode="haversine")
    demands = [p.demand_kg for p in points]
    vehicles = 3
    solution = solve_cvrp(matrix, demands, capacity=400, vehicles=vehicles)
    assert len(solution.routes) <= vehicles
