import type { OptimizeRequest, OptimizeResponse, SampleResponse } from "./types";

const ENGINE_URL = process.env.NEXT_PUBLIC_ENGINE_URL ?? "http://localhost:8000";

export async function loadSample(): Promise<SampleResponse> {
  const response = await fetch(`${ENGINE_URL}/api/sample`);
  if (!response.ok) throw new Error("Gagal memuat data contoh.");
  return response.json();
}

export async function optimize(request: OptimizeRequest): Promise<OptimizeResponse> {
  const response = await fetch(`${ENGINE_URL}/api/optimize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Terjadi kesalahan." }));
    throw new Error(error.detail ?? "Terjadi kesalahan.");
  }
  return response.json();
}
