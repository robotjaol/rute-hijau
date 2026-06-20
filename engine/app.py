import csv
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from engine.models import OptimizeRequest, OptimizeResponse, Point, Fleet, Solution
from engine.distance import build_matrix
from engine.baseline import nearest_neighbor
from engine.optimizer import solve_cvrp
from engine.impact import estimate_impact
from engine.config import DEFAULT_VEHICLES, DEFAULT_CAPACITY_KG

app = FastAPI(title="RuteHijau Engine")

ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN] if ALLOWED_ORIGIN != "*" else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_points.csv")


def _load_sample_csv() -> dict:
    depot = None
    points = []
    with open(DATA_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        point_id = 0
        for row in reader:
            p = Point(
                id=point_id,
                name=row["name"],
                lat=float(row["lat"]),
                lon=float(row["lon"]),
                demand_kg=int(row["demand_kg"]),
            )
            if row["type"] == "depot":
                depot = p
            else:
                points.append(p)
            point_id += 1
    return {"depot": depot, "points": points, "fleet": {"vehicles": DEFAULT_VEHICLES, "capacity_kg": DEFAULT_CAPACITY_KG}}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/sample")
def sample():
    data = _load_sample_csv()
    return data


@app.post("/api/optimize", response_model=OptimizeResponse)
def optimize(request: OptimizeRequest):
    if not request.points:
        raise HTTPException(status_code=400, detail="Daftar titik jemput tidak boleh kosong.")

    total_demand = sum(p.demand_kg for p in request.points)
    total_capacity = request.fleet.vehicles * request.fleet.capacity_kg
    if total_demand > total_capacity:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Total volume ({total_demand} kg) melebihi total kapasitas armada "
                f"({total_capacity} kg). Tambah armada atau kurangi volume."
            ),
        )

    all_points = [request.depot] + request.points
    matrix = build_matrix(all_points, mode=request.distance_mode)
    demands = [p.demand_kg for p in all_points]

    baseline_solution = nearest_neighbor(
        matrix, demands, request.fleet.capacity_kg, request.fleet.vehicles
    )
    optimized_solution = solve_cvrp(
        matrix, demands, request.fleet.capacity_kg, request.fleet.vehicles
    )

    savings_km = round(baseline_solution.total_km - optimized_solution.total_km, 4)
    savings_km = max(savings_km, 0.0)
    savings_percent = round(savings_km / baseline_solution.total_km * 100, 2) if baseline_solution.total_km > 0 else 0.0

    impact = estimate_impact(savings_km)

    return OptimizeResponse(
        baseline=baseline_solution,
        optimized=optimized_solution,
        savings_km=savings_km,
        savings_percent=savings_percent,
        impact=impact,
        meta={
            "distance_mode": request.distance_mode,
            "points": len(request.points),
            "vehicles": request.fleet.vehicles,
            "capacity_kg": request.fleet.capacity_kg,
        },
    )
