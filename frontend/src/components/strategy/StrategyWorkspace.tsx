import {
  GitFork,
  ShieldCheck,
  Swords,
  Trophy,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  getStrategyEvidence,
  getStrategyOverview,
} from "../../services/strategyApi";
import type {
  StrategyEvidenceItem,
  StrategyKey,
  StrategyOverview,
} from "../../types/strategy";
import PolicyHealthPanel from "./PolicyHealthPanel";
import PositionPreferencePanel from "./PositionPreferencePanel";
import StrategyEvidenceCard from "./StrategyEvidenceCard";


interface StrategyWorkspaceProps {
  refreshSignal: number;
}


function StrategyWorkspace({
  refreshSignal,
}: StrategyWorkspaceProps) {
  const [overview, setOverview] =
    useState<StrategyOverview | null>(null);
  const [
    selectedStrategy,
    setSelectedStrategy,
  ] = useState<StrategyKey>(
    "immediate_win",
  );
  const [evidence, setEvidence] =
    useState<StrategyEvidenceItem[]>([]);
  const [loading, setLoading] =
    useState(true);
  const [error, setError] = useState<
    string | null
  >(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError(null);

        const [
          nextOverview,
          nextEvidence,
        ] = await Promise.all([
          getStrategyOverview(),
          getStrategyEvidence(
            selectedStrategy,
            50,
          ),
        ]);

        setOverview(nextOverview);
        setEvidence(nextEvidence);
      } catch {
        setError(
          "Strategy intelligence could not be loaded.",
        );
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [
    selectedStrategy,
    refreshSignal,
  ]);

  if (loading && overview === null) {
    return (
      <div className="workspace-status">
        <span className="workspace-spinner" />
        Analyzing learned policy...
      </div>
    );
  }

  if (error && overview === null) {
    return (
      <div className="workspace-error">
        {error}
      </div>
    );
  }

  if (!overview) {
    return null;
  }

  const strategyCards = [
    {
      key: "immediate_win" as const,
      metric: overview.immediate_win,
      icon: Trophy,
    },
    {
      key: "immediate_block" as const,
      metric: overview.immediate_block,
      icon: ShieldCheck,
    },
    {
      key: "fork_creation" as const,
      metric: overview.fork_creation,
      icon: GitFork,
    },
    {
      key: "fork_prevention" as const,
      metric: overview.fork_prevention,
      icon: Swords,
    },
  ];

  return (
    <div className="strategy-workspace">
      <header className="workspace-hero">
        <div>
          <span className="workspace-eyebrow">
            EMERGENT BEHAVIOR
          </span>
          <h2>Strategy Intelligence</h2>
          <p>
            Observed alignment between the learned
            greedy policy and recognizable
            Tic-Tac-Toe tactics.
          </p>
        </div>

        <span className="observer-badge">
          OBSERVER ONLY
        </span>
      </header>

      <PolicyHealthPanel overview={overview} />

      <section className="strategy-evidence-section">
        <div className="workspace-section-header">
          <div>
            <span className="workspace-eyebrow">
              TACTICAL ALIGNMENT
            </span>
            <h3>Strategy Evidence</h3>
          </div>
        </div>

        <div className="strategy-evidence-grid">
          {strategyCards.map((item) => (
            <StrategyEvidenceCard
              key={item.key}
              metric={item.metric}
              icon={item.icon}
              selected={
                selectedStrategy === item.key
              }
              onSelect={() =>
                setSelectedStrategy(item.key)
              }
            />
          ))}
        </div>
      </section>

      <EvidenceInspector
        strategy={selectedStrategy}
        evidence={evidence}
      />

      <PositionPreferencePanel
        center={overview.center_preference}
        corner={overview.corner_preference}
        edge={overview.edge_preference}
      />

      <section className="scientific-caution">
        <strong>Interpretation boundary</strong>
        <p>
          These values measure policy alignment on
          observed stored states. They do not prove
          symbolic understanding or optimal play
          across every reachable state.
        </p>
      </section>
    </div>
  );
}


interface EvidenceInspectorProps {
  strategy: StrategyKey;
  evidence: StrategyEvidenceItem[];
}


function EvidenceInspector({
  strategy,
  evidence,
}: EvidenceInspectorProps) {
  return (
    <section className="evidence-inspector">
      <div className="workspace-section-header">
        <div>
          <span className="workspace-eyebrow">
            STATE EVIDENCE
          </span>
          <h3>
            {formatStrategyName(strategy)}
          </h3>
        </div>

        <span className="result-count">
          {evidence.length} states
        </span>
      </div>

      <div className="evidence-state-list">
        {evidence.length === 0 ? (
          <div className="workspace-empty">
            No observed opportunities for this
            strategy yet.
          </div>
        ) : (
          evidence.slice(0, 12).map((item) => (
            <article
              className="evidence-state-row"
              key={`${item.strategy}-${item.state_key}`}
            >
              <code>{item.state_key}</code>

              <div className="evidence-actions">
                <span>
                  opportunity [
                  {item.opportunity_actions.join(", ")}
                  ]
                </span>
                <span>
                  greedy [{item.greedy_actions.join(", ")}
                  ]
                </span>
              </div>

              <div className="evidence-score">
                <strong>
                  {(
                    item.alignment_score * 100
                  ).toFixed(0)}
                  %
                </strong>
                <small>
                  gap {item.action_gap.toFixed(3)}
                </small>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}


function formatStrategyName(
  strategy: StrategyKey,
) {
  return strategy
    .split("_")
    .map(
      (word) =>
        word.charAt(0).toUpperCase() +
        word.slice(1),
    )
    .join(" ");
}


export default StrategyWorkspace;
