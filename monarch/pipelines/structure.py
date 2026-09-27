from monarch.visual.scenes.board import board_from_lines


def build_structure(lines: list[str], total_s: float):
    return board_from_lines(lines, total_s)
