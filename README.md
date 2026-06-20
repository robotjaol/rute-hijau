# RuteHijau

**Waste Collection Route Optimiser for Small-Scale Fleet Operators**

RuteHijau solves the Capacitated Vehicle Routing Problem (CVRP) for community waste banks, RW-level collectors, and TPS3R operators who manage a limited fleet without commercial software. The engine finds routes that minimise total travel distance while respecting vehicle capacity, then quantifies fuel savings and CO₂ reduction against an unoptimised baseline.

---

## Table of Contents

1. [Architecture](#1-architecture)
2. [Algorithm](#2-algorithm)
3. [Data Model](#3-data-model)
4. [API Contract](#4-api-contract)
5. [Impact Estimation](#5-impact-estimation)
6. [File Structure](#6-file-structure)
7. [Quick Start](#7-quick-start)
8. [Running Tests](#8-running-tests)
9. [Deployment](#9-deployment)
10. [Tech Stack](#10-tech-stack)

---

## 1. Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Browser                                                │
│  Next.js 14 (React)  ·  react-leaflet  ·  TypeScript   │
│                                                         │
│   ParamsPanel ──► lib/api.ts ──► POST /api/optimize     │
│   MapView     ◄── OptimizeResponse                      │
│   SummaryPanel◄── OptimizeResponse                      │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP JSON
┌──────────────────────────▼──────────────────────────────┐
│  FastAPI Engine  (Python 3.11)                          │
│                                                         │
│   distance.py  ──► build_matrix (haversine / OSRM)     │
│   baseline.py  ──► nearest_neighbor / registration_order│
│   optimizer.py ──► solve_cvrp (Google OR-Tools)        │
│   impact.py    ──► estimate_impact (fuel · CO₂)        │
└─────────────────────────────────────────────────────────┘
```

The optimisation engine must remain in Python because Google OR-Tools ships native C++ binaries that cannot run in the browser or a serverless edge runtime. The frontend is a pure display layer — no routing logic lives in the client.

---

## 2. Algorithm

### 2.1 Distance Matrix

All pairwise distances are pre-computed once per request and stored in an *N × N* matrix, where *N* = |depot| + |pickup points|.

**Haversine formula** (default, offline-safe):

$$d(A, B) = 2R \arcsin\!\left(\sqrt{\sin^2\!\frac{\Delta\phi}{2} + \cos\phi_A\,\cos\phi_B\,\sin^2\!\frac{\Delta\lambda}{2}}\right)$$

where $R = 6371\ \text{km}$, $\phi$ = latitude in radians, $\lambda$ = longitude in radians.

The matrix is symmetric ($d_{ij} = d_{ji}$) and has a zero diagonal ($d_{ii} = 0$).

**OSRM mode** (optional): calls `router.project-osrm.org/table/v1/driving` for road distances. Falls back silently to haversine on timeout or error.

### 2.2 Baseline Routes

Two heuristics establish the pre-optimisation reference:

| Method | Description | Represents |
|---|---|---|
| **Nearest Neighbour** | At each step, assign the closest unvisited point that still fits capacity | Intuitive manual routing |
| **Registration Order** | Serve points in CSV row order, overflow to next vehicle | Routing with no planning at all |

The nearest-neighbour solution is used as the primary baseline for savings calculation.

### 2.3 CVRP Optimisation

The Capacitated Vehicle Routing Problem minimises total distance subject to per-vehicle capacity:

$$\min \sum_{k=1}^{K} \sum_{i=0}^{N} \sum_{j=0}^{N} d_{ij}\, x_{ijk}$$

$$\text{subject to} \quad \sum_{i \in S} q_i \leq Q_k \quad \forall k,\ S \subseteq \text{route}_k$$

where $x_{ijk} \in \{0,1\}$ indicates vehicle $k$ travels arc $(i,j)$, $q_i$ is demand at node $i$, and $Q_k$ is the capacity of vehicle $k$.

Solved with **Google OR-Tools** (`pywrapcp`):

```
Search strategy : PATH_CHEAPEST_ARC (first solution)
Metaheuristic   : GUIDED_LOCAL_SEARCH (improvement)
Time limit      : 8 s local  /  4 s serverless
```

```
Solver pipeline
───────────────
OptimizeRequest
    │
    ▼
build_matrix()  ──────────────── N×N float km matrix
    │
    ├──► nearest_neighbor()  ──── baseline Solution
    │
    └──► solve_cvrp()
            │
            ├── RoutingIndexManager
            ├── distance_callback  (metres, integer)
            ├── demand_callback
            ├── AddDimensionWithVehicleCapacity
            └── SolveWithParameters
                    │
                    ▼
              list[RouteLeg]  ──► optimised Solution
```

### 2.4 Savings Calculation

```
savings_km      = baseline.total_km − optimised.total_km
savings_percent = savings_km / baseline.total_km × 100
```

Savings are floored at 0 to handle the rare case where the solver's time-bounded solution slightly exceeds the greedy baseline.

---

## 3. Data Model

### Input CSV

| Column | Type | Required | Notes |
|---|---|---|---|
| `type` | string | ✓ | `depot` or `pickup` |
| `name` | string | ✓ | Human-readable label |
| `lat` | float | ✓ | WGS-84 decimal degrees |
| `lon` | float | ✓ | WGS-84 decimal degrees |
| `demand_kg` | int | ✓ | 0 for depot |

Example:

```csv
type,name,lat,lon,demand_kg
depot,TPS3R Jambangan,-7.3210,112.7180,0
pickup,Bank Sampah Melati,-7.3025,112.7240,90
pickup,Bank Sampah Mawar,-7.2980,112.7155,120
```

### Pydantic Schemas (engine/models.py)

```
OptimizeRequest
├── depot      : Point
├── points     : list[Point]
├── fleet      : Fleet { vehicles, capacity_kg }
└── distance_mode : "haversine" | "osrm"

OptimizeResponse
├── baseline   : Solution { total_km, routes: list[RouteLeg] }
├── optimized  : Solution
├── savings_km : float
├── savings_percent : float
├── impact     : Impact
└── meta       : dict

RouteLeg
├── vehicle     : int
├── sequence    : list[int]   # node IDs in visit order
├── distance_km : float
└── load_kg     : int

Impact
├── distance_saved_km
├── fuel_saved_liter
├── cost_saved_rupiah_per_cycle
├── cost_saved_rupiah_per_year
├── co2_saved_kg_per_cycle
├── co2_saved_kg_per_year
└── assumptions : dict
```

---

## 4. API Contract

### `GET /api/health`

```json
{ "status": "ok" }
```

### `GET /api/sample`

Returns the built-in 30-point Surabaya dataset ready for immediate use.

```json
{
  "depot": { "id": 0, "name": "TPS3R Jambangan", "lat": -7.321, "lon": 112.718, "demand_kg": 0 },
  "points": [ { "id": 1, "name": "Bank Sampah Melati", "lat": -7.3025, "lon": 112.724, "demand_kg": 90 }, "..." ],
  "fleet": { "vehicles": 4, "capacity_kg": 780 }
}
```

### `POST /api/optimize`

**Request body:** `OptimizeRequest`

**Response:** `OptimizeResponse`

| Status | Condition |
|---|---|
| 200 | Solution found |
| 400 | `points` list is empty |
| 409 | Total demand > total fleet capacity |
| 422 | Schema validation failure |

**Example 409 message:**

```
Total volume (3200 kg) melebihi total kapasitas armada (3120 kg).
Tambah armada atau kurangi volume.
```

---

## 5. Impact Estimation

Fuel and emission savings are derived from the distance delta using fixed operational constants:

| Constant | Value | Symbol |
|---|---|---|
| Fuel consumption | 10 km / litre | $\eta$ |
| Fuel price | Rp 13,000 / litre | $p$ |
| CO₂ emission factor | 2.31 kg CO₂ / litre | $\epsilon$ |
| Operating days | 312 days / year | $D$ |

$$L_{saved} = \frac{\Delta d}{\eta}$$

$$C_{cycle} = \lfloor L_{saved} \times p \rfloor$$

$$C_{year} = \lfloor \frac{\Delta d \times D}{\eta} \times p \rfloor$$

$$E_{cycle} = L_{saved} \times \epsilon$$

$$E_{year} = \lfloor \frac{\Delta d \times D}{\eta} \times \epsilon \rfloor$$

All assumptions are returned verbatim in the `impact.assumptions` field so results can be audited or reproduced independently.

---

## 6. File Structure

```
rute-hijau/
├── engine/
│   ├── app.py            # FastAPI endpoints (health, sample, optimize)
│   ├── config.py         # All constants and defaults
│   ├── models.py         # Pydantic request/response schemas
│   ├── distance.py       # build_matrix, haversine, OSRM fallback
│   ├── baseline.py       # nearest_neighbor, registration_order
│   ├── optimizer.py      # solve_cvrp with OR-Tools
│   ├── impact.py         # estimate_impact (fuel · CO₂)
│   ├── data/
│   │   └── sample_points.csv   # 30-point Surabaya demo dataset
│   └── requirements.txt
├── web/
│   ├── app/
│   │   ├── page.tsx      # Root page — composes all panels
│   │   ├── layout.tsx    # HTML shell
│   │   └── globals.css   # Global styles + Leaflet CSS import
│   ├── components/
│   │   ├── MapView.tsx       # react-leaflet map, dynamic (no SSR)
│   │   ├── ParamsPanel.tsx   # CSV upload, sample loader, fleet form
│   │   └── SummaryPanel.tsx  # Distance, savings, fuel, CO₂
│   ├── lib/
│   │   ├── api.ts        # loadSample(), optimize() — engine client
│   │   └── types.ts      # TypeScript mirrors of API schemas
│   ├── api/
│   │   └── optimize.py   # Optional Vercel serverless handler
│   └── package.json
├── tests/
│   ├── test_distance.py  # Matrix symmetry, haversine known value
│   ├── test_baseline.py  # Capacity bounds, full coverage
│   ├── test_optimizer.py # Feasibility, optimised ≤ baseline
│   ├── test_impact.py    # Formula correctness, zero-savings case
│   └── test_api.py       # Endpoint shapes, 400/409 error handling
├── run.sh                # One-command demo launcher
├── pytest.ini
└── README.md
```

---

## 7. Quick Start

### One-command demo

```bash
bash run.sh
```

Opens the engine on `http://localhost:8000` and the web UI on `http://localhost:3000`. Installs all dependencies automatically on first run.

### Manual setup

```bash
# Terminal 1 — engine
cd engine
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

# Terminal 2 — web
cd web
npm install
echo "NEXT_PUBLIC_ENGINE_URL=http://localhost:8000" > .env.local
npm run dev
```

### Demo flow

```
1. Open http://localhost:3000
2. Click  [ Muat Contoh ]   → loads 30 Surabaya pickup points
3. Adjust fleet parameters  (vehicles, capacity)
4. Click  [ Hitung Rute ]   → runs CVRP, draws coloured routes on map
5. Toggle [ Baseline / Optimal ] to compare
6. Read savings in the summary panel (distance · fuel cost · CO₂)
```

---

## 8. Running Tests

```bash
pip install -r engine/requirements.txt
pytest -q
```

Expected output: **26 passed** (≈50 s — dominated by the OR-Tools solver in `test_optimizer.py`).

### Test coverage

| File | What is verified |
|---|---|
| `test_distance.py` | Matrix symmetry, zero diagonal, haversine against known geodesic |
| `test_baseline.py` | Every point visited exactly once, load ≤ capacity on all routes |
| `test_optimizer.py` | Solver feasibility, optimised total ≤ nearest-neighbour baseline |
| `test_impact.py` | Fuel/cost/CO₂ formulas, per-cycle vs per-year consistency, zero-savings edge case |
| `test_api.py` | Response schema shape, savings\_percent ∈ [0,100], HTTP 400 / 409 errors |

---

## 9. Deployment

### Option A — Full local (demo)

Run `bash run.sh`. No external services required. Distance mode defaults to haversine, so the demo works with no internet connection.

### Option B — Vercel (web) + Python host (engine)

| Layer | Host | Notes |
|---|---|---|
| Web | Vercel | Deploy `web/` directory |
| Engine | Render / Railway / Fly.io | Deploy `engine/` as a FastAPI service |

Set `NEXT_PUBLIC_ENGINE_URL` in Vercel project settings to the public engine URL. Enable CORS on the engine by setting the `ALLOWED_ORIGIN` environment variable to the Vercel domain.

### Option C — Fully on Vercel (serverless)

`web/api/optimize.py` re-exports the FastAPI app as a Vercel Python function. Set `SOLVER_SECONDS=4` to stay within the serverless execution limit. Cold starts may be slow due to the OR-Tools native binary.

### Environment variables

| Variable | Where | Example |
|---|---|---|
| `NEXT_PUBLIC_ENGINE_URL` | web | `http://localhost:8000` |
| `SOLVER_SECONDS` | engine | `8` (local) · `4` (serverless) |
| `ALLOWED_ORIGIN` | engine | `https://rutehijau.vercel.app` |

---

## 10. Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Optimisation | Google OR-Tools 9.10 | Industry-grade CVRP solver, open-source |
| API | FastAPI + Pydantic v2 | Typed schemas, auto-validation, fast |
| Distance | Haversine (default) / OSRM | Offline-safe default; road distance optional |
| Frontend | Next.js 14 (App Router) | Serverless functions in same repo for Vercel deploy |
| Map | react-leaflet + OpenStreetMap | No API key required |
| CSV parsing | PapaParse | Browser-side, no server round-trip for file reading |
| Tests | pytest + HTTPX TestClient | Pure-function unit tests + live endpoint integration |
