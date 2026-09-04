import {
  BrainCircuit,
  CheckCircle2,
  Dices,
  Grid3X3,
  MoveRight,
  Table2,
} from "lucide-react";

import type {
  LucideIcon,
} from "lucide-react";
import type {
  DecisionPipelineStage,
} from "../../types/decision";


interface DecisionPipelineProps {
  activeStage: DecisionPipelineStage;
}


interface PipelineItem {
  id: DecisionPipelineStage;
  label: string;
  shortLabel: string;
  icon: LucideIcon;
}


const stages: PipelineItem[] = [
  {
    id: "state",
    label: "State Capture",
    shortLabel: "STATE",
    icon: Grid3X3,
  },
  {
    id: "q-values",
    label: "Q Lookup",
    shortLabel: "Q LOOKUP",
    icon: Table2,
  },
  {
    id: "epsilon-gate",
    label: "Epsilon Gate",
    shortLabel: "EPS GATE",
    icon: Dices,
  },
  {
    id: "policy",
    label: "Policy Mode",
    shortLabel: "POLICY",
    icon: BrainCircuit,
  },
  {
    id: "selection",
    label: "Move Selection",
    shortLabel: "MOVE",
    icon: CheckCircle2,
  },
];


function DecisionPipeline({
  activeStage,
}: DecisionPipelineProps) {
  const activeIndex =
    stages.findIndex(
      (stage) =>
        stage.id === activeStage,
    );

  return (
    <section className="decision-pipeline">
      {stages.map((stage, index) => {
        const Icon = stage.icon;
        const isActive =
          stage.id === activeStage;
        const isComplete =
          index < activeIndex;

        return (
          <div
            className="pipeline-fragment"
            key={stage.id}
          >
            <div
              className={[
                "pipeline-stage",
                isActive ? "active" : "",
                isComplete ? "complete" : "",
              ]
                .filter(Boolean)
                .join(" ")}
              title={stage.label}
            >
              <div className="pipeline-icon">
                <Icon size={12} />
              </div>

              <span>{stage.shortLabel}</span>
            </div>

            {index < stages.length - 1 && (
              <MoveRight
                className={
                  isComplete
                    ? "pipeline-arrow complete"
                    : "pipeline-arrow"
                }
                size={11}
              />
            )}
          </div>
        );
      })}
    </section>
  );
}


export default DecisionPipeline;
