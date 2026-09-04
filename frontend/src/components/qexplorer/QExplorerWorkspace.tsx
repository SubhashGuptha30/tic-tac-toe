import {
  Search,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  getQTableStates,
  inspectDecision,
  inspectQTableState,
} from "../../services/strategyApi";
import type {
  DecisionInspection,
  StateInspection,
  StateSummary,
} from "../../types/strategy";
import ActionValueList from "./ActionValueList";
import PolicyConfidencePanel from "./PolicyConfidencePanel";
import StateBoard from "./StateBoard";


interface QExplorerWorkspaceProps {
  refreshSignal: number;
}


function QExplorerWorkspace({
  refreshSignal,
}: QExplorerWorkspaceProps) {
  const [states, setStates] = useState<
    StateSummary[]
  >([]);
  const [
    selectedStateKey,
    setSelectedStateKey,
  ] = useState<string | null>(null);
  const [inspection, setInspection] =
    useState<StateInspection | null>(null);
  const [decision, setDecision] =
    useState<DecisionInspection | null>(null);
  const [
    selectedAction,
    setSelectedAction,
  ] = useState<number | null>(null);
  const [search, setSearch] =
    useState("");
  const [manualState, setManualState] =
    useState("");
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

        const nextStates =
          await getQTableStates(200, 0);

        setStates(nextStates);

        const targetState =
          selectedStateKey ??
          nextStates[0]?.state_key;

        if (targetState) {
          await loadState(targetState);
        } else {
          setInspection(null);
          setDecision(null);
          setSelectedAction(null);
        }
      } catch {
        setError(
          "Q-table states could not be loaded.",
        );
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [refreshSignal]);

  async function loadState(
    stateKey: string,
  ) {
    try {
      setError(null);

      const [
        stateData,
        decisionData,
      ] = await Promise.all([
        inspectQTableState(stateKey),
        inspectDecision(stateKey),
      ]);

      setInspection(stateData);
      setDecision(decisionData);
      setSelectedStateKey(stateKey);
      setSelectedAction(
        stateData.policy_confidence.best_action,
      );
    } catch {
      setError(
        "State inspection failed. Use a valid 9-cell state containing only 0, 1, and 2.",
      );
    }
  }

  function handleManualInspect() {
    const value = manualState.trim();

    if (!/^[012]{9}$/.test(value)) {
      setError(
        "State key must contain exactly 9 digits using only 0, 1, and 2.",
      );
      return;
    }

    void loadState(value);
  }

  const query = search.trim();
  const filteredStates = query
    ? states.filter((state) =>
        state.state_key.includes(query),
      )
    : states;

  if (loading && states.length === 0) {
    return (
      <div className="workspace-status">
        <span className="workspace-spinner" />
        Loading persistent Q-space...
      </div>
    );
  }

  return (
    <div className="q-explorer-workspace">
      <header className="workspace-hero">
        <div>
          <span className="workspace-eyebrow">
            TABULAR POLICY
          </span>
          <h2>Q-Table Explorer</h2>
          <p>
            Reconstruct learned states and inspect
            legal action values, rankings,
            tactical evidence, and policy
            separation.
          </p>
        </div>
      </header>

      <section className="manual-state-inspector">
        <input
          value={manualState}
          onChange={(event) =>
            setManualState(
              event.target.value,
            )
          }
          maxLength={9}
          placeholder="e.g. 102010000"
          aria-label="State key"
        />

        <button
          type="button"
          onClick={handleManualInspect}
        >
          <Search size={13} />
          Inspect
        </button>
      </section>

      {error && (
        <div className="workspace-error">
          {error}
        </div>
      )}

      <section className="state-browser">
        <div className="state-browser-sidebar">
          <div className="state-search">
            <Search size={12} />
            <input
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value,
                )
              }
              placeholder="Filter states..."
            />
          </div>

          <div className="state-summary-list">
            {filteredStates.slice(0, 100).map(
              (state) => (
                <button
                  type="button"
                  key={state.state_key}
                  className={
                    selectedStateKey ===
                    state.state_key
                      ? "state-summary-row selected"
                      : "state-summary-row"
                  }
                  onClick={() =>
                    void loadState(
                      state.state_key,
                    )
                  }
                >
                  <code>{state.state_key}</code>
                  <span>
                    Q {state.best_q.toFixed(3)}
                  </span>
                  <small>
                    {state.visit_updates} updates
                  </small>
                </button>
              ),
            )}
          </div>
        </div>

        <div className="state-inspection-area">
          {inspection ? (
            <>
              <div className="state-inspection-header">
                <div>
                  <span>ACTIVE STATE</span>
                  <code>
                    {inspection.state_key}
                  </code>
                </div>

                <span>
                  {inspection.q_rows_found} persisted
                  rows
                </span>
              </div>

              <StateBoard
                board={inspection.board}
                actionValues={
                  inspection.action_values
                }
                selectedAction={selectedAction}
                onActionSelect={setSelectedAction}
              />

              <ActionValueList
                actions={inspection.action_values}
                selectedAction={selectedAction}
                onSelect={setSelectedAction}
              />

              <PolicyConfidencePanel
                confidence={
                  inspection.policy_confidence
                }
                decision={decision}
              />
            </>
          ) : (
            <div className="workspace-empty">
              Select a stored state.
            </div>
          )}
        </div>
      </section>
    </div>
  );
}


export default QExplorerWorkspace;
