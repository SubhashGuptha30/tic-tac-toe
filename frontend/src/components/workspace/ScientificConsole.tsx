import {
  useEffect,
  useState,
} from "react";

import type {
  AnalyticsDataset,
  AnalyticsOverview,
  LearningUpdateDetail,
} from "../../types/analytics";
import type {
  AgentMetrics,
} from "../../types/game";
import type {
  WorkspaceTab,
} from "../../types/strategy";
import AnalyticsDashboard from "../analytics/AnalyticsDashboard";
import DecisionWorkspace from "../decisions/DecisionWorkspace";
import EpisodesWorkspace from "../episodes/EpisodesWorkspace";
import EvaluationLabWorkspace from "../evaluation/EvaluationLabWorkspace";
import QExplorerWorkspace from "../qexplorer/QExplorerWorkspace";
import StrategyWorkspace from "../strategy/StrategyWorkspace";
import TrainingArenaWorkspace from "../training/TrainingArenaWorkspace";
import WorkspaceTabs from "./WorkspaceTabs";


interface ScientificConsoleProps {
  overview: AnalyticsOverview | null;
  dataset: AnalyticsDataset;
  updates: LearningUpdateDetail[];
  metrics: AgentMetrics | null;
  isAgentThinking: boolean;
  loading: boolean;
  lastUpdated: Date | null;
  refreshSignal: number;
  liveDecisionEventId: number | null;
  onTrainingComplete: () => void | Promise<void>;
}


function ScientificConsole({
  overview,
  dataset,
  updates,
  metrics,
  isAgentThinking,
  loading,
  lastUpdated,
  refreshSignal,
  liveDecisionEventId,
  onTrainingComplete,
}: ScientificConsoleProps) {
  const [activeTab, setActiveTab] =
    useState<WorkspaceTab>("live");
  const [decisionPulse, setDecisionPulse] =
    useState(false);

  useEffect(() => {
    if (liveDecisionEventId === null) {
      return;
    }

    setDecisionPulse(true);

    const timerId =
      window.setTimeout(() => {
        setDecisionPulse(false);
      }, 2400);

    return () =>
      window.clearTimeout(timerId);
  }, [liveDecisionEventId]);

  return (
    <aside className="scientific-console">
      <div className="scientific-console-top">
        <div>
          <span>ADAPTIVE RL SYSTEM</span>
          <strong>Scientific Console</strong>
        </div>

        <div className="console-status">
          <span />
          ONLINE
        </div>
      </div>

      <WorkspaceTabs
        activeTab={activeTab}
        pulseTab={
          decisionPulse
            ? "decisions"
            : null
        }
        onChange={setActiveTab}
      />

      <div className="workspace-viewport">
        {activeTab === "live" && (
          <AnalyticsDashboard
            overview={overview}
            dataset={dataset}
            updates={updates}
            metrics={metrics}
            isAgentThinking={isAgentThinking}
            loading={loading}
            lastUpdated={lastUpdated}
          />
        )}

        {activeTab === "strategy" && (
          <StrategyWorkspace
            refreshSignal={refreshSignal}
          />
        )}

        {activeTab === "training" && (
          <TrainingArenaWorkspace
            refreshSignal={refreshSignal}
            onTrainingComplete={
              onTrainingComplete
            }
          />
        )}

        {activeTab === "evaluation" && (
          <EvaluationLabWorkspace
            refreshSignal={refreshSignal}
          />
        )}

        {activeTab === "q-explorer" && (
          <QExplorerWorkspace
            refreshSignal={refreshSignal}
          />
        )}

        {activeTab === "decisions" && (
          <DecisionWorkspace
            liveDecisionEventId={
              liveDecisionEventId
            }
            refreshSignal={refreshSignal}
          />
        )}

        {activeTab === "episodes" && (
          <EpisodesWorkspace
            refreshSignal={refreshSignal}
          />
        )}
      </div>
    </aside>
  );
}


export default ScientificConsole;
