import type { DashboardData, Diagnostics, Overview, PaperResult, SyntheticMarket } from "./types";

async function requestJson<T>(
  path: string,
  options: RequestInit = {},
  signal?: AbortSignal
): Promise<T> {
  const response = await fetch(path, { ...options, signal });
  if (!response.ok) {
    throw new Error(`Operations API returned ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function loadDashboard(signal?: AbortSignal): Promise<DashboardData> {
  const [overview, markets, diagnostics] = await Promise.all([
    requestJson<Overview>("/api/overview", {}, signal),
    requestJson<SyntheticMarket[]>("/api/markets", {}, signal),
    requestJson<Diagnostics>("/api/diagnostics", {}, signal)
  ]);
  return { overview, markets, diagnostics };
}

export function runPaperCycle(marketId: string): Promise<PaperResult> {
  return requestJson<PaperResult>("/api/paper/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ market_id: marketId })
  });
}
