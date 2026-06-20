from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from engine.models import RouteLeg, Solution
from engine.config import SOLVER_SECONDS


def _read_routes(
    manager: pywrapcp.RoutingIndexManager,
    routing: pywrapcp.RoutingModel,
    solution: pywrapcp.Assignment,
    matrix: list[list[float]],
    demands: list[int],
    vehicles: int,
) -> list[RouteLeg]:
    routes: list[RouteLeg] = []
    for vehicle in range(vehicles):
        index = routing.Start(vehicle)
        sequence = []
        load = 0
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            sequence.append(node)
            load += demands[node]
            index = solution.Value(routing.NextVar(index))
        sequence.append(manager.IndexToNode(index))
        distance_km = sum(matrix[sequence[i]][sequence[i + 1]] for i in range(len(sequence) - 1))
        routes.append(
            RouteLeg(
                vehicle=vehicle,
                sequence=sequence,
                distance_km=round(distance_km, 4),
                load_kg=load,
            )
        )
    return routes


def solve_cvrp(
    matrix: list[list[float]],
    demands: list[int],
    capacity: int,
    vehicles: int,
) -> Solution:
    size = len(matrix)
    matrix_m = [[round(d * 1000) for d in row] for row in matrix]

    manager = pywrapcp.RoutingIndexManager(size, vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index: int, to_index: int) -> int:
        return matrix_m[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    transit = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit)

    def demand_callback(from_index: int) -> int:
        return demands[manager.IndexToNode(from_index)]

    load_callback = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        load_callback, 0, [capacity] * vehicles, True, "Cap"
    )

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.FromSeconds(SOLVER_SECONDS)  # demo budget

    solution = routing.SolveWithParameters(params)
    if solution is None:
        raise ValueError("Solver tidak menemukan solusi layak.")

    legs = _read_routes(manager, routing, solution, matrix, demands, vehicles)
    total_km = round(sum(leg.distance_km for leg in legs), 4)
    return Solution(total_km=total_km, routes=legs)
