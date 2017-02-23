# Setup
assignments = []

# Functions


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # First select boxes with 2 potential digits
    potential_twins = [box for box in values.keys() if len(values[box]) == 2]

    # Box pairs where a potential twin has another box in its neighbourhood
    # (peers[box1]) with the same set of values
    naked_twins = [[box1, box2] for box1 in potential_twins for box2 in peers[
        box1] if set(values[box1]) == set(values[box2])]

    # For each naked twins pair
    for i in range(len(naked_twins)):

        # Assign the twin boxes
        first_twin = naked_twins[i][0]
        second_twin = naked_twins[i][1]

        # Find the set of all peers (no duplicates!)
        first_peers = set(peers[first_twin])
        second_peers = set(peers[second_twin])

        # Bitwise and; what elements in the first set are also in the second
        # set?
        all_peers = first_peers & second_peers

        # Now that we have all the peers, we need to delete them from every
        # peer
        for peer in all_peers:

            # If it has more than two options
            if len(values[peer]) > 2:

                # Remove each digit that's in the twin box
                for twin_value in values[first_twin]:
                    values = assign_value(values, peer, values[
                                          peer].replace(twin_value, ''))
    return values


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s + t for s in A for t in B]


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    # Check the grid
    assert len(grid) == 81, "Input grid must be a string of length 81 (9x9)"

    # Make the dict again
    result = dict(zip(boxes, grid))

    # Now replace every . with 123456789
    for key, value in result.items():
        if value == '.':
            result[key] = '123456789'

    # Give it back
    return(result)


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)
    return


def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """

    # what do we know?
    solved = [square for square in values.keys() if len(values[square]) == 1]

    # what do we need to do know?
    unsolved = [square for square in values.keys() if len(values[square]) != 1]

    # for every square we don't know
    for square in unsolved:

        # get the square's entry
        entry = values[square]

        # get all the peer values we do know
        peer_values = [values[peer]
                       for peer in peers[square] if peer in solved]

        # update the local entry by removing those values
        for peer_value in peer_values:
            entry = entry.replace(peer_value, '')

        # update that square's entry
        # values[square] = entry
        values = assign_value(values, square, entry)

    return values


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    # for every neighbourhood
    for unit in unitlist:

        # for every digit
        for digit in '123456789':

            # Get every box in the unit if the current digit is in it's box
            # value
            dplaces = [box for box in unit if digit in values[box]]

            # If there is only one such box with a given digit
            if len(dplaces) == 1:

                # Set it to that value
                # values[dplaces[0]] = digit
                values = assign_value(values, dplaces[0], digit)

    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """

    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len(
            [box for box in values.keys() if len(values[box]) == 1])

        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)

        solved_values_after = len(
            [box for box in values.keys() if len(values[box]) == 1])

        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """
    Using depth-first search and propagation, try all possible values.
    """

    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)

    # Like a while loop; if False, stay False
    if values is False:
        return False

    # But if you have unique values for for every box after the last round
    # return True!
    if all(len(values[s]) == 1 for s in boxes):
        return values

    # If still false, find the smallest value and smallest box
    smallest_value, smallest_box = min([(values[box], box) for box in values if len(
        values[box]) > 1], key=lambda x: len(x[0]))

    # For each digit in that box
    for value in values[smallest_box]:

        # Create a new sub-puzzle by copying current value dictionary
        new_values = values.copy()

        # Assign the missing box the current value
        new_values[smallest_box] = value

        # Call this function again as an attempt to search
        attempt = search(new_values)

        # If attempt becomes true
        if attempt:

            # Return that attempt (which in turn returns values from the True
            # condition)
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

    # lol
    return search(grid_values(grid))

# Setup

# Convention
rows = 'ABCDEFGHI'
cols = '123456789'

# Boxes!
boxes = cross(rows, cols)

# Units
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI')
                for cs in ('123', '456', '789')]
upper_diag_units = [boxes[0::10]]
lower_diag_units = [boxes[8:-1:8]]

# Store it in a larger list
unitlist = row_units + column_units + \
    square_units + upper_diag_units + lower_diag_units

# Some useful lookup dictionaries
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
