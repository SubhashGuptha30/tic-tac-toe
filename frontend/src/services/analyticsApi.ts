import api from "./api";

import type {
  AnalyticsDataset,
  AnalyticsOverview,
  LearningUpdateDetail,
} from "../types/analytics";


export async function getAnalyticsOverview():
Promise<AnalyticsOverview> {
  const response =
    await api.get<AnalyticsOverview>(
      "/api/analytics/overview",
    );

  return response.data;
}


export async function getAnalyticsDataset(
  rollingWindow = 10,
): Promise<AnalyticsDataset> {
  const response =
    await api.get<AnalyticsDataset>(
      "/api/analytics/dataset",
      {
        params: {
          rolling_window: rollingWindow,
        },
      },
    );

  return response.data;
}


export async function getRecentLearningUpdates(
  limit = 20,
): Promise<LearningUpdateDetail[]> {
  const response =
    await api.get<LearningUpdateDetail[]>(
      "/api/analytics/learning-updates",
      {
        params: {
          limit,
        },
      },
    );

  return response.data;
}
