export interface OutcomeCounts {
  human_wins: number;
  agent_wins: number;
  draws: number;
  total_episodes: number;
}


export interface WinRates {
  human_win_rate: number;
  agent_win_rate: number;
  draw_rate: number;
}


export interface QValueHealth {
  total_persisted_actions: number;
  positive_q_values: number;
  negative_q_values: number;
  zero_q_values: number;
  min_q_value: number;
  max_q_value: number;
  mean_q_value: number;
  mean_absolute_q: number;
}


export interface TDErrorHealth {
  total_updates: number;
  mean_td_error: number;
  mean_absolute_td_error: number;
  min_td_error: number;
  max_td_error: number;
  recent_mean_absolute_td_error: number;
}


export interface AnalyticsOverview {
  outcomes: OutcomeCounts;
  win_rates: WinRates;
  known_states: number;
  persisted_state_actions: number;
  exploration_moves: number;
  exploitation_moves: number;
  exploration_rate: number;
  exploitation_rate: number;
  current_epsilon: number;
  q_value_health: QValueHealth;
  td_error_health: TDErrorHealth;
}


export interface LearningCurvePoint {
  episode: number;
  agent_win_rate: number;
  human_win_rate: number;
  draw_rate: number;
  rolling_agent_win_rate: number;
  rolling_human_win_rate: number;
  rolling_draw_rate: number;
}


export interface OutcomeTimelinePoint {
  episode: number;
  outcome: "agent" | "human" | "draw";
  winner: string | null;
  is_draw: boolean;
  epsilon_after: number;
  total_updates_after: number;
  created_at: string;
}


export interface TDErrorPoint {
  update_id: number;
  episode: number;
  td_error: number;
  absolute_td_error: number;
  rolling_mean_absolute_td_error: number;
  terminal: boolean;
  created_at: string;
}


export interface RewardPoint {
  update_id: number;
  episode: number;
  reward: number;
  cumulative_reward: number;
  terminal: boolean;
  created_at: string;
}


export interface EpsilonPoint {
  episode: number;
  epsilon: number;
  created_at: string;
}


export interface LearningUpdateDetail {
  id: number;
  episode: number;
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


export interface AnalyticsDataset {
  learning_curve: LearningCurvePoint[];
  outcome_timeline: OutcomeTimelinePoint[];
  td_error_curve: TDErrorPoint[];
  reward_trajectory: RewardPoint[];
  epsilon_curve: EpsilonPoint[];
}
