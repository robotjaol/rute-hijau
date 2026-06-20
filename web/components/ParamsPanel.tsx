"use client";

import { useRef, useState } from "react";
import Papa from "papaparse";
import type { Point, Fleet } from "@/lib/types";

interface Props {
  fleet: Fleet;
  onFleetChange: (fleet: Fleet) => void;
  onPointsLoaded: (depot: Point, points: Point[]) => void;
  onLoadSample: () => void;
  onOptimize: () => void;
  loading: boolean;
  error: string | null;
}

export default function ParamsPanel({
  fleet,
  onFleetChange,
  onPointsLoaded,
  onLoadSample,
  onOptimize,
  loading,
  error,
}: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [parseError, setParseError] = useState<string | null>(null);

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setParseError(null);

    Papa.parse<Record<string, string>>(file, {
      header: true,
      skipEmptyLines: true,
      complete: (result) => {
        const rows = result.data;
        const depotRow = rows.find((r) => r.type === "depot");
        if (!depotRow) {
          setParseError("CSV tidak memiliki baris depot.");
          return;
        }
        let idCounter = 0;
        const depot: Point = {
          id: idCounter++,
          name: depotRow.name,
          lat: parseFloat(depotRow.lat),
          lon: parseFloat(depotRow.lon),
          demand_kg: 0,
        };
        const points: Point[] = rows
          .filter((r) => r.type === "pickup")
          .map((r) => ({
            id: idCounter++,
            name: r.name,
            lat: parseFloat(r.lat),
            lon: parseFloat(r.lon),
            demand_kg: parseInt(r.demand_kg, 10) || 0,
          }));
        onPointsLoaded(depot, points);
      },
      error: () => setParseError("Gagal membaca file CSV."),
    });
  }

  return (
    <div className="params-panel">
      <h2 className="panel-title">Parameter</h2>

      <section className="param-section">
        <h3 className="section-label">Data Titik</h3>
        <button className="btn btn-secondary" onClick={onLoadSample} disabled={loading}>
          Muat Contoh
        </button>
        <span className="separator">atau</span>
        <button className="btn btn-secondary" onClick={() => fileRef.current?.click()} disabled={loading}>
          Unggah CSV
        </button>
        <input ref={fileRef} type="file" accept=".csv" onChange={handleFile} style={{ display: "none" }} />
        {parseError && <p className="error-text">{parseError}</p>}
      </section>

      <section className="param-section">
        <h3 className="section-label">Armada</h3>
        <label className="field-label">
          Jumlah Armada
          <input
            type="number"
            min={1}
            max={20}
            value={fleet.vehicles}
            onChange={(e) => onFleetChange({ ...fleet, vehicles: parseInt(e.target.value, 10) || 1 })}
            className="field-input"
          />
        </label>
        <label className="field-label">
          Kapasitas (kg)
          <input
            type="number"
            min={1}
            value={fleet.capacity_kg}
            onChange={(e) => onFleetChange({ ...fleet, capacity_kg: parseInt(e.target.value, 10) || 1 })}
            className="field-input"
          />
        </label>
      </section>

      <button className="btn btn-primary" onClick={onOptimize} disabled={loading}>
        {loading ? "Menghitung..." : "Hitung Rute"}
      </button>

      {error && <p className="error-text">{error}</p>}
    </div>
  );
}
