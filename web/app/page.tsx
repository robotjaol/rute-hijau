"use client";

import dynamic from "next/dynamic";
import { useState } from "react";
import ParamsPanel from "@/components/ParamsPanel";
import SummaryPanel from "@/components/SummaryPanel";
import { loadSample, optimize } from "@/lib/api";
import type { Point, Fleet, OptimizeResponse } from "@/lib/types";

const MapView = dynamic(() => import("@/components/MapView"), { ssr: false });

const DEFAULT_FLEET: Fleet = { vehicles: 4, capacity_kg: 780 };

export default function HomePage() {
  const [depot, setDepot] = useState<Point | null>(null);
  const [points, setPoints] = useState<Point[]>([]);
  const [fleet, setFleet] = useState<Fleet>(DEFAULT_FLEET);
  const [result, setResult] = useState<OptimizeResponse | null>(null);
  const [showMode, setShowMode] = useState<"baseline" | "optimized">("optimized");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleLoadSample() {
    setError(null);
    setLoading(true);
    try {
      const data = await loadSample();
      setDepot(data.depot);
      setPoints(data.points);
      setFleet(data.fleet);
      setResult(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function handleOptimize() {
    if (!depot) { setError("Muat data titik terlebih dahulu."); return; }
    if (points.length === 0) { setError("Daftar titik jemput tidak boleh kosong."); return; }
    setError(null);
    setLoading(true);
    try {
      const response = await optimize({ depot, points, fleet, distance_mode: "haversine" });
      setResult(response);
      setShowMode("optimized");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  const activeSolution = result ? (showMode === "baseline" ? result.baseline : result.optimized) : null;

  return (
    <>
      <header className="app-header">
        <h1>RuteHijau</h1>
        <span>Optimasi Rute Pengangkutan Sampah</span>
      </header>
      <div className="app-body">
        <aside className="sidebar">
          <ParamsPanel
            fleet={fleet}
            onFleetChange={setFleet}
            onPointsLoaded={(d, p) => { setDepot(d); setPoints(p); setResult(null); }}
            onLoadSample={handleLoadSample}
            onOptimize={handleOptimize}
            loading={loading}
            error={error}
          />
        </aside>

        <main className="map-area">
          <MapView depot={depot} points={points} solution={activeSolution} showMode={showMode} />
        </main>

        <aside className="sidebar sidebar-right">
          <SummaryPanel result={result} showMode={showMode} onShowModeChange={setShowMode} />
        </aside>
      </div>
    </>
  );
}
