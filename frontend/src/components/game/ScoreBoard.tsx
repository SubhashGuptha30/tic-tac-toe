import { Bot, Equal, UserRound } from "lucide-react";

import type { GameStats } from "../../types/game";


interface ScoreBoardProps {
  stats: GameStats;
}


function ScoreBoard({ stats }: ScoreBoardProps) {
  return (
    <div className="score-grid">
      <article className="score-card human-score">
        <UserRound size={18} />

        <div>
          <span>Human Wins</span>
          <strong>{stats.human_wins}</strong>
        </div>
      </article>

      <article className="score-card agent-score">
        <Bot size={18} />

        <div>
          <span>Agent Wins</span>
          <strong>{stats.agent_wins}</strong>
        </div>
      </article>

      <article className="score-card draw-score">
        <Equal size={18} />

        <div>
          <span>Draws</span>
          <strong>{stats.draws}</strong>
        </div>
      </article>
    </div>
  );
}


export default ScoreBoard;
