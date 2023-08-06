
def solve(board):
    """Returns the board object filled in with the solution, or raises an
    exception if it was unable to solve the board.

    If there are multiple solutions for the board, one is selected in an
    undefined manner."""

    # Create a dict that contains the possibilities for each space. The keys are
    # xy integers for the space, the value is a string of possible symbols for
    # the space.
    candidates = dict([((i % BOARD_LENGTH, i // BOARD_LENGTH), '123456789') for i in range(80)])

    # Go through each of the givens on the board and remove them from the other
    # spaces.
    for i, given in enumerate(board):
        if given == EMPTY_SPACE:
            continue

        # Get the xy coordinates of this given.
        given_x, given_y = i % BOARD_LENGTH, i // BOARD_LENGTH

        # Remove the given from the candidates in the other spaces of this row.
        for x in range(BOARD_LENGTH):
            if given in candidates[x, given_y]:
                # Remove the given from these candidates.
                cand_str = candidates[x, given_y]
                candidates[x, given_y] = cand_str[:cand_str.find(given)] + cand_str[cand_str.find(given)+1:]

        # Remove the given from the candidates in the other spaces of this column.
        for y in range(BOARD_LENGTH):
            if given in candidates[given_x, y]:
                # Remove the given from these candidates.
                cand_str = candidates[given_x, y]
                candidates[given_x, y] = cand_str[:cand_str.find(given)] + cand_str[cand_str.find(given)+1:]

        # Remove the given from the candidates in the other spaces of this box.
        boxx, boxy = board.get_box_of(given_x, given_y)
        for x in range(boxx * BOARD_LENGTH_SQRT, boxx * BOARD_LENGTH_SQRT + BOARD_LENGTH_SQRT):
            for y in range(boxy * BOARD_LENGTH_SQRT, boxy * BOARD_LENGTH_SQRT + BOARD_LENGTH_SQRT):
                if x == given_x and y == given_y:
                    continue # don't remove from the given's candidates (we just want to remove it from the other spaces in this box)
                if given in candidates[x, y]:
                    # Remove the given from these candidates.
                    candidates[x, y] = cand_str[:cand_str.find(given)] + cand_str[cand_str.find(given)+1:]
