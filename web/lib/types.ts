export interface Point {
  id: number;
  name: string;
  lat: number;
  lon: number;
  demand_kg: number;
}

export interface Fleet {
  vehicles: number;
  capacity_kg: number;
}

export interface RouteLeg {
  vehicle: number;
  sequence: number[];
  distance_km: number;
  load_kg: number;
}

export interface Solution {
  total_km: number;
  routes: RouteLeg[];
}

export interface Impact {
  distance_saved_km: number;
  fuel_saved_liter: number;
  cost_saved_rupiah_per_cycle: number;
  cost_saved_rupiah_per_year: number;
  co2_saved_kg_per_cycle: number;
  co2_saved_kg_per_year: number;
  assumptions: Record<string, number>;
}

export interface OptimizeResponse {
  baseline: Solution;
  optimized: Solution;
  savings_km: number;
  savings_percent: number;
  impact: Impact;
  meta: Record<string, number | string>;
}

export interface SampleResponse {
  depot: Point;
  points: Point[];
  fleet: Fleet;
}

export interface OptimizeRequest {
  depot: Point;
  points: Point[];
  fleet: Fleet;
  distance_mode: "haversine" | "osrm";
}
