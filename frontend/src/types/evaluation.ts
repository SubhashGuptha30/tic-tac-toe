export type EvaluationOpponentType =
  | "random"
  | "tactical"
  | "mixed";


export interface EvaluationRunCreate {
  games: number;
  opponent_type: EvaluationOpponentType;
  tactical_probability: number;
  seed: number | null;
  snapshot_id: number | null;
}


export interface PolicySnapshot {
  id: number;
  source: string;
  q_table_hash: string;
  q_states: number;
  q_entries: number;
  alpha: number;
  gamma: number;
  tie_breaking_policy: string;
  created_at: string;
}


export interface EvaluationRun {
  id: number;
  snapshot_id: number;
  status: string;
  opponent_type: EvaluationOpponentType;
  tactical_probability: number | null;
  requested_games: number;
  completed_games: number;
  agent_wins: number;
  opponent_wins: number;
  draws: number;
  agent_win_rate: number;
  opponent_win_rate: number;
  draw_rate: number;
  total_moves: number;
  average_moves: number;
  total_agent_moves: number;
  total_opponent_moves: number;
  total_decisions: number;
  greedy_decision_rate: number;
  unique_states_visited: number;
  average_decision_confidence: number;
  average_action_gap: number;
  immediate_win_opportunities: number;
  immediate_win_successes: number;
  immediate_win_conversion_rate: number;
  immediate_block_opportunities: number;
  immediate_block_successes: number;
  immediate_block_success_rate: number;
  seed: number | null;
  tie_breaking_policy: string;
  duration_seconds: number | null;
  games_per_second: number | null;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}


export interface EvaluationComparisonRow {
  opponent_type: EvaluationOpponentType;
  evaluation_run_id: number | null;
  games: number;
  agent_win_rate: number;
  draw_rate: number;
  opponent_win_rate: number;
  average_moves: number;
  average_decision_confidence: number;
  is_available: boolean;
}


export interface EvaluationComparison {
  snapshot: PolicySnapshot;
  rows: EvaluationComparisonRow[];
}


export interface EvaluationEngineHealth {
  engine_ready: boolean;
  active_run_id: number | null;
  supported_opponents: EvaluationOpponentType[];
  tie_breaking_policy: string;
  message: string;
}
