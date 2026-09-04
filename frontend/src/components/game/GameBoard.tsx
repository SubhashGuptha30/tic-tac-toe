import { motion } from "framer-motion";

import type { GameState } from "../../types/game";


interface GameBoardProps {
  game: GameState;
  disabled: boolean;
  onCellClick: (index: number) => void;
}


function GameBoard({
  game,
  disabled,
  onCellClick,
}: GameBoardProps) {
  const winningCells = new Set(game.winning_line ?? []);

  return (
    <div className="game-board">
      {game.board.map((cell, index) => {
        const isLegal = game.legal_actions.includes(index);
        const canClick =
          !disabled &&
          !game.game_over &&
          game.current_player === "X" &&
          isLegal;
        const isWinning = winningCells.has(index);

        return (
          <motion.button
            key={index}
            className={[
              "game-cell",
              cell === "X" ? "human-cell" : "",
              cell === "O" ? "agent-cell" : "",
              isWinning ? "winning-cell" : "",
            ].join(" ")}
            onClick={() => onCellClick(index)}
            disabled={!canClick}
            whileHover={canClick ? { scale: 1.025 } : undefined}
            whileTap={canClick ? { scale: 0.96 } : undefined}
          >
            {cell && (
              <motion.span
                initial={{
                  scale: 0.4,
                  opacity: 0,
                }}
                animate={{
                  scale: 1,
                  opacity: 1,
                }}
                transition={{
                  type: "spring",
                  stiffness: 320,
                  damping: 18,
                }}
              >
                {cell}
              </motion.span>
            )}

            {!cell && canClick && (
              <span className="cell-index">{index + 1}</span>
            )}
          </motion.button>
        );
      })}
    </div>
  );
}


export default GameBoard;
