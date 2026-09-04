export interface GameStats {
  human_wins: number;
  agent_wins: number;
  draws: number;
  episodes: number;
}


export interface GameState {
  board: string[];
  current_player: "X" | "O";
  game_over: boolean;
  winner: "X" | "O" | null;
  winning_line: number[] | null;
  is_draw: boolean;
  legal_actions: number[];
  stats: GameStats;
}


export interface AgentMetrics {
  alpha: number;
  gamma: number;
  epsilon: number;
  epsilon_min: number;
  epsilon_decay: number;
  total_decisions: number;
  exploration_moves: number;
  exploitation_moves: number;
  total_updates: number;
  states_known: number;
  learned_state_actions: number;
}


export interface DecisionData {
  state: string;
  action: number;
  decision_mode:
    | "exploration"
    | "exploitation";
  epsilon: number;
  random_sample: number;
  q_values: number[];
  legal_actions: number[];
  best_action: number | null;
  best_q_value: number;
  legal_q_values?: Record<string, number>;
  greedy_actions?: number[];
  selected_q_value?: number;
  second_best_action?: number | null;
  second_best_q_value?: number;
  action_gap?: number;
}


export interface LearningUpdateData {
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
}


export interface HumanMoveResponse {
  game: GameState;
  learning_update:
    | LearningUpdateData
    | null;
  agent_metrics: AgentMetrics;
}


export interface AgentMoveResponse {
  action: number;
  decision_event_id: number | null;
  decision: DecisionData;
  learning_update:
    | LearningUpdateData
    | null;
  game: GameState;
  agent_metrics: AgentMetrics;
}


export interface ResetResponse {
  game: GameState;
  agent_metrics: AgentMetrics;
}


export interface AgentParameterUpdate {
  alpha: number;
  gamma: number;
  epsilon: number;
  epsilon_min: number;
  epsilon_decay: number;
}
