from utils import *
import re
import collections
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonals = [['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'], ['A9', 'B8', 'C7', 'D6', 'E5', 'F4', 'G3', 'H2', 'I1']]
unitlist = row_units + column_units + square_units + diagonals

unitlist = unitlist


# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)


def naked_twins(values):
    for unit in unitlist:
        valuesList = []
        for i in unit:
            valuesList.append(values[i])
        setOfDpulicates = set([x for x in valuesList if valuesList.count(x) > 1])
        if(len(setOfDpulicates) >= 1 ):
            for k in setOfDpulicates:

                if (len(k) == 2):
                    for l in unit:
                        if(values[l] == k):
                            pass
                        else:
                            for c in k:
                                values[l]= values[l].replace(c,"")
                            values[l] = values[l].strip()
    return values


def eliminate(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]

        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'').strip()
    return values


def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit

        break


    return values
def reduce_puzzle(values):
    NoProgress = False

    while not NoProgress:
        solved_values_Old = len([box for box in values.keys() if len(values[box]) == 1])

        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_New = len([box for box in values.keys() if len(values[box]) == 1])
        NoProgress = solved_values_Old == solved_values_New
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values




def search(values):
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    for value in values[s]:
        print(value)
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
