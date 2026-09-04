export type TrainingOpponentType =
  | "random"
  | "tactical"
  | "mixed";


export interface TrainingRunCreate {
  episodes: number;
  opponent_type: TrainingOpponentType;
  tactical_probability: number;
  seed: number | null;
}


export interface TrainingRun {
  id: number;
  status: string;
  opponent_type: TrainingOpponentType;
  tactical_probability: number | null;
  requested_episodes: number;
  completed_episodes: number;
  agent_wins: number;
  opponent_wins: number;
  draws: number;
  total_agent_moves: number;
  total_opponent_moves: number;
  epsilon_start: number;
  epsilon_end: number | null;
  q_states_start: number;
  q_states_end: number | null;
  q_entries_start: number;
  q_entries_end: number | null;
  cumulative_reward: number;
  mean_reward: number;
  duration_seconds: number | null;
  episodes_per_second: number | null;
  seed: number | null;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}


export interface TrainingEpisode {
  id: number;
  training_run_id: number;
  episode_index: number;
  result:
    | "agent_win"
    | "opponent_win"
    | "draw";
  reward: number;
  agent_moves: number;
  opponent_moves: number;
  epsilon_before: number;
  epsilon_after: number;
  final_board_key: string;
  move_count: number;
  duration_ms: number;
  created_at: string;
}


export interface TrainingRunStats {
  run_id: number;
  completed_episodes: number;
  requested_episodes: number;
  progress: number;
  agent_wins: number;
  opponent_wins: number;
  draws: number;
  agent_win_rate: number;
  opponent_win_rate: number;
  draw_rate: number;
  cumulative_reward: number;
  mean_reward: number;
  epsilon_start: number;
  current_epsilon: number;
  q_states_start: number;
  current_q_states: number;
  q_entries_start: number;
  current_q_entries: number;
  duration_seconds: number | null;
  episodes_per_second: number | null;
}


export interface TrainingEngineHealth {
  engine_ready: boolean;
  supported_opponents: TrainingOpponentType[];
  active_run_id: number | null;
  agent_available: boolean;
  message: string;
}


export interface TrainingOutcomePoint {
  episode: number;
  agent_win_rate: number;
  opponent_win_rate: number;
  draw_rate: number;
}


export interface TrainingScalarPoint {
  episode: number;
  value: number;
}


export interface TrainingQGrowthPoint {
  episode: number;
  q_states: number;
  q_entries: number;
}
