from app.strategy.board_analysis import (
    CORNER_ACTIONS,
    CENTER_ACTION,
    EDGE_ACTIONS,
    analyze_tactics,
)


def observe_selected_action(
    *,
    board: list[int],
    selected_action: int,
) -> list[str]:
    tactics = analyze_tactics(board)
    labels: list[str] = []

    if selected_action in tactics.immediate_wins:
        labels.append("IMMEDIATE_WIN")

    if selected_action in tactics.immediate_blocks:
        labels.append("IMMEDIATE_BLOCK")

    if selected_action in tactics.fork_creations:
        labels.append("FORK_CREATION")

    if selected_action in tactics.fork_preventions:
        labels.append("FORK_PREVENTION")

    if selected_action == CENTER_ACTION:
        labels.append("CENTER_POSITION")
    elif selected_action in CORNER_ACTIONS:
        labels.append("CORNER_POSITION")
    elif selected_action in EDGE_ACTIONS:
        labels.append("EDGE_POSITION")

    return labels
