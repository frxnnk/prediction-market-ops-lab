import { useEffect, useState } from "react";

import { loadDashboard, runPaperCycle } from "./api";
import type { DashboardData, PaperResult, SyntheticMarket } from "./types";
import "./styles.css";

const emptyActivity = "NO PAPER CYCLE RUN IN THIS SESSION";

function MarketRow({ market, index }: { market: SyntheticMarket; index: number }) {
  return (
    <article className="market-row">
      <div className="market-index">MKT-{String(index + 1).padStart(2, "0")}</div>
      <div className="market-copy">
        <p className="eyebrow">SYNTHETIC FIXTURE · SEQ {market.sequence}</p>
        <h3>{market.question}</h3>
        <code>{market.market_id}</code>
      </div>
      <div className="quote quote-yes">
        <span>YES</span>
        <strong>{market.yes_price}</strong>
      </div>
      <div className="quote quote-no">
        <span>NO</span>
        <strong>{market.no_price}</strong>
      </div>
    </article>
  );
}

function App() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [activity, setActivity] = useState<PaperResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    loadDashboard(controller.signal)
      .then(setData)
      .catch((cause: unknown) => {
        if (!controller.signal.aborted) {
          setError(cause instanceof Error ? cause.message : "Unknown dashboard error");
        }
      });
    return () => controller.abort();
  }, []);

  async function handlePaperRun() {
    const market = data?.markets[0];
    if (!market || running) return;
    setRunning(true);
    setError(null);
    try {
      const result = await runPaperCycle(market.market_id);
      setActivity(result);
      setData(await loadDashboard());
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Paper cycle failed");
    } finally {
      setRunning(false);
    }
  }

  const nominal = Boolean(data && !error);

  return (
    <main>
      <div className="safety-strip">
        <span>LIVE EXECUTION ABSENT</span>
        <span>NO ORDERS · NO TRANSFERS · NO PRIVATE KEYS</span>
      </div>

      <header className="masthead">
        <div>
          <p className="eyebrow">PUBLIC SYSTEMS DEMONSTRATOR / 01</p>
          <h1>Prediction Market<br />Ops Lab</h1>
        </div>
        <div className="mode-plate">
          <span>RUNTIME MODE</span>
          <strong>{data ? "PAPER / SYNTHETIC" : "INITIALIZING"}</strong>
          <small>DETERMINISTIC · LOCAL-FIRST</small>
        </div>
      </header>

      <section className="status-rail" aria-label="System status">
        <div className="status-lead">
          <span className={nominal ? "pulse" : "pulse pulse-warn"} />
          <div>
            <strong>{nominal ? "SYSTEM NOMINAL" : error ? "SYSTEM DEGRADED" : "CHECKING SYSTEM"}</strong>
            <small>Health surface / current process</small>
          </div>
        </div>
        <StatusCell label="Execution" value={data?.diagnostics.execution_boundary ?? "checking"} />
        <StatusCell label="Fixtures" value={data?.diagnostics.synthetic_data ?? "checking"} />
        <StatusCell label="Ledger" value={data?.diagnostics.ledger ?? "checking"} />
        <StatusCell label="Outbound" value={data?.diagnostics.outbound_access ?? "checking"} />
      </section>

      {error && <div className="error-panel" role="alert">{error}</div>}

      <div className="console-grid">
        <section className="market-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">MARKET INPUT / READ MODEL</p>
              <h2>Synthetic watchlist</h2>
            </div>
            <span>{data?.overview.market_count ?? "–"} FIXTURES</span>
          </div>
          <div className="market-list">
            {data?.markets.map((market, index) => (
              <MarketRow key={market.market_id} market={market} index={index} />
            )) ?? <div className="loading-line">Loading deterministic fixtures…</div>}
          </div>
        </section>

        <aside className="operations-panel">
          <div className="section-heading compact">
            <div>
              <p className="eyebrow">CONTROL SURFACE</p>
              <h2>Paper cycle</h2>
            </div>
          </div>

          <div className="boundary-box">
            <span>BOUNDARY ASSERTION</span>
            <strong>NON-PAPER MODES REJECTED BEFORE PERSISTENCE</strong>
          </div>

          <button type="button" onClick={handlePaperRun} disabled={!data || running}>
            <span>{running ? "Running…" : "Run paper cycle"}</span>
            <b aria-hidden="true">→</b>
          </button>

          <div className="activity" aria-live="polite">
            <div className="activity-head">
              <span>LAST SESSION EVENT</span>
              <i>{activity ? "01" : "00"}</i>
            </div>
            {activity ? (
              <div className="activity-event">
                <strong>{activity.request_id}</strong>
                <span>{activity.status.toUpperCase()}</span>
              </div>
            ) : (
              <p>{emptyActivity}</p>
            )}
          </div>

          <dl className="readout">
            <div><dt>Recorded fills</dt><dd>{data?.overview.paper_fill_count ?? "–"}</dd></div>
            <div><dt>External writes</dt><dd>0</dd></div>
            <div><dt>Funds at risk</dt><dd>$0.00</dd></div>
          </dl>
        </aside>
      </div>

      <footer>
        <span>INDEPENDENT IMPLEMENTATION · SYNTHETIC DATA ONLY</span>
        <span>HEALTH / DIAGNOSTICS / PAPER AUTOMATION</span>
      </footer>
    </main>
  );
}

function StatusCell({ label, value }: { label: string; value: string }) {
  return (
    <div className="status-cell">
      <small>{label}</small>
      <strong>{value.toUpperCase()}</strong>
    </div>
  );
}

export default App;
