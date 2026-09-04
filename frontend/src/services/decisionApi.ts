import api from "./api";

import type {
  DecisionEvent,
  DecisionEventSummary,
  DecisionStats,
} from "../types/decision";


export async function getLatestDecision():
Promise<DecisionEvent | null> {
  const response =
    await api.get<DecisionEvent | null>(
      "/api/decisions/latest",
    );

  return response.data;
}


export async function getDecisionHistory(
  limit = 50,
  offset = 0,
): Promise<DecisionEventSummary[]> {
  const response =
    await api.get<DecisionEventSummary[]>(
      "/api/decisions/history",
      {
        params: {
          limit,
          offset,
        },
      },
    );

  return response.data;
}


export async function getDecisionStats():
Promise<DecisionStats> {
  const response =
    await api.get<DecisionStats>(
      "/api/decisions/stats",
    );

  return response.data;
}


export async function getDecisionById(
  decisionId: number,
): Promise<DecisionEvent> {
  const response =
    await api.get<DecisionEvent>(
      `/api/decisions/${decisionId}`,
    );

  return response.data;
}
