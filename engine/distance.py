import math
import requests
from engine.models import Point
from engine.config import EARTH_KM


def haversine(a: Point, b: Point) -> float:
    lat1, lon1 = math.radians(a.lat), math.radians(a.lon)
    lat2, lon2 = math.radians(b.lat), math.radians(b.lon)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_KM * math.asin(math.sqrt(h))


def _build_haversine_matrix(points: list[Point]) -> list[list[float]]:
    size = len(points)
    matrix = [[0.0] * size for _ in range(size)]
    for i in range(size):
        for j in range(i + 1, size):
            dist = haversine(points[i], points[j])
            matrix[i][j] = dist
            matrix[j][i] = dist
    return matrix


def _build_osrm_matrix(points: list[Point]) -> list[list[float]]:
    coords = ";".join(f"{p.lon},{p.lat}" for p in points)
    url = f"http://router.project-osrm.org/table/v1/driving/{coords}?annotations=distance"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        distances_m = data["distances"]
        return [[d / 1000.0 for d in row] for row in distances_m]
    except Exception:
        return _build_haversine_matrix(points)  # graceful fallback


def build_matrix(points: list[Point], mode: str = "haversine") -> list[list[float]]:
    if mode == "osrm":
        return _build_osrm_matrix(points)
    return _build_haversine_matrix(points)
