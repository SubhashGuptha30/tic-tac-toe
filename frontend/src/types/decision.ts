export type DecisionMode =
  | "exploration"
  | "exploitation";


export interface DecisionQValue {
  action: number;
  q_value: number;
  is_greedy: boolean;
  is_selected: boolean;
}


export interface DecisionEvent {
  id: number;
  episode_number: number | null;
  decision_number: number;
  state_key: string;
  legal_actions: number[];
  q_values: DecisionQValue[];
  epsilon: number;
  exploration_draw: number;
  decision_mode: DecisionMode;
  greedy_actions: number[];
  selected_action: number;
  selected_q: number;
  best_q: number;
  second_best_q: number;
  action_gap: number;
  was_greedy_action: boolean;
  tie_count: number;
  tactical_labels: string[];
  explanation: string;
  created_at: string;
}


export interface DecisionEventSummary {
  id: number;
  episode_number: number | null;
  decision_number: number;
  state_key: string;
  epsilon: number;
  exploration_draw: number;
  decision_mode: DecisionMode;
  selected_action: number;
  selected_q: number;
  best_q: number;
  action_gap: number;
  was_greedy_action: boolean;
  created_at: string;
}


export interface DecisionStats {
  total_decisions: number;
  exploration_decisions: number;
  exploitation_decisions: number;
  exploration_rate: number;
  exploitation_rate: number;
  greedy_selection_rate: number;
  mean_action_gap: number;
  mean_epsilon: number;
  decisions_with_ties: number;
}


export type DecisionPipelineStage =
  | "state"
  | "q-values"
  | "epsilon-gate"
  | "policy"
  | "selection";


export interface ReconstructedDecisionCell {
  index: number;
  value: number;
  symbol:
    | "X"
    | "O"
    | null;
}


export interface CounterfactualAction {
  action: number;
  q_value: number;
  gap_from_best: number;
  gap_from_selected: number;
  is_greedy: boolean;
  is_selected: boolean;
  position_type:
    | "center"
    | "corner"
    | "edge";
}
