import {
  Activity,
  BrainCircuit,
  ChartNoAxesCombined,
  FlaskConical,
  SlidersHorizontal,
} from "lucide-react";

import ExperimentControls from "./ExperimentControls";
import LearningInspector from "./LearningInspector";
import QValueHeatmap from "./QValueHeatmap";
import type {
  AgentMetrics,
  AgentParameterUpdate,
  DecisionData,
  GameState,
  LearningUpdateData,
} from "../../types/game";


interface SciencePanelProps {
  game: GameState;
  metrics: AgentMetrics | null;
  decision: DecisionData | null;
  learningUpdate: LearningUpdateData | null;
  isAgentThinking: boolean;
  onSaveParameters: (
    parameters: AgentParameterUpdate
  ) => Promise<void>;
  onResetBrain: () => Promise<void>;
}


function SciencePanel({
  game,
  metrics,
  decision,
  learningUpdate,
  isAgentThinking,
  onSaveParameters,
  onResetBrain,
}: SciencePanelProps) {
  return (
    <aside className="science-panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">
            LIVE RL INSTRUMENTATION
          </span>
          <h2>Agent Cognition</h2>
        </div>

        <BrainCircuit size={23} />
      </div>

      <section className="science-card">
        <div className="science-card-title">
          <Activity size={16} />
          POLICY DECISION
        </div>

        {decision ? (
          <div className="decision-summary">
            <div
              className={[
                "decision-mode",
                decision.decision_mode,
              ].join(" ")}
            >
              {decision.decision_mode.toUpperCase()}
            </div>

            <div className="metric-list">
              <Metric
                label="Epsilon threshold"
                value={decision.epsilon.toFixed(4)}
              />
              <Metric
                label="Random sample"
                value={decision.random_sample.toFixed(4)}
              />
              <Metric
                label="Selected action"
                value={`A${decision.action + 1}`}
              />
            </div>
          </div>
        ) : (
          <div className="empty-science-state">
            Waiting for first decision...
          </div>
        )}

        {isAgentThinking && (
          <div className="thinking-strip">
            Evaluating epsilon-greedy policy...
          </div>
        )}
      </section>

      <section className="science-card">
        <div className="science-card-title">
          <BrainCircuit size={16} />
          ACTION-VALUE MATRIX
        </div>

        <QValueHeatmap decision={decision} />
      </section>

      <section className="science-card">
        <div className="science-card-title">
          <ChartNoAxesCombined size={16} />
          LATEST Q-UPDATE
        </div>

        <LearningInspector update={learningUpdate} />
      </section>

      <section className="science-card">
        <div className="science-card-title">
          <FlaskConical size={16} />
          AGENT METRICS
        </div>

        <div className="metric-list">
          <Metric
            label="Episode"
            value={String(game.stats.episodes + 1)}
          />
          <Metric
            label="Known states"
            value={String(metrics?.states_known ?? 0)}
          />
          <Metric
            label="Q-updates"
            value={String(metrics?.total_updates ?? 0)}
          />
          <Metric
            label="Exploration moves"
            value={String(metrics?.exploration_moves ?? 0)}
          />
          <Metric
            label="Exploitation moves"
            value={String(metrics?.exploitation_moves ?? 0)}
          />
          <Metric
            label="Current epsilon"
            value={metrics?.epsilon.toFixed(4) ?? "-"}
          />
        </div>
      </section>

      <section className="science-card">
        <div className="science-card-title">
          <SlidersHorizontal size={16} />
          EXPERIMENT CONTROLS
        </div>

        <ExperimentControls
          metrics={metrics}
          onSave={onSaveParameters}
          onResetBrain={onResetBrain}
        />
      </section>
    </aside>
  );
}


interface MetricProps {
  label: string;
  value: string;
}


function Metric({ label, value }: MetricProps) {
  return (
    <div className="metric-row">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}


export default SciencePanel;
