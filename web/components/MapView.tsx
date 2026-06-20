"use client";

import { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import type { Point, Solution } from "@/lib/types";

const VEHICLE_COLORS = ["#16a34a", "#2563eb", "#dc2626", "#d97706", "#7c3aed", "#0891b2"];

const depotIcon = L.divIcon({
  className: "",
  html: `<div style="width:20px;height:20px;background:#16a34a;border:3px solid white;border-radius:50%;box-shadow:0 1px 3px rgba(0,0,0,0.4)"></div>`,
  iconAnchor: [10, 10],
});

function pickupIcon(color: string) {
  return L.divIcon({
    className: "",
    html: `<div style="width:14px;height:14px;background:${color};border:2px solid white;border-radius:50%;box-shadow:0 1px 3px rgba(0,0,0,0.3)"></div>`,
    iconAnchor: [7, 7],
  });
}

function FitBounds({ depot, points }: { depot: Point | null; points: Point[] }) {
  const map = useMap();
  useEffect(() => {
    const all = depot ? [depot, ...points] : points;
    if (all.length === 0) return;
    const bounds = L.latLngBounds(all.map((p) => [p.lat, p.lon]));
    map.fitBounds(bounds, { padding: [40, 40] });
  }, [depot, points, map]);
  return null;
}

interface Props {
  depot: Point | null;
  points: Point[];
  solution: Solution | null;
  showMode: "baseline" | "optimized";
}

export default function MapView({ depot, points, solution, showMode }: Props) {
  const allPoints = depot ? [depot, ...points] : points;
  const pointById: Record<number, Point> = {};
  allPoints.forEach((p) => { pointById[p.id] = p; });

  return (
    <MapContainer
      center={[-7.32, 112.72]}
      zoom={12}
      style={{ height: "100%", width: "100%" }}
      scrollWheelZoom
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      />
      <FitBounds depot={depot} points={points} />

      {depot && (
        <Marker position={[depot.lat, depot.lon]} icon={depotIcon}>
          <Popup>{depot.name} (Depot)</Popup>
        </Marker>
      )}

      {solution &&
        solution.routes.map((route) => {
          const color = VEHICLE_COLORS[route.vehicle % VEHICLE_COLORS.length];
          const coords = route.sequence
            .map((id) => pointById[id])
            .filter(Boolean)
            .map((p) => [p.lat, p.lon] as [number, number]);

          return (
            <Polyline
              key={`route-${route.vehicle}`}
              positions={coords}
              pathOptions={{ color, weight: 3, opacity: 0.8 }}
            />
          );
        })}

      {solution &&
        solution.routes.map((route) => {
          const color = VEHICLE_COLORS[route.vehicle % VEHICLE_COLORS.length];
          return route.sequence.slice(1, -1).map((id) => {
            const p = pointById[id];
            if (!p) return null;
            return (
              <Marker key={`pt-${showMode}-${id}`} position={[p.lat, p.lon]} icon={pickupIcon(color)}>
                <Popup>
                  <strong>{p.name}</strong>
                  <br />
                  {p.demand_kg} kg · Armada {route.vehicle + 1}
                </Popup>
              </Marker>
            );
          });
        })}

      {!solution &&
        points.map((p) => (
          <Marker key={`idle-${p.id}`} position={[p.lat, p.lon]} icon={pickupIcon("#64748b")}>
            <Popup>
              {p.name} · {p.demand_kg} kg
            </Popup>
          </Marker>
        ))}
    </MapContainer>
  );
}
