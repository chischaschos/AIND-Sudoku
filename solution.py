"""
Solution and helper functions to solve sudokus
"""


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
        The values dictionary with the naked twins eliminated from peers.
    """
    # Go through all the units
    for unit in unitlist:
        # What if there were more than 1 pair?
        # For now find boxes with two values
        pairs = [box for box in unit if len(values[box]) == 2]

        # Make sure that the values are the same
        if len(pairs) == 2 and values[pairs[0]] == values[pairs[1]]:

            # Pick one pair
            pair = values[pairs[0]]

            for box in unit:
                # Skip solved values
                if len(values[box]) == 1:
                    continue

                # Remove pair from boxes as long as it is not itself
                if values[box] != pair:
                    values[box] = values[box].replace(pair[0], '')
                    values[box] = values[box].replace(pair[1], '')
                    assign_value(values, box, values[box])

    return values


def cross(a, b):
    "Cross product of elements in A and elements in B."
    return [s+t for s in a for t in b]


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value,
                then the value will be '123456789'.
    """
    # empty_mapper is a lambda that receives a tuple of length 2, if its
    # second element is a . then we fill it in with digits from 1-9
    empty_mapper = (lambda t: (t[0], '123456789') if t[1] == '.' else t)

    # apply our empty mapper to every box
    values = dict(map(empty_mapper, zip(boxes, grid)))

    # reflect or values updates for the visualizer
    for box, value in values.items():
        assign_value(values, box, value)

    return values


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for row in rows:
        print(''.join(values[row + col].center(width) + ('|' if col in '36' else '') for col in cols))
        if row in 'CF':
            print(line)


def eliminate(values):
    """
    Eliminates solved values from peer boxes
    Args:
        values(dict): The sudoku in dictionary form
    Returns:
        The sudoku in dictionary form with solved values eliminated from peer
        boxes
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit, '')
            assign_value(values, peer, values[peer])
    return values


def only_choice(values):
    """
    Solve values for units containing boxes with only once choice in a unit
    Args:
        values(dict): The sudoku in dictionary form
    Returns:
        The sudoku in dictionary form with only choice values solved
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
                assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice().

    If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same,
    return the sudoku.

    Args:
        A sudoku in dictionary form.
    Returns:
        The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # record solves values in order to detect improvements
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # apply our constraints#
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)

        # verify if it got solved
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])

        # determine if it got solved or got stalled#
        stalled = solved_values_before == solved_values_after

        # sanity check
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values


def search(values):
    """
    Using depth-first search and propagation, create a search tree and solve
    the sudoku.

    Args:
        A sudoku in dictionary form.
    Returns:
        The resulting sudoku in dictionary form.
    """
    reduced_values = reduce_puzzle(values)
    # return if reduction failed
    if reduced_values is False:
        return False

    least_values_box = None

    # pick the non solved box with the least amount of values
    for box, box_values in reduced_values.items():

        if len(box_values) > 1:
            if least_values_box is None:
                least_values_box = box

            if len(box_values) < len(reduced_values[least_values_box]):
                least_values_box = box

    # If non was found we have then already solved it
    if least_values_box is None:
        return reduced_values

    # Deep first search or box with at least two values from left to right
    # trying each value
    for value in reduced_values[least_values_box]:
        op_values = reduced_values.copy()
        op_values[least_values_box] = value
        assign_value(op_values, least_values_box, value)

        # attempt to solve sudoku for given value
        op_search_result = search(op_values)

        if op_search_result:
            return op_search_result

    # No solution was found for this sudoku
    return False


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no
        solution exists.
    """
    values = grid_values(grid)
    for box, value in values.items():
        assign_value(values, box, value)
    return search(values)


assignments = []

# bild boxes
rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)

# build units list
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, col) for col in cols]
square_units = [cross(rows, columns) for rows in ('ABC', 'DEF', 'GHI') for columns in ('123', '456', '789')]
left_diagonal_units = [[a + str(i) for i, a in enumerate(rows, 1)]]
right_diagonal_units = [[a + str(9-i) for i, a in enumerate(rows)]]
unitlist = row_units + column_units + square_units + left_diagonal_units + right_diagonal_units

# build dictionary box to units
units = dict((box, [u for u in unitlist if box in u]) for box in boxes)

# build dictionary box to peers
peers = dict((box, set(sum(units[box], []))-set([box])) for box in boxes)

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
