export type StrategyKey =
  | "immediate_win"
  | "immediate_block"
  | "fork_creation"
  | "fork_prevention"
  | "center_preference"
  | "corner_preference"
  | "edge_preference";


export type WorkspaceTab =
  | "live"
  | "training"
  | "evaluation"
  | "strategy"
  | "q-explorer"
  | "decisions"
  | "episodes";


export interface BoardCell {
  index: number;
  value: number;
  symbol: "X" | "O" | null;
}


export interface ActionValue {
  action: number;
  q_value: number;
  rank: number;
  is_legal: boolean;
  is_best: boolean;
  position_type:
    | "center"
    | "corner"
    | "edge";
  action_gap_from_best: number;
  is_immediate_win: boolean;
  is_immediate_block: boolean;
  is_fork_creation: boolean;
  is_fork_prevention: boolean;
}


export interface PolicyConfidenceResponse {
  best_action: number | null;
  best_q: number;
  second_best_q: number;
  action_gap: number;
  normalized_confidence: number;
  tied_best_actions: number[];
}


export interface TacticalEvidence {
  immediate_wins: number[];
  immediate_blocks: number[];
  fork_creations: number[];
  fork_preventions: number[];
}


export interface StateInspection {
  state_key: string;
  board: BoardCell[];
  legal_actions: number[];
  action_values: ActionValue[];
  policy_confidence:
    PolicyConfidenceResponse;
  tactical_evidence:
    TacticalEvidence;
  q_rows_found: number;
}


export interface StateSummary {
  state_key: string;
  stored_actions: number;
  legal_actions: number;
  best_action: number | null;
  best_q: number;
  action_gap: number;
  visit_updates: number;
}


export interface StrategyMetric {
  key: string;
  label: string;
  opportunities: number;
  aligned_states: number;
  evidence_rate: number;
  interpretation: string;
}


export interface PositionPreferenceMetric {
  key: string;
  label: string;
  eligible_states: number;
  preference_mass: number;
  preference_rate: number;
  interpretation: string;
}


export interface StrategyOverview {
  analyzed_states: number;
  states_with_legal_actions: number;
  states_with_nonzero_q: number;
  states_with_unique_best_action: number;
  mean_action_gap: number;
  mean_normalized_confidence: number;
  immediate_win: StrategyMetric;
  immediate_block: StrategyMetric;
  fork_creation: StrategyMetric;
  fork_prevention: StrategyMetric;
  center_preference:
    PositionPreferenceMetric;
  corner_preference:
    PositionPreferenceMetric;
  edge_preference:
    PositionPreferenceMetric;
}


export interface StrategyEvidenceItem {
  state_key: string;
  strategy: string;
  opportunity_actions: number[];
  greedy_actions: number[];
  alignment_score: number;
  best_action: number | null;
  best_q: number;
  action_gap: number;
}


export interface EpisodeSummary {
  episode_number: number;
  winner: string | null;
  is_draw: boolean;
  outcome:
    | "agent"
    | "human"
    | "draw"
    | "unknown";
  epsilon_after: number;
  total_updates_after: number;
  learning_event_count: number;
  created_at: string;
}


export interface EpisodeLearningEvent {
  id: number;
  state: string;
  action: number;
  reward: number;
  old_q: number;
  best_future_q: number;
  td_target: number;
  td_error: number;
  new_q: number;
  delta_q: number;
  alpha: number;
  gamma: number;
  terminal: boolean;
  created_at: string;
}


export interface EpisodeInspection {
  episode_number: number;
  winner: string | null;
  is_draw: boolean;
  outcome:
    | "agent"
    | "human"
    | "draw"
    | "unknown";
  epsilon_after: number;
  total_updates_after: number;
  created_at: string;
  learning_events:
    EpisodeLearningEvent[];
}


export interface DecisionInspection {
  state_key: string;
  best_action: number | null;
  greedy_actions: number[];
  best_q: number;
  second_best_q: number;
  action_gap: number;
  normalized_confidence: number;
  immediate_win_alignment: number;
  immediate_block_alignment: number;
  fork_creation_alignment: number;
  fork_prevention_alignment: number;
  tactical_labels: string[];
}
