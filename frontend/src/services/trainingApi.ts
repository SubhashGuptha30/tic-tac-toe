import api from "./api";

import type {
  TrainingEngineHealth,
  TrainingEpisode,
  TrainingRun,
  TrainingRunCreate,
  TrainingRunStats,
} from "../types/training";


export async function getTrainingHealth():
Promise<TrainingEngineHealth> {
  const response =
    await api.get<TrainingEngineHealth>(
      "/api/training/health",
    );

  return response.data;
}


export async function createTrainingRun(
  payload: TrainingRunCreate,
): Promise<TrainingRun> {
  const response =
    await api.post<TrainingRun>(
      "/api/training/runs",
      payload,
    );

  return response.data;
}


export async function listTrainingRuns(
  limit = 50,
  offset = 0,
): Promise<TrainingRun[]> {
  const response =
    await api.get<TrainingRun[]>(
      "/api/training/runs",
      {
        params: {
          limit,
          offset,
        },
      },
    );

  return response.data;
}


export async function getTrainingRun(
  runId: number,
): Promise<TrainingRun> {
  const response =
    await api.get<TrainingRun>(
      `/api/training/runs/${runId}`,
    );

  return response.data;
}


export async function getTrainingEpisodes(
  runId: number,
  limit = 1000,
  offset = 0,
): Promise<TrainingEpisode[]> {
  const response =
    await api.get<TrainingEpisode[]>(
      `/api/training/runs/${runId}/episodes`,
      {
        params: {
          limit,
          offset,
        },
      },
    );

  return response.data;
}


export async function getTrainingRunStats(
  runId: number,
): Promise<TrainingRunStats> {
  const response =
    await api.get<TrainingRunStats>(
      `/api/training/runs/${runId}/stats`,
    );

  return response.data;
}
