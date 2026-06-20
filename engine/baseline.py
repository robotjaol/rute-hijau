from engine.models import RouteLeg, Solution


def nearest_neighbor(
    matrix: list[list[float]],
    demands: list[int],
    capacity: int,
    vehicles: int,
) -> Solution:
    num_points = len(matrix)
    unvisited = set(range(1, num_points))
    routes: list[RouteLeg] = []

    for vehicle in range(vehicles):
        if not unvisited:
            break
        sequence = [0]
        load = 0
        current = 0

        while unvisited:
            nearest = None
            nearest_dist = float("inf")
            for candidate in unvisited:
                if load + demands[candidate] <= capacity:
                    dist = matrix[current][candidate]
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest = candidate
            if nearest is None:
                break
            sequence.append(nearest)
            load += demands[nearest]
            unvisited.discard(nearest)
            current = nearest

        sequence.append(0)
        distance_km = sum(matrix[sequence[i]][sequence[i + 1]] for i in range(len(sequence) - 1))
        routes.append(RouteLeg(vehicle=vehicle, sequence=sequence, distance_km=round(distance_km, 4), load_kg=load))

    total_km = round(sum(r.distance_km for r in routes), 4)
    return Solution(total_km=total_km, routes=routes)


def registration_order(
    matrix: list[list[float]],
    demands: list[int],
    capacity: int,
    vehicles: int,
) -> Solution:
    num_points = len(matrix)
    point_queue = list(range(1, num_points))
    routes: list[RouteLeg] = []

    for vehicle in range(vehicles):
        if not point_queue:
            break
        sequence = [0]
        load = 0

        remaining = []
        for point in point_queue:
            if load + demands[point] <= capacity:
                sequence.append(point)
                load += demands[point]
            else:
                remaining.append(point)

        point_queue = remaining
        sequence.append(0)
        distance_km = sum(matrix[sequence[i]][sequence[i + 1]] for i in range(len(sequence) - 1))
        routes.append(RouteLeg(vehicle=vehicle, sequence=sequence, distance_km=round(distance_km, 4), load_kg=load))

    total_km = round(sum(r.distance_km for r in routes), 4)
    return Solution(total_km=total_km, routes=routes)
