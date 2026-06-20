"use client";

import type { OptimizeResponse } from "@/lib/types";

interface Props {
  result: OptimizeResponse | null;
  showMode: "baseline" | "optimized";
  onShowModeChange: (mode: "baseline" | "optimized") => void;
}

function formatRupiah(value: number): string {
  return "Rp " + value.toLocaleString("id-ID");
}

export default function SummaryPanel({ result, showMode, onShowModeChange }: Props) {
  if (!result) {
    return (
      <div className="summary-panel summary-empty">
        <p>Muat data dan tekan <strong>Hitung Rute</strong> untuk melihat hasil.</p>
      </div>
    );
  }

  const { baseline, optimized, savings_km, savings_percent, impact } = result;

  return (
    <div className="summary-panel">
      <h2 className="panel-title">Ringkasan</h2>

      <div className="toggle-row">
        <button
          className={`toggle-btn ${showMode === "baseline" ? "active" : ""}`}
          onClick={() => onShowModeChange("baseline")}
        >
          Baseline
        </button>
        <button
          className={`toggle-btn ${showMode === "optimized" ? "active" : ""}`}
          onClick={() => onShowModeChange("optimized")}
        >
          Optimal
        </button>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <span className="stat-label">Jarak Baseline</span>
          <span className="stat-value">{baseline.total_km.toFixed(2)} km</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Jarak Optimal</span>
          <span className="stat-value">{optimized.total_km.toFixed(2)} km</span>
        </div>
        <div className="stat-card stat-highlight">
          <span className="stat-label">Hemat Jarak</span>
          <span className="stat-value">{savings_km.toFixed(2)} km ({savings_percent.toFixed(1)}%)</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Hemat BBM</span>
          <span className="stat-value">{impact.fuel_saved_liter.toFixed(2)} liter/siklus</span>
        </div>
        <div className="stat-card stat-highlight">
          <span className="stat-label">Hemat Biaya/Siklus</span>
          <span className="stat-value">{formatRupiah(impact.cost_saved_rupiah_per_cycle)}</span>
        </div>
        <div className="stat-card stat-highlight">
          <span className="stat-label">Hemat Biaya/Tahun</span>
          <span className="stat-value">{formatRupiah(impact.cost_saved_rupiah_per_year)}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Kurang Emisi/Siklus</span>
          <span className="stat-value">{impact.co2_saved_kg_per_cycle.toFixed(2)} kg CO₂</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Kurang Emisi/Tahun</span>
          <span className="stat-value">{impact.co2_saved_kg_per_year} kg CO₂</span>
        </div>
      </div>

      <div className="route-list">
        <h3 className="section-label">Rute {showMode === "baseline" ? "Baseline" : "Optimal"}</h3>
        {(showMode === "baseline" ? baseline : optimized).routes.map((route) => (
          <div key={route.vehicle} className="route-item">
            <span className="route-badge" style={{ background: VEHICLE_COLORS[route.vehicle % VEHICLE_COLORS.length] }}>
              Armada {route.vehicle + 1}
            </span>
            <span className="route-stats">{route.distance_km.toFixed(2)} km · {route.load_kg} kg</span>
          </div>
        ))}
      </div>
    </div>
  );
}

const VEHICLE_COLORS = ["#16a34a", "#2563eb", "#dc2626", "#d97706", "#7c3aed", "#0891b2"];
