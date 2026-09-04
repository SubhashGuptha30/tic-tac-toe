import {
  useEffect,
  useState,
} from "react";

import {
  Save,
  Trash2,
} from "lucide-react";

import type {
  AgentMetrics,
  AgentParameterUpdate,
} from "../../types/game";


interface ExperimentControlsProps {
  metrics: AgentMetrics | null;
  onSave: (
    parameters: AgentParameterUpdate
  ) => Promise<void>;
  onResetBrain: () => Promise<void>;
}


function ExperimentControls({
  metrics,
  onSave,
  onResetBrain,
}: ExperimentControlsProps) {
  const [parameters, setParameters] =
    useState<AgentParameterUpdate>({
      alpha: 0.20,
      gamma: 0.95,
      epsilon: 0.90,
      epsilon_min: 0.05,
      epsilon_decay: 0.995,
    });
  const [saving, setSaving] = useState(false);
  const [confirmReset, setConfirmReset] =
    useState(false);

  useEffect(() => {
    if (!metrics) {
      return;
    }

    setParameters({
      alpha: metrics.alpha,
      gamma: metrics.gamma,
      epsilon: metrics.epsilon,
      epsilon_min: metrics.epsilon_min,
      epsilon_decay: metrics.epsilon_decay,
    });
  }, [metrics]);

  function updateField(
    field: keyof AgentParameterUpdate,
    value: number,
  ) {
    setParameters((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function handleSave() {
    try {
      setSaving(true);
      await onSave(parameters);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="experiment-controls">
      <ParameterInput
        label="Learning rate alpha"
        value={parameters.alpha}
        step={0.01}
        onChange={(value) =>
          updateField("alpha", value)
        }
      />

      <ParameterInput
        label="Discount gamma"
        value={parameters.gamma}
        step={0.01}
        onChange={(value) =>
          updateField("gamma", value)
        }
      />

      <ParameterInput
        label="Exploration epsilon"
        value={parameters.epsilon}
        step={0.01}
        onChange={(value) =>
          updateField("epsilon", value)
        }
      />

      <ParameterInput
        label="Minimum epsilon"
        value={parameters.epsilon_min}
        step={0.01}
        onChange={(value) =>
          updateField("epsilon_min", value)
        }
      />

      <ParameterInput
        label="Epsilon decay"
        value={parameters.epsilon_decay}
        step={0.001}
        onChange={(value) =>
          updateField("epsilon_decay", value)
        }
      />

      <button
        className="save-parameters-button"
        onClick={() => void handleSave()}
        disabled={saving}
      >
        <Save size={14} />
        {saving
          ? "Saving..."
          : "Apply Parameters"}
      </button>

      {!confirmReset ? (
        <button
          className="danger-outline-button"
          onClick={() => setConfirmReset(true)}
        >
          <Trash2 size={14} />
          Reset Agent Brain
        </button>
      ) : (
        <div className="reset-confirmation">
          <p>
            Permanently erase Q-values,
            episodes and learning history?
          </p>

          <div>
            <button
              className="confirm-delete-button"
              onClick={async () => {
                await onResetBrain();
                setConfirmReset(false);
              }}
            >
              Yes, erase brain
            </button>

            <button
              className="cancel-delete-button"
              onClick={() => setConfirmReset(false)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}


interface ParameterInputProps {
  label: string;
  value: number;
  step: number;
  onChange: (value: number) => void;
}


function ParameterInput({
  label,
  value,
  step,
  onChange,
}: ParameterInputProps) {
  return (
    <label className="parameter-row">
      <span>{label}</span>

      <input
        type="number"
        min="0"
        max="1"
        step={step}
        value={value}
        onChange={(event) =>
          onChange(
            Number(event.target.value)
          )
        }
      />
    </label>
  );
}


export default ExperimentControls;
