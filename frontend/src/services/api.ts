import axios from "axios";

import type {
  AgentMetrics,
  AgentMoveResponse,
  AgentParameterUpdate,
  GameState,
  HumanMoveResponse,
  ResetResponse,
} from "../types/game";
import type { HealthResponse } from "../types/system";


const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 5000,
});


export async function getBackendHealth(): Promise<HealthResponse> {
  const response = await api.get<HealthResponse>("/api/health");
  return response.data;
}


export async function getGameState(): Promise<GameState> {
  const response = await api.get<GameState>("/api/game/state");
  return response.data;
}


export async function makeHumanMove(
  action: number,
): Promise<HumanMoveResponse> {
  const response = await api.post<HumanMoveResponse>(
    "/api/game/human-move",
    { action },
  );

  return response.data;
}


export async function makeAgentMove(): Promise<AgentMoveResponse> {
  const response = await api.post<AgentMoveResponse>(
    "/api/game/agent-move",
  );

  return response.data;
}


export async function resetGame(): Promise<ResetResponse> {
  const response = await api.post<ResetResponse>(
    "/api/game/reset",
  );

  return response.data;
}


export async function getAgentMetrics(): Promise<AgentMetrics> {
  const response = await api.get<AgentMetrics>(
    "/api/agent/metrics",
  );

  return response.data;
}


export async function updateAgentParameters(
  parameters: AgentParameterUpdate,
): Promise<AgentMetrics> {
  const response = await api.put<AgentMetrics>(
    "/api/agent/parameters",
    parameters,
  );

  return response.data;
}


export async function resetAgentBrain(): Promise<ResetResponse> {
  const response = await api.delete<ResetResponse>(
    "/api/agent/brain",
  );

  return response.data;
}


export default api;
