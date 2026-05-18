export type MetricSet = {
  month: number;
  cash: number;
  cash_change: number;
  cash_coverage_label: string;
  cash_coverage_months: number;
  mrr: number;
  mrr_change: number;
  users: number;
  users_change: number;
  product_score: number;
  product_change: number;
  reputation: number;
  founder_equity: number;
  valuation: number;
};

export type BoardItem = {
  name: string;
  role: string;
  message: string;
  confidence: number;
};

export type CompetitorItem = {
  name: string;
  status: string;
  mrr: number;
  trend: 'up' | 'down' | 'flat';
};

export type SuggestionItem = {
  title: string;
  description: string;
  command: string;
  risk_level: string;
  reason: string;
};

export type GameStateView = {
  session_id: number;
  status: string;
  metrics: MetricSet;
  stage: {
    company_name: string;
    week_label: string;
    focus: string;
  };
  core_tension: {
    title: string;
    description: string;
    severity: string;
    next_focus: string;
  };
  insight: {
    title: string;
    description: string;
  };
  board: BoardItem[];
  competitors: CompetitorItem[];
  advice_entry: {
    label: string;
    summary: string;
  };
  ending: {
    type: string;
    description: string;
  };
};

export type SuggestionResponse = {
  items: SuggestionItem[];
  warning: string;
  recommended_focus: string;
};

export type TurnResponse = {
  state: GameStateView;
  turn: {
    month: number;
    delta_reasons?: string[];
  };
};
