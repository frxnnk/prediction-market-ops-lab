export interface Overview {
  mode: "paper";
  live_execution_enabled: false;
  data_source: "synthetic";
  market_count: number;
  paper_fill_count: number;
}

export interface SyntheticMarket {
  market_id: string;
  question: string;
  sequence: number;
  yes_price: string;
  no_price: string;
}

export interface Diagnostics {
  execution_boundary: string;
  synthetic_data: string;
  ledger: string;
  outbound_access: string;
}

export interface PaperResult {
  request_id: string;
  status: "simulated";
}

export interface DashboardData {
  overview: Overview;
  markets: SyntheticMarket[];
  diagnostics: Diagnostics;
}
