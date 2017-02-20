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


def naked_twins(sudoku_dict):
    """Eliminate values using the naked twins strategy.
    Args:
        sudoku_dict(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        The values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    for box in boxes:
        if len(sudoku_dict[box]) != 2:
            continue

        peer_pairs = [p for p in peers[box] if sudoku_dict[p] == sudoku_dict[box]]

        if len(peer_pairs) != 2:
            continue

        naked_twins = sudoku_dict[peer_pairs[0]]

        # Eliminate the naked twins as possibilities for their peers
        for peer in peers[box]:
            if sudoku_dict[peer] != naked_twins:
                sudoku_dict[peer] = sudoku_dict[peer].replace(naked_twins[0], '')
                sudoku_dict[peer] = sudoku_dict[peer].replace(naked_twins[1], '')
                assign_value(sudoku_dict, peer, sudoku_dict[peer])

    return sudoku_dict


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
    empty_mapper = (lambda t: t if t[1] != '.' else (t[0], '123456789'))
    values = dict(map(empty_mapper, zip(boxes, grid)))

    for box, value in values.items():
        assign_value(values, box, value)

    return values


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '') for c in cols))
        if r in 'CF':
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
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
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
    if reduced_values is False:
        return False

    least_values_box = None

    for box, box_values in reduced_values.items():

        if len(box_values) > 1:
            if least_values_box is None:
                least_values_box = box

            if len(box_values) < len(reduced_values[least_values_box]):
                least_values_box = box

    if least_values_box is None:
        return reduced_values

    for value in reduced_values[least_values_box]:
        op_values = reduced_values.copy()
        op_values[least_values_box] = value
        assign_value(op_values, least_values_box, value)

        op_search_result = search(op_values)

        if op_search_result:
            return op_search_result

    # Means that no answer was found in the loop attempts
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
rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

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
