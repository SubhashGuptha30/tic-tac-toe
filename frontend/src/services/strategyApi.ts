import api from "./api";

import type {
  DecisionInspection,
  EpisodeInspection,
  EpisodeSummary,
  StateInspection,
  StateSummary,
  StrategyEvidenceItem,
  StrategyKey,
  StrategyOverview,
} from "../types/strategy";


export async function getStrategyOverview():
Promise<StrategyOverview> {
  const response =
    await api.get<StrategyOverview>(
      "/api/strategy/overview",
    );

  return response.data;
}


export async function getStrategyEvidence(
  strategy: StrategyKey,
  limit = 100,
): Promise<StrategyEvidenceItem[]> {
  const response =
    await api.get<StrategyEvidenceItem[]>(
      "/api/strategy/evidence",
      {
        params: {
          strategy,
          limit,
        },
      },
    );

  return response.data;
}


export async function getQTableStates(
  limit = 100,
  offset = 0,
): Promise<StateSummary[]> {
  const response =
    await api.get<StateSummary[]>(
      "/api/strategy/q-table/states",
      {
        params: {
          limit,
          offset,
        },
      },
    );

  return response.data;
}


export async function inspectQTableState(
  stateKey: string,
): Promise<StateInspection> {
  const response =
    await api.get<StateInspection>(
      `/api/strategy/q-table/state/${stateKey}`,
    );

  return response.data;
}


export async function inspectDecision(
  stateKey: string,
): Promise<DecisionInspection> {
  const response =
    await api.get<DecisionInspection>(
      `/api/strategy/decision/${stateKey}`,
    );

  return response.data;
}


export async function getEpisodes(
  limit = 100,
  offset = 0,
): Promise<EpisodeSummary[]> {
  const response =
    await api.get<EpisodeSummary[]>(
      "/api/strategy/episodes",
      {
        params: {
          limit,
          offset,
        },
      },
    );

  return response.data;
}


export async function inspectEpisode(
  episodeNumber: number,
): Promise<EpisodeInspection> {
  const response =
    await api.get<EpisodeInspection>(
      `/api/strategy/episodes/${episodeNumber}`,
    );

  return response.data;
}
