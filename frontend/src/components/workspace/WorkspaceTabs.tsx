import {
  Activity,
  BrainCircuit,
  Database,
  Dumbbell,
  FlaskConical,
  History,
  Microscope,
} from "lucide-react";

import type {
  WorkspaceTab,
} from "../../types/strategy";


interface WorkspaceTabsProps {
  activeTab: WorkspaceTab;
  pulseTab?: WorkspaceTab | null;
  onChange: (
    tab: WorkspaceTab,
  ) => void;
}


const tabs = [
  {
    id: "live" as const,
    label: "LIVE LAB",
    icon: Activity,
  },
  {
    id: "training" as const,
    label: "TRAINING",
    icon: Dumbbell,
  },
  {
    id: "evaluation" as const,
    label: "EVALUATE",
    icon: FlaskConical,
  },
  {
    id: "strategy" as const,
    label: "STRATEGY",
    icon: BrainCircuit,
  },
  {
    id: "q-explorer" as const,
    label: "Q-EXPLORER",
    icon: Database,
  },
  {
    id: "decisions" as const,
    label: "DECISIONS",
    icon: Microscope,
  },
  {
    id: "episodes" as const,
    label: "EPISODES",
    icon: History,
  },
];


function WorkspaceTabs({
  activeTab,
  pulseTab = null,
  onChange,
}: WorkspaceTabsProps) {
  return (
    <nav
      className="workspace-tabs"
      aria-label="Scientific workspaces"
    >
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive =
          activeTab === tab.id;
        const isPulsing =
          pulseTab === tab.id && !isActive;

        return (
          <button
            key={tab.id}
            type="button"
            className={[
              "workspace-tab",
              isActive ? "active" : "",
              isPulsing ? "pulse" : "",
            ]
              .filter(Boolean)
              .join(" ")}
            onClick={() =>
              onChange(tab.id)
            }
          >
            <Icon size={13} />
            <span>{tab.label}</span>
          </button>
        );
      })}
    </nav>
  );
}


export default WorkspaceTabs;
