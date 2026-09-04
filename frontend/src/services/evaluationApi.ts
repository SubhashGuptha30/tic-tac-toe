import api from "./api";

import type {
  EvaluationComparison,
  EvaluationEngineHealth,
  EvaluationRun,
  EvaluationRunCreate,
  PolicySnapshot,
} from "../types/evaluation";


export async function getEvaluationHealth():
Promise<EvaluationEngineHealth> {
  const response =
    await api.get<EvaluationEngineHealth>(
      "/api/evaluation/health",
    );

  return response.data;
}


export async function createEvaluationRun(
  payload: EvaluationRunCreate,
): Promise<EvaluationRun> {
  const response = await api.post<EvaluationRun>(
    "/api/evaluation/runs",
    payload,
  );

  return response.data;
}


export async function listEvaluationRuns(
  limit = 50,
  offset = 0,
): Promise<EvaluationRun[]> {
  const response = await api.get<EvaluationRun[]>(
    "/api/evaluation/runs",
    {
      params: {
        limit,
        offset,
      },
    },
  );

  return response.data;
}


export async function getEvaluationRun(
  runId: number,
): Promise<EvaluationRun> {
  const response = await api.get<EvaluationRun>(
    `/api/evaluation/runs/${runId}`,
  );

  return response.data;
}


export async function listPolicySnapshots(
  limit = 50,
): Promise<PolicySnapshot[]> {
  const response = await api.get<PolicySnapshot[]>(
    "/api/evaluation/snapshots",
    {
      params: { limit },
    },
  );

  return response.data;
}


export async function getSnapshotComparison(
  snapshotId: number,
): Promise<EvaluationComparison> {
  const response = await api.get<EvaluationComparison>(
    `/api/evaluation/snapshots/${snapshotId}/comparison`,
  );

  return response.data;
}
