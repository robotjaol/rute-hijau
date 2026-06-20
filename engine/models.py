from typing import Literal
from pydantic import BaseModel


class Point(BaseModel):
    id: int
    name: str
    lat: float
    lon: float
    demand_kg: int = 0


class Fleet(BaseModel):
    vehicles: int
    capacity_kg: int


class OptimizeRequest(BaseModel):
    depot: Point
    points: list[Point]
    fleet: Fleet
    distance_mode: Literal["haversine", "osrm"] = "haversine"


class RouteLeg(BaseModel):
    vehicle: int
    sequence: list[int]
    distance_km: float
    load_kg: int


class Solution(BaseModel):
    total_km: float
    routes: list[RouteLeg]


class Impact(BaseModel):
    distance_saved_km: float
    fuel_saved_liter: float
    cost_saved_rupiah_per_cycle: int
    cost_saved_rupiah_per_year: int
    co2_saved_kg_per_cycle: float
    co2_saved_kg_per_year: int
    assumptions: dict


class OptimizeResponse(BaseModel):
    baseline: Solution
    optimized: Solution
    savings_km: float
    savings_percent: float
    impact: Impact
    meta: dict
