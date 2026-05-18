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
  phase_goals?: {
    phase_label: string;
    title: string;
    summary: string;
    objectives: Array<{
      id: string;
      title: string;
      status: string;
      progress_label: string;
      action_directions: string[];
      risk_hint: string;
    }>;
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

export type CommandPreviewAction = {
  type: string;
  label: string;
  intent: string;
  budget: number;
  budget_label: string;
  risk_label: string;
  tradeoffs: string[];
};

export type CommandPreviewResponse = {
  status: 'ready' | 'needs_clarification';
  summary: string;
  guardrail: string;
  actions: CommandPreviewAction[];
};

export type TurnFactChange = {
  metric?: string;
  label: string;
  delta?: number;
  value: string;
  tone: string;
};

export type TurnFacts = {
  month: number;
  command: string;
  changes: TurnFactChange[];
  replay_basis: string[];
  next_pressure: string;
  authority?: 'backend-turn-engine';
};

export type RoleMemoryPayload = {
  role_id?: string;
  role_name?: string;
  month?: number;
  fact: string;
  implication: string;
  source?: 'settled-turn-facts';
  relevance_score?: number;
};

export type OfficeSignalPayload = {
  id: string;
  room_id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical' | 'info' | 'warning' | 'opportunity';
  source:
    | 'settled-core-tension'
    | 'settled-business-insight'
    | 'turn-facts'
    | 'role-memory'
    | 'competitor-facts'
    | 'scenario';
  visual_intent?: 'surface-in-office';
};

export type StoryEventPayload = {
  id: string;
  title: string;
  description: string;
  tone: 'neutral' | 'good' | 'bad' | 'warning' | 'opportunity';
  source: 'rule-event' | 'competitor-fact' | 'business-insight';
};

export type ObjectiveUpdatePayload = {
  id: string;
  title: string;
  status: '完成' | '推进中' | '承压' | string;
  summary: string;
};

export type GameReviewResponse = {
  session_id?: number;
  ending_status?: string;
  review_phase?: string;
  status_copy?: string;
  ending_title?: string;
  ending_summary?: string;
  archive_summary?: string;
  archive_timeline?: Array<{
    id?: string;
    title: string;
    description: string;
    month?: number;
    tone?: string;
    source?: string;
  }>;
  archive_badges?: Array<{
    code?: string;
    title: string;
    description?: string;
    rarity?: string;
    source?: string;
  }>;
  advice_for_next_run?: string;
  next_run_suggestions?: string[];
  final_metrics?: Record<string, unknown>;
  achievement_cards?: Array<{
    code?: string;
    title: string;
    description?: string;
    rarity?: string;
  }>;
  achievements?: Array<{
    code?: string;
    title: string;
    description?: string;
    rarity?: string;
  }>;
  achievement_summary?: {
    total_count: number;
    rare_count: number;
    summary: string;
  };
  key_moments?: Array<{
    title: string;
    description: string;
  }>;
};

export type TurnResponse = {
  state: GameStateView;
  turn: {
    month: number;
    delta_reasons?: string[];
    turn_facts?: TurnFacts;
    role_memory?: RoleMemoryPayload[];
    recent_role_memory?: RoleMemoryPayload[];
    memory_history?: RoleMemoryPayload[];
    office_signals?: OfficeSignalPayload[];
    story_events?: StoryEventPayload[];
    objective_updates?: ObjectiveUpdatePayload[];
  };
  turn_facts?: TurnFacts;
  role_memory?: RoleMemoryPayload[];
  recent_role_memory?: RoleMemoryPayload[];
  memory_history?: RoleMemoryPayload[];
  office_signals?: OfficeSignalPayload[];
  story_events?: StoryEventPayload[];
  objective_updates?: ObjectiveUpdatePayload[];
};
