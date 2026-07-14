import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const overview = {
  mode: "paper",
  live_execution_enabled: false,
  data_source: "synthetic",
  market_count: 3,
  paper_fill_count: 0
};

const markets = [
  {
    market_id: "synthetic-weather-001",
    question: "Will the demo sensor report a clear day?",
    sequence: 8,
    yes_price: "0.44",
    no_price: "0.56"
  }
];

function jsonResponse(body: object): Promise<Response> {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    })
  );
}

describe("operations dashboard", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        if (url.endsWith("/api/overview")) return jsonResponse(overview);
        if (url.endsWith("/api/markets")) return jsonResponse(markets);
        if (url.endsWith("/api/diagnostics")) {
          return jsonResponse({
            execution_boundary: "paper-only",
            synthetic_data: "ok",
            ledger: "ok",
            outbound_access: "public-read-only"
          });
        }
        if (url.endsWith("/api/paper/run") && init?.method === "POST") {
          return jsonResponse({
            request_id: "dummy-synthetic-weather-001-8",
            status: "simulated"
          });
        }
        return Promise.reject(new Error(`Unexpected request: ${url}`));
      })
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("makes the safety boundary, health, synthetic market and paper activity visible", async () => {
    render(<App />);

    expect(screen.getByText("LIVE EXECUTION ABSENT")).toBeInTheDocument();
    expect(await screen.findByText("PAPER / SYNTHETIC")).toBeInTheDocument();
    expect(screen.getByText("SYSTEM NOMINAL")).toBeInTheDocument();
    expect(screen.getByText("Will the demo sensor report a clear day?")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Run paper cycle" }));

    expect(await screen.findByText("dummy-synthetic-weather-001-8")).toBeInTheDocument();
    expect(screen.getByText("SIMULATED")).toBeInTheDocument();
  });
});
