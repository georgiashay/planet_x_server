from planetx_game.utilities import *
from planetx_game.board import Board

def compare_unordered_list_of_lists(result, expected):
    result_tuples = sorted([tuple([item if item is not None else "" for item in item_list]) for item_list in result])
    expected_tuples = sorted([tuple([item if item is not None else "" for item in item_list]) for item_list in expected])
    assert result_tuples == expected_tuples

def compare_unordered_list_of_boards(result, expected):
    result_sorted = sorted(result, key=lambda b: tuple([obj if obj is not None else "" for obj in b.objects]))
    expected_sorted = sorted(expected, key=lambda b: tuple([obj if obj is not None else "" for obj in b.objects]))
    assert result_sorted == expected_sorted
    
def rotate(lists):
    n = len(lists[0])
    new_lists = []
    for i in range(n):
        for l in lists:
            new_lists.append(l[n-i:n] + l[:n-i])
    return new_lists
        

# permutations_multi
# inputs:
#     counts: an object mapping values to counts
# output:
#     a generator for all unique lists containing 
#     counts[val] val's for each val in counts

# Testing strategy:
#     - partition: # keys in counts: 0, 1, 2, >2
#     - partition: maximum count: 1, 2, > 2

# keys = 0
def test_permutations_multi_empty():
    compare_unordered_list_of_lists(list(permutations_multi({})), [[]])
    
# keys = 1, max = 1
def test_permutations_multi_single():
    compare_unordered_list_of_lists(list(permutations_multi({"A": 1})), [["A"]])
    
# keys = 1, max = 2
def test_permutations_multi_monopair():
    compare_unordered_list_of_lists(list(permutations_multi({"A": 2})), [["A", "A"]])
    
# keys = 1, max > 2
def test_permutations_multi_repeat_one():
    compare_unordered_list_of_lists(list(permutations_multi({"A": 4})), [["A", "A", "A", "A"]])

# keys = 2, max = 1
def test_permutations_multi_one_of_each():
    compare_unordered_list_of_lists(list(permutations_multi({"A": 1, "B": 1})), [["A", "B"], ["B", "A"]])

# keys = 2, max = 2
def test_permutations_multi_one_and_two():
    compare_unordered_list_of_lists(list(permutations_multi({"A": 2, "B": 1})),
                                    [["A", "A", "B"], ["A", "B", "A"], ["B", "A", "A"]])

# keys = 2, max > 2
def test_permutations_multi_two_many():
    compare_unordered_list_of_lists(list(permutations_multi({"A": 2, "B": 4})), [
        ["A", "A", "B", "B", "B", "B"],
        ["A", "B", "A", "B", "B", "B"],
        ["A", "B", "B", "A", "B", "B"],
        ["A", "B", "B", "B", "A", "B"],
        ["A", "B", "B", "B", "B", "A"],
        ["B", "A", "A", "B", "B", "B"],
        ["B", "A", "B", "A", "B", "B"],
        ["B", "A", "B", "B", "A", "B"],
        ["B", "A", "B", "B", "B", "A"],
        ["B", "B", "A", "A", "B", "B"],
        ["B", "B", "A", "B", "A", "B"],
        ["B", "B", "A", "B", "B", "A"],
        ["B", "B", "B", "A", "A", "B"],
        ["B", "B", "B", "A", "B", "A"],
        ["B", "B", "B", "B", "A", "A"]
    ])

# keys  > 2, max = 1
def test_permutations_multi_many_single():
    compare_unordered_list_of_lists(list(permutations_multi({"A": 1, "B": 1, "C": 1, "D": 1})), [
        ["A", "B", "C", "D"],
        ["A", "B", "D", "C"],
        ["A", "C", "B", "D"],
        ["A", "C", "D", "B"],
        ["A", "D", "B", "C"],
        ["A", "D", "C", "B"],
        ["B", "A", "C", "D"],
        ["B", "A", "D", "C"],
        ["B", "C", "A", "D"],
        ["B", "C", "D", "A"],
        ["B", "D", "A", "C"],
        ["B", "D", "C", "A"],
        ["C", "A", "B", "D"],
        ["C", "A", "D", "B"],
        ["C", "B", "A", "D"],
        ["C", "B", "D", "A"],
        ["C", "D", "A", "B"],
        ["C", "D", "B", "A"],
        ["D", "A", "B", "C"],
        ["D", "A", "C", "B"],
        ["D", "B", "A", "C"],
        ["D", "B", "C", "A"],
        ["D", "C", "A", "B"],
        ["D", "C", "B", "A"]
    ])

# keys > 2, max = 2
def test_permutations_multi_many_max_two():
     compare_unordered_list_of_lists(list(permutations_multi({"A": 2, "B": 1, "C": 2})), [
        ["A", "A", "B", "C", "C"],
        ["A", "A", "C", "B", "C"],
        ["A", "A", "C", "C", "B"],
        ["A", "B", "A", "C", "C"],
        ["A", "B", "C", "A", "C"],
        ["A", "B", "C", "C", "A"],
        ["A", "C", "A", "B", "C"],
        ["A", "C", "A", "C", "B"],
        ["A", "C", "B", "A", "C"],
        ["A", "C", "B", "C", "A"],
        ["A", "C", "C", "A", "B"],
        ["A", "C", "C", "B", "A"],
        ["B", "A", "A", "C", "C"],
        ["B", "A", "C", "A", "C"],
        ["B", "A", "C", "C", "A"],
        ["B", "C", "A", "A", "C"],
        ["B", "C", "A", "C", "A"],
        ["B", "C", "C", "A", "A"],
        ["C", "A", "A", "B", "C"],
        ["C", "A", "A", "C", "B"],
        ["C", "A", "B", "A", "C"],
        ["C", "A", "B", "C", "A"],
        ["C", "A", "C", "A", "B"],
        ["C", "A", "C", "B", "A"],
        ["C", "B", "A", "A", "C"],
        ["C", "B", "A", "C", "A"],
        ["C", "B", "C", "A", "A"],
        ["C", "C", "A", "A", "B"],
        ["C", "C", "A", "B", "A"],
        ["C", "C", "B", "A", "A"]
    ])

# keys > 2, max > 2
def test_permutations_multi_many_many():
    compare_unordered_list_of_lists(list(permutations_multi({"A": 1, "B": 3, "C": 1})), [
        ["A", "B", "B", "B", "C"],
        ["A", "B", "B", "C", "B"],
        ["A", "B", "C", "B", "B"],
        ["A", "C", "B", "B", "B"],
        ["B", "A", "B", "B", "C"],
        ["B", "A", "B", "C", "B"],
        ["B", "A", "C", "B", "B"],
        ["B", "B", "A", "B", "C"],
        ["B", "B", "A", "C", "B"],
        ["B", "B", "B", "A", "C"],
        ["B", "B", "B", "C", "A"],
        ["B", "B", "C", "A", "B"],
        ["B", "B", "C", "B", "A"],
        ["B", "C", "A", "B", "B"],
        ["B", "C", "B", "A", "B"],
        ["B", "C", "B", "B", "A"],
        ["C", "A", "B", "B", "B"],
        ["C", "B", "A", "B", "B"],
        ["C", "B", "B", "A", "B"],
        ["C", "B", "B", "B", "A"]
    ])
    
    
# fill_no_touch
# inputs:
#    - counts: Mapping of objects to the number of that object to add to a board
#    - board: Board to add objects to
# output:
#    - generator of all boards filling in the objects in counts where there are Nones, 
#      such that none of the objects in counts touch each other

# Testing strategy:
#    - partition: # keys in counts: 0, 1, 2, > 2
#    - partition: board valid, board not valid
#    - partition: board contains objects, board contains no objects
#    - partition: board contains objects in counts, board does not contain objects in counts
#    - partition: max count: 1, > 1
#    - partition: object in first position on board, object not in first position on board
#    - partition: object in last position on board, object not in last position on board

# keys = 0, board contains no objects
def test_fill_no_touch_empty():
    compare_unordered_list_of_boards(list(fill_no_touch({}, Board([None, None, None, None]))), 
                                     [Board([None, None, None, None])])
    
# keys = 0, board contains objects
def test_fill_no_touch_empty_existing():
    compare_unordered_list_of_boards(list(fill_no_touch({}, Board([None, "A", "B", None]))),
                                     [Board([None, "A", "B", None])])
    
# keys = 1, board contains no objects, max = 1
def test_fill_no_touch_one_on_empty():
    compare_unordered_list_of_boards(list(fill_no_touch({"A": 1}, Board([None, None, None]))), [
        Board(["A", None, None]),
        Board([None, "A", None]),
        Board([None, None, "A"])])
    
# keys = 1, board contains no objects, max > 1
def test_fill_no_touch_one_type_on_empty():
    compare_unordered_list_of_boards(list(fill_no_touch({"A": 3}, Board([None, None, None, None, None]))), [
        Board(["A", "A", "A", None, None]),
        Board(["A", "A", None, "A", None]),
        Board(["A", "A", None, None, "A"]),
        Board(["A", None, "A", "A", None]),
        Board(["A", None, "A", None, "A"]),
        Board(["A", None, None, "A", "A"]),
        Board([None, "A", "A", "A", None]),
        Board([None, "A", "A", None, "A"]),
        Board([None, "A", None, "A", "A"]),
        Board([None, None, "A", "A", "A"])])
    
# keys = 1, board contains objects in counts, max = 1
def test_fill_no_touch_one_on_existing():
    compare_unordered_list_of_boards(list(fill_no_touch({"A": 1}, Board([None, "A", None, None]))), [
        Board(["A", "A", None, None]),
        Board([None, "A", "A", None]),
        Board([None, "A", None, "A"])])
    
# keys = 1, board contains objects not in counts, max = 1
def test_fill_no_touch_one_on_others():
    compare_unordered_list_of_boards(list(fill_no_touch({"A": 1}, Board([None, "B", None, "C"]))), [
        Board(["A", "B", None, "C"]),
        Board([None, "B", "A", "C"])])
    
# keys = 1, board contains objects in counts, max > 1
def test_fill_no_touch_one_type_on_existing():
    compare_unordered_list_of_boards(list(fill_no_touch({"A": 2}, Board([None, None, "A", None, None]))), [
        Board(["A", "A", "A", None, None]),
        Board(["A", None, "A", "A", None]),
        Board(["A", None, "A", None, "A"]),
        Board([None, "A", "A", "A", None]),
        Board([None, "A", "A", None, "A"]),
        Board([None, None, "A", "A", "A"])])
    
# keys = 1, board contains objects not in counts, max > 1
def test_fill_no_touch_one_type_on_others():
    compare_unordered_list_of_boards(list(fill_no_touch({"A": 3}, Board([None, "B", None, None]))), [
        Board(["A", "B", "A", "A"])])

# keys = 2, board contains no objects, max = 1
def test_fill_no_touch_two_one_each_on_empty():
    compare_unordered_list_of_boards(list(fill_no_touch({"A": 1, "B": 1}, Board([None, None, None, None]))), [
        Board(["A", None, "B", None]),
        Board([None, "A", None, "B"]),
        Board(["B", None, "A", None]),
        Board([None, "B", None, "A"])])
    
# keys = 2, board contains objects not in counts, object in last position, max = 1
def test_fill_no_touch_two_one_each_on_others():
    compare_unordered_list_of_boards(list(fill_no_touch({"A": 1, "B": 1}, Board([None, "C", None, None, "D"]))), [
        Board(["A", "C", "B", None, "D"]),
        Board(["A", "C", None, "B", "D"]),
        Board(["B", "C", "A", None, "D"]),
        Board(["B", "C", None, "A", "D"])])
    
# keys = 2, board contains objects in counts, object in first position, max = 1
def test_fill_no_touch_two_one_each_on_existing():
    compare_unordered_list_of_boards(list(fill_no_touch({"A": 1, "B": 1}, Board(["A", "C", None, None, None, "D", None]))), [
        Board(["A", "C", "A", None, "B", "D", None]),
        Board(["A", "C", "B", None, "A", "D", None]),
        Board(["A", "C", "B", None, None, "D", "A"]),
        Board(["A", "C", None, "B", None, "D", "A"]),
        Board(["A", "C", None, None, "B", "D", "A"])])

# keys = 2, board contains no objects, max > 1
def test_fill_no_touch_two_many_on_empty():
    compare_unordered_list_of_boards(list(fill_no_touch({"A": 2, "B": 3}, Board([None]*8))), [
        Board(["A", "A", None, "B", "B", "B", None, None]),
        Board(["A", "A", None, "B", "B", None, "B", None]),
        Board(["A", "A", None, "B", None, "B", "B", None]),
        Board(["A", "A", None, None, "B", "B", "B", None]),
        Board(["A", None, "A", None, "B", "B", "B", None]),
        Board([None, "A", "A", None, "B", "B", "B", None]),
        Board([None, "A", "A", None, "B", "B", None, "B"]),
        Board([None, "A", "A", None, "B", None, "B", "B"]),
        Board([None, "A", "A", None, None, "B", "B", "B"]),
        Board([None, "A", None, "A", None, "B", "B", "B"]),
        Board([None, None, "A", "A", None, "B", "B", "B"]),
        Board(["B", None, "A", "A", None, "B", "B", None]),
        Board(["B", None, "A", "A", None, "B", None, "B"]),
        Board(["B", None, "A", "A", None, None, "B", "B"]),
        Board(["B", None, "A", None, "A", None, "B", "B"]),
        Board(["B", None, None, "A", "A", None, "B", "B"]),
        Board([None, "B", None, "A", "A", None, "B", "B"]),
        Board(["B", "B", None, "A", "A", None, "B", None]),
        Board(["B", "B", None, "A", "A", None, None, "B"]),
        Board(["B", "B", None, "A", None, "A", None, "B"]),
        Board(["B", "B", None, None, "A", "A", None, "B"]),
        Board(["B", None, "B", None, "A", "A", None, "B"]),
        Board([None, "B", "B", None, "A", "A", None, "B"]),
        Board(["B", "B", "B", None, "A", "A", None, None]),
        Board(["B", "B", "B", None, "A", None, "A", None]),
        Board(["B", "B", "B", None, None, "A", "A", None]),
        Board(["B", "B", None, "B", None, "A", "A", None]),
        Board(["B", None, "B", "B", None, "A", "A", None]),
        Board([None, "B", "B", "B", None, "A", "A", None]),
        Board([None, "B", "B", "B", None, "A", None, "A"]),
        Board([None, "B", "B", "B", None, None, "A", "A"]),
        Board([None, "B", "B", None, "B", None, "A", "A"]),
        Board([None, "B", None, "B", "B", None, "A", "A"]),
        Board([None, None, "B", "B", "B", None, "A", "A"]),
        Board(["A", None, "B", "B", "B", None, "A", None]),
        Board(["A", None, "B", "B", "B", None, None, "A"]),
        Board(["A", None, "B", "B", None, "B", None, "A"]),
        Board(["A", None, "B", None, "B", "B", None, "A"]),
        Board(["A", None, None, "B", "B", "B", None, "A"]),
        Board([None, "A", None, "B", "B", "B", None, "A"])])
    
# keys = 2, board contains objects not in counts, max > 1, object in first & last position
def test_fill_no_touch_two_many_on_others():
    compare_unordered_list_of_boards(list(fill_no_touch({"A": 1, "B": 2}, 
                                                        Board(["C", "C", None, None, None, "D", "C", None, "E"]))), [
        Board(["C", "C", "A", None, "B", "D", "C", "B", "E"]),
        Board(["C", "C", "B", None, "A", "D", "C", "B", "E"]),
        Board(["C", "C", "B", "B", None, "D", "C", "A", "E"]),
        Board(["C", "C", None, "B", "B", "D", "C", "A", "E"]),
        Board(["C", "C", "B", None, "B", "D", "C", "A", "E"])])
    
# keys = 2, board contains objects in counts, max > 1
def test_fill_no_touch_two_many_on_existing():
    compare_unordered_list_of_boards(list(fill_no_touch({"A": 2, "B": 2},
                                                        Board([None, "A", "A", "C", None, None, "C", "B", None, "D", None]))), [
        Board(["A", "A", "A", "C", "B", "B", "C", "B", None, "D", "A"]),
        Board(["A", "A", "A", "C", "B", None, "C", "B", "B", "D", "A"]),
        Board(["A", "A", "A", "C", None, "B", "C", "B", "B", "D", "A"]),
        Board([None, "A", "A", "C", "A", "A", "C", "B", "B", "D", "B"])])
    
# keys > 2, board contains no objects, max = 1
def test_fill_no_touch_three_one_each_on_empty():
    compare_unordered_list_of_boards(
        list(fill_no_touch({"A": 1, "B": 1, "C": 1},
                            Board([None, None, None, None, None, None]))), [
            Board(["A", None, "B", None, "C", None]),
            Board([None, "A", None, "B", None, "C"]),
            Board(["A", None, "C", None, "B", None]),
            Board([None, "A", None, "C", None, "B"]),
            Board(["B", None, "A", None, "C", None]),
            Board([None, "B", None, "A", None, "C"]),
            Board(["B", None, "C", None, "A", None]),
            Board([None, "B", None, "C", None, "A"]),
            Board(["C", None, "A", None, "B", None]),
            Board([None, "C", None, "A", None, "B"]),
            Board(["C", None, "B", None, "A", None]),
            Board([None, "C", None, "B", None, "A"])])
    
# keys > 2, board contains objects not in counts, max = 1
def test_fill_no_touch_three_one_each_on_others():
    compare_unordered_list_of_boards(
        list(fill_no_touch({"A": 1, "B": 1, "C": 1},
                           Board([None, "D", None, "E", "F", None, None]))), [
            Board(["A", "D", "B", "E", "F", "C", None]),
            Board(["A", "D", "C", "E", "F", "B", None]),
            Board(["B", "D", "A", "E", "F", "C", None]),
            Board(["B", "D", "C", "E", "F", "A", None]),
            Board(["C", "D", "A", "E", "F", "B", None]),
            Board(["C", "D", "B", "E", "F", "A", None])])

# keys > 2, board contains objects in counts, max = 1
def test_fill_no_touch_four_one_each_on_existing():
    compare_unordered_list_of_boards(
        list(fill_no_touch({"A": 1, "B": 1, "C": 1, "D": 1},
                           Board([None, "C", None, None, "A", "E", None, None, "F"]))), [])

# keys > 2, board contains no objects, max > 1
def test_fill_no_touch_three_many_on_empty():
    compare_unordered_list_of_boards(
        list(fill_no_touch({"A": 1, "B": 2, "C": 2},
                           Board([None, None, None, None, None, None, None, None]))), [
            Board(["A", None, "B", "B", None, "C", "C", None]),
            Board([None, "A", None, "B", "B", None, "C", "C"]),
            Board(["A", None, "C", "C", None, "B", "B", None]),
            Board([None, "A", None, "C", "C", None, "B", "B"]),
            Board(["B", "B", None, "A", None, "C", "C", None]),
            Board([None, "B", "B", None, "A", None, "C", "C"]),
            Board(["B", None, "A", None, "C", "C", None, "B"]),
            Board(["B", "B", None, "C", "C", None, "A", None]),
            Board([None, "B", "B", None, "C", "C", None, "A"]),
            Board(["B", None, "C", "C", None, "A", None, "B"]),
            Board(["C", "C", None, "A", None, "B", "B", None]),
            Board([None, "C", "C", None, "A", None, "B", "B"]),
            Board(["C", None, "A", None, "B", "B", None, "C"]),
            Board(["C", "C", None, "B", "B", None, "A", None]),
            Board([None, "C", "C", None, "B", "B", None, "A"]),
            Board(["C", None, "B", "B", None, "A", None, "C"])])

# keys > 2, board contains objects not in counts, max > 1
def test_fill_no_touch_three_many_on_others():
    compare_unordered_list_of_boards(
        list(fill_no_touch({"A": 2, "B": 1, "C": 1},
                           Board([None, None, "D", None, None, "E", None, "F"]))), [
            Board(["A", "A", "D", "B", None, "E", "C", "F"]),
            Board(["A", "A", "D", None, "B", "E", "C", "F"]),
            Board(["A", "A", "D", "C", None, "E", "B", "F"]),
            Board(["A", "A", "D", None, "C", "E", "B", "F"]),
            Board(["B", None, "D", "A", "A", "E", "C", "F"]),
            Board([None, "B", "D", "A", "A", "E", "C", "F"]),
            Board(["C", None, "D", "A", "A", "E", "B", "F"]),
            Board([None, "C", "D", "A", "A", "E", "B", "F"])])
                           
# keys > 2, board contains objects in counts, max > 1
def test_fill_no_touch_three_many_on_existing():
    compare_unordered_list_of_boards(
        list(fill_no_touch({"A": 1, "B": 1, "C": 2},
                           Board(["A", "A", "A", None, None, "B", None, None, "D", "C", None, None, None]))), [
            Board(["A", "A", "A", "A", None, "B", "B", None, "D", "C", "C", "C", None]),
            Board(["A", "A", "A", None, "B", "B", None, "C", "D", "C", "C", None, "A"]),
            Board(["A", "A", "A", "A", None, "B", None, "B", "D", "C", "C", "C", None]),
            Board(["A", "A", "A", None, "B", "B", None, "A", "D", "C", "C", "C", None])])
    
# board invalid
def test_fill_no_touch_invalid_input():
    compare_unordered_list_of_boards(
        list(fill_no_touch({"A": 3, "B": 2},
                           Board(["A", "A", None, None, None, None, None, None, "B"]))), [])
    
def test_fill_no_touch_invalid_input_mid():
    compare_unordered_list_of_boards(
        list(fill_no_touch({"A": 1, "B": 1},
                          Board([None, None, "A", "B", None]))), [])
    
# add_one_no_touch
# inputs:
#     - obj1: The object to add to the board
#     - obj2: The object not allowed to be adjacent to obj2
#     - num_obj1: The number of obj1 to add to the board
#     - board: The board to add obj1 to (must be valid to begin with)
#     - start_i: The index at which to begin adding obj1, default = 0
# output:
#     - A generator of all boards valid by adding num_obj1 obj1's to board,
#       without any obj1's touching obj2's

# Testing Strategy:
#     - partition: num_obj1 = 0, = 1, > 1
#     - partition: board - contains obj1, does not contain obj1
#     - partition: board - contains obj1, does not contain obj1
#     - partition: board - empty, not empty

# num_obj1 = 0, board - empty 
def test_add_one_no_touch_none_on_empty():
    compare_unordered_list_of_boards(
        list(add_one_no_touch("A", "B", 0, Board([None, None, None, None]))), [Board([None, None, None, None])])

# num_obj1 = 0, board - valid, contains obj1 and obj2
def test_add_one_no_touch_none_on_valid():
    compare_unordered_list_of_boards(
        list(add_one_no_touch("A", "B", 0, Board(["A", None, "B", None]))), [Board(["A", None, "B", None])])

# num_obj1 = 1, board - empty
def test_add_one_no_touch_one_on_empty():
    compare_unordered_list_of_boards(
        list(add_one_no_touch("A", "B", 1, Board([None, None, None, None]))), [
            Board(["A", None, None, None]),
            Board([None, "A", None, None]),
            Board([None, None, "A", None]),
            Board([None, None, None, "A"])])

# num_obj1 = 1, board - contains other objects
def test_add_one_no_touch_one_on_others():
    compare_unordered_list_of_boards(
        list(add_one_no_touch("A", "B", 1, Board(["C", None, "D", None, None]))), [
            Board(["C", "A", "D", None, None]),
            Board(["C", None, "D", "A", None]),
            Board(["C", None, "D", None, "A"])])

# num_obj1 = 1, board - contains obj1
def test_add_one_no_touch_one_on_obj1():
    compare_unordered_list_of_boards(
        list(add_one_no_touch("A", "B", 1, Board(["A", "C", None, None, "D"]))), [
            Board(["A", "C", "A", None, "D"]),
            Board(["A", "C", None, "A", "D"])])

# num_obj1 = 1, board - contains obj2
def test_add_one_no_touch_one_on_obj2():
    compare_unordered_list_of_boards(
        list(add_one_no_touch("A", "B", 1, Board(["C", None, "B", None, None, "E", None]))), [
            Board(["C", None, "B", None, "A", "E", None]),
            Board(["C", None, "B", None, None, "E", "A"])])

# num_obj1 = 1, board - contains obj1 and obj2
def test_add_one_no_touch_one_on_both():
    compare_unordered_list_of_boards(
        list(add_one_no_touch("A", "B", 1, Board(["A", "C", None, None, "B", None, "A", None, "C"]))), [
            Board(["A", "C", "A", None, "B", None, "A", None, "C"]),
            Board(["A", "C", None, None, "B", None, "A", "A", "C"])])

# num_obj1 > 1, board - empty
def test_add_one_no_touch_many_on_empty():
    compare_unordered_list_of_boards(
        list(add_one_no_touch("A", "B", 4, Board([None, None, None, None, None, None]))), [
            Board(["A", "A", "A", "A", None, None]),
            Board(["A", "A", "A", None, "A", None]),
            Board(["A", "A", "A", None, None, "A"]),
            Board(["A", "A", None, "A", "A", None]),
            Board(["A", "A", None, "A", None, "A"]),
            Board(["A", "A", None, None, "A", "A"]),
            Board(["A", None, "A", "A", "A", None]),
            Board(["A", None, "A", "A", None, "A"]),
            Board(["A", None, "A", None, "A", "A"]),
            Board(["A", None, None, "A", "A", "A"]),
            Board([None, "A", "A", "A", "A", None]),
            Board([None, "A", "A", "A", None, "A"]),
            Board([None, "A", "A", None, "A", "A"]),
            Board([None, "A", None, "A", "A", "A"]),
            Board([None, None, "A", "A", "A", "A"])])

# num_obj1 > 1, board - contains other objects
def test_add_one_no_touch_many_on_others():
    compare_unordered_list_of_boards(
        list(add_one_no_touch("A", "B", 2, Board([None, "D", "C", None, "E", None]))), [
            Board(["A", "D", "C", "A", "E", None]),
            Board(["A", "D", "C", None, "E", "A"]),
            Board([None, "D", "C", "A", "E", "A"])])

# num_obj1 > 1, board - contains obj1
def test_add_one_no_touch_many_on_obj1():
    compare_unordered_list_of_boards(
        list(add_one_no_touch("A", "B", 3, Board([None, None, None, "A", "C", "A", None]))), [
            Board(["A", "A", "A", "A", "C", "A", None]),
            Board(["A", "A", None, "A", "C", "A", "A"]),
            Board(["A", None, "A", "A", "C", "A", "A"]),
            Board([None, "A", "A", "A", "C", "A", "A"])])

# num_obj1 > 1, board - contains obj2
def test_add_one_no_touch_many_on_obj2():
    compare_unordered_list_of_boards(
        list(add_one_no_touch("A", "B", 2, Board([None, None, "B", None, "C", "D", None, None]))), [
            Board(["A", None, "B", None, "C", "D", "A", None]),
            Board(["A", None, "B", None, "C", "D", None, "A"]),
            Board([None, None, "B", None, "C", "D", "A", "A"])])

# num_obj1 > 1, board - contains obj1 and obj2
def test_add_one_no_touch_many_on_both():
    compare_unordered_list_of_boards(
        list(add_one_no_touch("A", "B", 2, Board([None, "A", None, "B", None, None, "C", None, "A", None, None, "B"]))), [
            Board([None, "A", None, "B", None, "A", "C", "A", "A", None, None, "B"]),
            Board([None, "A", None, "B", None, "A", "C", None, "A", "A", None, "B"]),
            Board([None, "A", None, "B", None, None, "C", "A", "A", "A", None, "B"])])
    
# add_two_no_touch
# inputs:
#     - obj1: The object to add to the board
#     - obj2: The object not allowed to be adjacent to obj2
#     - num_obj1: The number of obj1 to add to the board
#     - num_obj2: The 
#     - board: The board to add obj1 to (must be valid to begin with)
# output:
#     - A generator of all boards valid by adding num_obj1 obj1's to board
#       and num_obj2 obj2's to board without any obj1's touching obj2's

# Testing Strategy:
#     - partition: num_obj1 = 0, = 1, > 1
#     - partition: num_obj2 = 0, = 1, > 1
#     - partition: board - contains obj1, does not contain obj1
#     - partition: board - contains obj1, does not contain obj1
#     - partition: board - empty, not empty

# num_obj1 = 0, num_obj2 = 0, board empty
def test_add_two_no_touch_none_on_empty():
    compare_unordered_list_of_boards(
        list(add_two_no_touch("A", "B", 0, 0, Board([None, None, None]))), [Board([None, None, None])])

# num_obj1 = 0, num_obj2 = 0, board contains no obj1, obj2
def test_add_two_no_touch_none_on_others():
    compare_unordered_list_of_boards(
        list(add_two_no_touch("A", "B", 0, 0, Board(["C", "D", None, None]))), [Board(["C", "D", None, None])])

# num_obj1 = 1, num_obj2 = 0, board empty
def test_add_two_no_touch_one_obj1_on_empty():
    compare_unordered_list_of_boards(
        list(add_two_no_touch("A", "B", 1, 0, Board([None, None, None, None, None]))), [
            Board(["A", None, None, None, None]),
            Board([None, "A", None, None, None]),
            Board([None, None, "A", None, None]),
            Board([None, None, None, "A", None]),
            Board([None, None, None, None, "A"])])

# num_obj1 = 1, num_obj2 = 0, board contains no obj1, obj2
def test_add_two_no_touch_one_obj1_on_others():
    compare_unordered_list_of_boards(
        list(add_two_no_touch("A", "B", 1, 0, Board([None, "C", "C", None, None]))), [
            Board(["A", "C", "C", None, None]),
            Board([None, "C", "C", "A", None]),
            Board([None, "C", "C", None, "A"])])

# num_obj1 = 1, num_obj2 = 0, board contains obj1
def test_add_two_no_touch_one_obj1_on_obj1():
    compare_unordered_list_of_boards(
        list(add_two_no_touch("A", "B", 1, 0, Board(["A", None, "A", None, "A"]))), [
            Board(["A", "A", "A", None, "A"]),
            Board(["A", None, "A", "A", "A"])])

# num_obj1 = 0, num_obj2 = 1, board empty
def test_add_two_no_touch_one_obj2_on_empty():
    compare_unordered_list_of_boards(
        list(add_two_no_touch("A", "B", 0, 1, Board([None, None, None]))), [
            Board(["B", None, None]),
            Board([None, "B", None]),
            Board([None, None, "B"])])

# num_obj1 = 0, num_obj2 = 1, board contains no obj1, obj2
def test_add_two_no_touch_one_obj2_on_others():
    compare_unordered_list_of_boards(
        list(add_two_no_touch("A", "B", 0, 1, Board([None, "C", "D", "D", None, None]))), [
            Board(["B", "C", "D", "D", None, None]),
            Board([None, "C", "D", "D", "B", None]),
            Board([None, "C", "D", "D", None, "B"])])

# num_obj1 = 0, num_obj2 = 1, board contains obj1 & obj2
def test_add_two_no_touch_one_obj2_on_both():
    compare_unordered_list_of_boards(
        list(add_two_no_touch("A", "B", 0, 1, Board(["A", None, "B", None, None, "A", None, None, None]))), [
            Board(["A", None, "B", "B", None, "A", None, None, None]),
            Board(["A", None, "B", None, None, "A", None, "B", None])])
    
# num_obj1 = 0, num_obj2 > 1, board contains obj1
def test_add_two_no_touch_many_obj2_on_obj1():
    compare_unordered_list_of_boards(
        list(add_two_no_touch("A", "B", 0, 2, Board(["A", "A", None, None, None, None, "A", None, None, None, None]))), [
            Board(["A", "A", None, "B", "B", None, "A", None, None, None, None]),
            Board(["A", "A", None, "B", None, None, "A", None, "B", None, None]),
            Board(["A", "A", None, "B", None, None, "A", None, None, "B", None]),
            Board(["A", "A", None, None, "B", None, "A", None, "B", None, None]),
            Board(["A", "A", None, None, "B", None, "A", None, None, "B", None]),
            Board(["A", "A", None, None, None, None, "A", None, "B", "B", None])])

# num_obj1 > 1, num_obj2 > 1, board empty
def test_add_two_no_touch_both_on_empty():
    compare_unordered_list_of_boards(
        list(add_two_no_touch("A", "B", 2, 2, Board([None, None, None, None, None, None, None]))), [
            Board(["A", "A", None, "B", "B", None, None]),
            Board(["A", "A", None, None, "B", "B", None]),
            Board(["A", None, "A", None, "B", "B", None]),
            Board(["A", "A", None, "B", None, "B", None]),
            Board([None, "A", "A", None, "B", "B", None]),
            Board([None, "A", "A", None, None, "B", "B"]),
            Board([None, "A", None, "A", None, "B", "B"]),
            Board([None, "A", "A", None, "B", None, "B"]),
            Board([None, None, "A", "A", None, "B", "B"]),
            Board(["B", None, "A", "A", None, None, "B"]),
            Board(["B", None, "A", None, "A", None, "B"]),
            Board(["B", None, "A", "A", None, "B", None]),
            Board(["B", None, None, "A", "A", None, "B"]),
            Board(["B", "B", None, "A", "A", None, None]),
            Board(["B", "B", None, "A", None, "A", None]),
            Board([None, "B", None, "A", "A", None, "B"]),
            Board(["B", "B", None, None, "A", "A", None]),
            Board([None, "B", "B", None, "A", "A", None]),
            Board([None, "B", "B", None, "A", None, "A"]),
            Board(["B", None, "B", None, "A", "A", None]),
            Board([None, "B", "B", None, None, "A", "A"]),
            Board([None, None, "B", "B", None, "A", "A"]),
            Board(["A", None, "B", "B", None, "A", None]),
            Board([None, "B", None, "B", None, "A", "A"]),
            Board(["A", None, "B", "B", None, None, "A"]),
            Board(["A", None, None, "B", "B", None, "A"]),
            Board([None, "A", None, "B", "B", None, "A"]),
            Board(["A", None, "B", None, "B", None, "A"])])

# num_obj1 > 1, num_obj2 = 1, board contains no obj1, obj2
def test_add_two_no_touch_both_on_others():
    compare_unordered_list_of_boards(
        list(add_two_no_touch("A", "B", 2, 1, Board(["C", "D", None, None, None, "E", "E", None, None]))), [
            Board(["C", "D", "A", "A", None, "E", "E", "B", None]),
            Board(["C", "D", "A", "A", None, "E", "E", None, "B"]),
            Board(["C", "D", "A", None, "A", "E", "E", "B", None]),
            Board(["C", "D", "A", None, "A", "E", "E", None, "B"]),
            Board(["C", "D", None, "A", "A", "E", "E", "B", None]),
            Board(["C", "D", None, "A", "A", "E", "E", None, "B"]),
            Board(["C", "D", "A", None, "B", "E", "E", "A", None]),
            Board(["C", "D", "A", None, "B", "E", "E", None, "A"]),
            Board(["C", "D", "B", None, "A", "E", "E", "A", None]),
            Board(["C", "D", "B", None, "A", "E", "E", None, "A"]),
            Board(["C", "D", "B", None, None, "E", "E", "A", "A"]),
            Board(["C", "D", None, "B", None, "E", "E", "A", "A"]),
            Board(["C", "D", None, None, "B", "E", "E", "A", "A"])])

# num_obj1 = 1, num_obj2 = 2, board contains obj1
def test_add_two_no_touch_both_on_obj1():
    compare_unordered_list_of_boards(
        list(add_two_no_touch("A", "B", 1, 2, Board([None, "C", "A", None, None, "D", None, None]))), [
            Board(["A", "C", "A", None, "B", "D", "B", None]),
            Board([None, "C", "A", "A", None, "D", "B", "B"]),
            Board(["B", "C", "A", "A", None, "D", "B", None]),
            Board(["B", "C", "A", "A", None, "D", None, "B"]),
            Board([None, "C", "A", None, "A", "D", "B", "B"]),
            Board(["B", "C", "A", None, "A", "D", "B", None]),
            Board(["B", "C", "A", None, "A", "D", None, "B"]),
            Board(["B", "C", "A", None, "B", "D", "A", None])])

# num_obj1 = 1, num_obj2 = 2, board contains obj2
def test_add_two_no_touch_both_on_obj2():
    compare_unordered_list_of_boards(
        list(add_two_no_touch("A", "B", 1, 2, Board([None, "B", "B", "B", None, None, None, "C", "E", None]))), [
            Board(["B", "B", "B", "B", None, "A", None, "C", "E", "B"]),
            Board(["B", "B", "B", "B", None, None, "A", "C", "E", "B"]),
            Board(["B", "B", "B", "B", "B", None, "A", "C", "E", None]),
            Board([None, "B", "B", "B", "B", None, "A", "C", "E", "B"]),
            Board([None, "B", "B", "B", "B", "B", None, "C", "E", "A"]),
            Board([None, "B", "B", "B", "B", None, "B", "C", "E", "A"]),
            Board([None, "B", "B", "B", None, "B", "B", "C", "E", "A"])])

# num_obj1 = 2, num_obj2 = 1, board contains obj1 & obj2
def test_add_two_no_touch_both_on_both():
    compare_unordered_list_of_boards(
        list(add_two_no_touch("A", "B", 2, 1, Board(["A", "C", None, None, None, "D", "B", "D", None, None, "B", "C", None]))), [
            Board(["A", "C", "A", "A", None, "D", "B", "D", "B", None, "B", "C", None]),
            Board(["A", "C", "A", "A", None, "D", "B", "D", None, "B", "B", "C", None]),
            Board(["A", "C", "A", None, "A", "D", "B", "D", "B", None, "B", "C", None]),
            Board(["A", "C", "A", None, "A", "D", "B", "D", None, "B", "B", "C", None]),
            Board(["A", "C", None, "A", "A", "D", "B", "D", "B", None, "B", "C", None]),
            Board(["A", "C", None, "A", "A", "D", "B", "D", None, "B", "B", "C", None]),
            Board(["A", "C", "A", None, "B", "D", "B", "D", "A", None, "B", "C", None]),
            Board(["A", "C", "A", None, "B", "D", "B", "D", None, None, "B", "C", "A"]),
            Board(["A", "C", "A", None, None, "D", "B", "D", "B", None, "B", "C", "A"]),
            Board(["A", "C", "A", None, None, "D", "B", "D", None, "B", "B", "C", "A"]),
            Board(["A", "C", None, "A", None, "D", "B", "D", "B", None, "B", "C", "A"]),
            Board(["A", "C", None, "A", None, "D", "B", "D", None, "B", "B", "C", "A"]),
            Board(["A", "C", None, None, "A", "D", "B", "D", "B", None, "B", "C", "A"]),
            Board(["A", "C", None, None, "A", "D", "B", "D", None, "B", "B", "C", "A"]),
            Board(["A", "C", "B", None, "A", "D", "B", "D", "A", None, "B", "C", None]),
            Board(["A", "C", "B", None, "A", "D", "B", "D", None, None, "B", "C", "A"]),
            Board(["A", "C", "B", None, None, "D", "B", "D", "A", None, "B", "C", "A"]),
            Board(["A", "C", None, "B", None, "D", "B", "D", "A", None, "B", "C", "A"]),
            Board(["A", "C", None, None, "B", "D", "B", "D", "A", None, "B", "C", "A"])])
    
# add_one_no_self_touch
# inputs:
#     - obj: The object to add to the board
#     - num_obj: The number of objects to add to the board
#     - board: The board to add the objects to, must be valid
# output:
#     - generator for boards starting from board created by adding num_obj obj's
#       such that no obj touches another obj

# Testing strategy:
#     - Partition: num_obj = 0, 1, > 1
#     - Partition: board - empty, not empty
#     - Partition: board - contains obj, does not contain obj

# num_obj = 0, board - empty
def test_add_one_no_self_touch_none_on_empty():
    compare_unordered_list_of_boards(
        list(add_one_no_self_touch("A", 0, Board([None, None, None, None]))), [Board([None, None, None, None])])

# num_obj = 0, board - does not contain obj
def test_add_one_no_self_touch_none_on_others():
    compare_unordered_list_of_boards(
        list(add_one_no_self_touch("A", 0, Board(["C", "D", None, "E"]))), [Board(["C", "D", None, "E"])])

# num_obj = 0, board - contains obj
def test_add_one_no_self_touch_none_on_existing():
    compare_unordered_list_of_boards(
        list(add_one_no_self_touch("A", 0, Board(["A", None, None, "A", None]))), [Board(["A", None, None, "A", None])])

# num_obj = 1, board - empty
def test_add_one_no_self_touch_one_on_empty():
    compare_unordered_list_of_boards(
        list(add_one_no_self_touch("A", 1, Board([None, None, None, None]))), [
            Board(["A", None, None, None]),
            Board([None, "A", None, None]),
            Board([None, None, "A", None]),
            Board([None, None, None, "A"])])

# num_obj = 1, board - does not contain obj
def test_add_one_no_self_touch_one_on_others():
    compare_unordered_list_of_boards(
        list(add_one_no_self_touch("A", 1, Board(["C", None, "D", None, None]))), [
            Board(["C", "A", "D", None, None]),
            Board(["C", None, "D", "A", None]),
            Board(["C", None, "D", None, "A"])])

# num_obj = 1, board - contains obj
def test_add_one_no_self_touch_one_on_existing():
    compare_unordered_list_of_boards(
        list(add_one_no_self_touch("A", 1, Board(["A", None, None, None, "A", None, None, None, None]))), [
            Board(["A", None, "A", None, "A", None, None, None, None]),
            Board(["A", None, None, None, "A", None, "A", None, None]),
            Board(["A", None, None, None, "A", None, None, "A", None])])

# num_obj > 1, board - empty
def test_add_one_no_self_touch_many_on_empty():
    compare_unordered_list_of_boards(
        list(add_one_no_self_touch("A", 2, Board([None, None, None, None, None, None]))), [
            Board(["A", None, "A", None, None, None]),
            Board(["A", None, None, "A", None, None]),
            Board(["A", None, None, None, "A", None]),
            Board([None, "A", None, "A", None, None]),
            Board([None, "A", None, None, "A", None]),
            Board([None, "A", None, None, None, "A"]),
            Board([None, None, "A", None, "A", None]),
            Board([None, None, "A", None, None, "A"]),
            Board([None, None, None, "A", None, "A"])])

# num_obj > 1, board - does not contain obj
def test_add_one_no_self_touch_many_on_others():
    compare_unordered_list_of_boards(
        list(add_one_no_self_touch("A", 3, Board([None, "B", "C", None, None, "D", "D", None, None]))), [
            Board(["A", "B", "C", "A", None, "D", "D", "A", None]),
            Board(["A", "B", "C", None, "A", "D", "D", "A", None])])

# num_obj > 1, board - contains obj
def test_add_one_no_self_touch_many_on_existing():
    compare_unordered_list_of_boards(
        list(add_one_no_self_touch("A", 2, Board([None, "A", None, None, "B", "C", None, None, None, "A", None, None]))), [
            Board([None, "A", None, "A", "B", "C", "A", None, None, "A", None, None]),
            Board([None, "A", None, "A", "B", "C", None, "A", None, "A", None, None]),
            Board([None, "A", None, "A", "B", "C", None, None, None, "A", None, "A"]),
            Board([None, "A", None, None, "B", "C", "A", None, None, "A", None, "A"]),
            Board([None, "A", None, None, "B", "C", None, "A", None, "A", None, "A"])])
    
# fill_no_within
# inputs:
#      - counts: A mapping of values to put on the board to the number of times that 
#                value should be added
#      - board: The board to add the values to 
#      - n: The number of sectors within which no two values in counts can be
# output:
#     - A generator of all boards starting from board, adding the values in counts, such 
#       that none of the values in the keys of counts are within n sectors of each other

# Testing strategy:
#     - Partition: # keys in counts: 0, 1, 2, > 2
#     - Partition: board - empty, not empty
#     - Partition: board - valid, not valid
#     - Partition: board - contains objects in counts, does not contain objects in counts
#     - Partition: n - 2, > 2
#     - Partition: output length: 0, > 0
#     - Partition: max val in counts: 1, > 1

fill_no_within({}, Board([None, None, None]), 3)

# keys = 0, board empty
def test_fill_no_within_none_on_empty():
    compare_unordered_list_of_lists(
        list(fill_no_within({}, [None, None, None], 3)), [[None, None, None]])

# keys = 0, board not empty
def test_fill_no_within_none_on_others():
    compare_unordered_list_of_lists(
        list(fill_no_within({}, ["C", "D", None, None], 2)), [["C", "D", None, None]])

# keys = 1, board empty, max = 1
def test_fill_no_within_one_on_empty():
    compare_unordered_list_of_lists(
        list(fill_no_within({"A": 1}, [None, None, None], 4)), [
            ["A", None, None],
            [None, "A", None],
            [None, None, "A"]])

# keys = 1, board contains objects not in counts, max > 1
def test_fill_no_within_one_on_others():
    compare_unordered_list_of_lists(
        list(fill_no_within({"A": 3}, [None, "B", "C", "D", None, None, None, "B"], 3)), [
            ["A", "B", "C", "D", "A", "A", None, "B"],
            ["A", "B", "C", "D", "A", None, "A", "B"],
            ["A", "B", "C", "D", None, "A", "A", "B"],
            [None, "B", "C", "D", "A", "A", "A", "B"]])

# keys = 1, board contains objects in counts, max = 1
def test_fill_no_within_one_on_existing():
    compare_unordered_list_of_lists(
        list(fill_no_within({"A": 1}, ["A", None, "B", None, None], 2)), [
            ["A", "A", "B", None, None],
            ["A", None, "B", "A", None],
            ["A", None, "B", None, "A"]])

# keys = 2, board empty, max > 1, n > 2
def test_fill_no_within_two_on_empty():
    compare_unordered_list_of_lists(
        list(fill_no_within({"A": 1, "B": 2}, [None, None, None, None, None, None, None, None, None], 3)), [
            ["A", None, None, None, "B", "B", None, None, None],
            [None, "A", None, None, None, "B", "B", None, None],
            [None, None, "A", None, None, None, "B", "B", None],
            [None, None, None, "A", None, None, None, "B", "B"],
            ["B", None, None, None, "A", None, None, None, "B"],
            ["B", "B", None, None, None, "A", None, None, None],
            [None, "B", "B", None, None, None, "A", None, None],
            [None, None, "B", "B", None, None, None, "A", None],
            [None, None, None, "B", "B", None, None, None, "A"]])

# keys = 2, board contains objects not in counts, max = 1, n = 2
def test_fill_no_within_two_on_others():
    compare_unordered_list_of_lists(
        list(fill_no_within({"A": 1, "B": 1}, ["C", "D", None, None, None, "E", None, None], 2)), [
            ["C", "D", "A", None, None, "E", "B", None],
            ["C", "D", "A", None, None, "E", None, "B"],
            ["C", "D", None, "A", None, "E", "B", None],
            ["C", "D", None, "A", None, "E", None, "B"],
            ["C", "D", None, None, "A", "E", None, "B"],
            ["C", "D", "B", None, None, "E", "A", None],
            ["C", "D", "B", None, None, "E", None, "A"],
            ["C", "D", None, "B", None, "E", "A", None],
            ["C", "D", None, "B", None, "E", None, "A"],
            ["C", "D", None, None, "B", "E", None, "A"]])

# keys = 2, board contains objects in counts, max = 1, n > 2
def test_fill_no_within_two_on_existing():
    compare_unordered_list_of_lists(
        list(fill_no_within({"A": 1, "B": 1}, ["A", "C", "C", None, None, None, "B", None, None, None, "E", None], 3)), [
            ["A", "C", "C", None, "B", None, "B", None, None, None, "E", "A"],
            ["A", "C", "C", None, None, "B", "B", None, None, None, "E", "A"],
            ["A", "C", "C", None, None, None, "B", "B", None, None, "E", "A"]])

# keys = 2, board not valid
def test_fill_no_within_two_on_invalid():
    compare_unordered_list_of_lists(
        list(fill_no_within({"A": 2, "B": 1}, ["A", None, None, "C", "B", "E", None], 3)), [])

# keys = 2, output length = 0, max > 1, n > 2
def test_fill_no_within_two_no_solution():
    compare_unordered_list_of_lists(
        list(fill_no_within({"A": 1, "B": 2}, ["C", None, None, None, "D", None, None, "E"], 3)), [])

# keys > 2, board empty, max > 1, n = 2
def test_fill_no_within_many_on_empty():
    compare_unordered_list_of_lists(
        list(fill_no_within({"A": 2, "B": 1, "C": 1}, [None, None, None, None, None, None, None, None, None, None, None], 2)), 
        rotate([
            ["A", "A", None, None, "B", None, None, "C", None, None, None],
            ["A", "A", None, None, "B", None, None, None, "C", None, None],
            ["A", "A", None, None, None, "B", None, None, "C", None, None],
            ["A", None, "A", None, None, "B", None, None, "C", None, None],
            ["A", "A", None, None, "C", None, None, "B", None, None, None],
            ["A", "A", None, None, "C", None, None, None, "B", None, None],
            ["A", "A", None, None, None, "C", None, None, "B", None, None],
            ["A", None, "A", None, None, "C", None, None, "B", None, None]
        ]))         

# keys > 2, board contains objects not in counts, max = 1, n > 2
def test_fill_no_within_many_on_others():
    compare_unordered_list_of_lists(
        list(fill_no_within({"A": 1, "B": 1, "C": 1}, 
                            ["D", "D", None, None, None, "E", None, None, None, None, None, "F"], 3)), [
            ["D", "D", "A", None, None, "E", "B", None, None, None, "C", "F"],
            ["D", "D", "A", None, None, "E", "C", None, None, None, "B", "F"],
            ["D", "D", "B", None, None, "E", "A", None, None, None, "C", "F"],
            ["D", "D", "B", None, None, "E", "C", None, None, None, "A", "F"],
            ["D", "D", "C", None, None, "E", "A", None, None, None, "B", "F"],
            ["D", "D", "C", None, None, "E", "B", None, None, None, "A", "F"]])

# keys > 2, board contains objects in counts, max = 1, n = 2
def test_fill_no_within_many_on_existing():
    compare_unordered_list_of_lists(
        list(fill_no_within({"A": 1, "B": 1, "C": 1}, ["A", None, None, None, None, None, "D", None, None, None], 2)), [
            ["A", "A", None, None, "B", None, "D", "C", None, None],
            ["A", "A", None, None, "C", None, "D", "B", None, None]])

# keys > 2, board not valid
def test_fill_no_within_many_on_invalid():
    compare_unordered_list_of_lists(
        list(fill_no_within({"A": 2, "B": 1, "C": 2}, ["A", "A", "B", None, None], 2)), [])

# keys > 2, output length = 0, max = 1
def test_fill_no_within_many_no_solutions():
    compare_unordered_list_of_lists(
        list(fill_no_within({"A": 1, "B": 1, "C": 1}, ["F", None, None, None, "D", None, None, None, "E"], 2)), [])
    
    
# fill_no_self_touch
# inputs:
#     - obj: The object to add to the board
#     - num_obj: The number of objects to add to the board
#     - board: The board to add the objects to, must be valid
# output:
#     - generator for boards starting from board created by adding num_obj obj's
#       such that no obj touches another obj

# Testing strategy:
#     - Partition: num_obj = 0, 1, > 1
#     - Partition: board - empty, not empty
#     - Partition: board - valid, not valid
#     - Partition: board - contains obj, does not contain obj

# num_obj = 0, board - empty
def test_fill_no_self_touch_none_on_empty():
    compare_unordered_list_of_lists(
        list(fill_no_self_touch("A", 0, [None, None, None, None, None])), [[None, None, None, None, None]])

# num_obj = 0, board - does not contain obj
def test_fill_no_self_touch_none_on_others():
    compare_unordered_list_of_lists(
        list(fill_no_self_touch("A", 0, ["C", None, None, "C"])), [["C", None, None, "C"]])

# num_obj = 0, board - contains obj
def test_fill_no_self_touch_none_on_existing():
    compare_unordered_list_of_lists(
        list(fill_no_self_touch("A", 0, ["A", None, None, "A", None])), [["A", None, None, "A", None]])

# num_obj = 0, board - invalid
def test_fill_no_self_touch_none_on_invalid():
    compare_unordered_list_of_lists(
        list(fill_no_self_touch("A", 0, [None, "A", "A"])), [])

# num_obj = 1, board - empty
def test_fill_no_self_touch_one_on_empty():
    compare_unordered_list_of_lists(
        list(fill_no_self_touch("A", 1, [None, None, None, None])), [
            ["A", None, None, None],
            [None, "A", None, None],
            [None, None, "A", None],
            [None, None, None, "A"]])

# num_obj = 1, board - does not contain obj
def test_fill_no_self_touch_one_on_others():
    compare_unordered_list_of_lists(
        list(fill_no_self_touch("A", 1, ["C", None, "D", "E", None])), [
            ["C", "A", "D", "E", None],
            ["C", None, "D", "E", "A"]])

# num_obj = 1, board - contains obj
def test_fill_no_self_touch_one_on_existing():
    compare_unordered_list_of_lists(
        list(fill_no_self_touch("A", 1, [None, "A", "B", None, None, None])), [
            [None, "A", "B", "A", None, None],
            [None, "A", "B", None, "A", None],
            [None, "A", "B", None, None, "A"]])

# num_obj = 1, board - invalid
def test_fill_no_self_touch_one_on_invalid():
    compare_unordered_list_of_lists(
        list(fill_no_self_touch("A", 1, [None, "C", "A", "A", None])), [])

# num_obj > 1, board - empty
def test_fill_no_self_touch_many_on_empty():
    compare_unordered_list_of_lists(
        list(fill_no_self_touch("A", 2, [None, None, None, None, None])), [
            ["A", None, "A", None, None],
            ["A", None, None, "A", None],
            [None, "A", None, "A", None],
            [None, "A", None, None, "A"],
            [None, None, "A", None, "A"]])

# num_obj > 1, board - does not contain obj
def test_fill_no_self_touch_many_on_others():
    compare_unordered_list_of_lists(
        list(fill_no_self_touch("A", 3, ["C", "D", None, None, "D", None, None, None])), [
            ["C", "D", "A", None, "D", "A", None, "A"],
            ["C", "D", None, "A", "D", "A", None, "A"]])

# num_obj > 1, board - contains obj
def test_fill_no_self_touch_many_on_existing():
    compare_unordered_list_of_lists(
        list(fill_no_self_touch("A", 2, ["A", "B", None, None, None, None, "E", None, None])), [
            ["A", "B", "A", None, "A", None, "E", None, None],
            ["A", "B", "A", None, None, "A", "E", None, None],
            ["A", "B", "A", None, None, None, "E", "A", None],
            ["A", "B", None, "A", None, "A", "E", None, None],
            ["A", "B", None, "A", None, None, "E", "A", None],
            ["A", "B", None, None, "A", None, "E", "A", None],
            ["A", "B", None, None, None, "A", "E", "A", None]])

# num_obj > 1, board - invalid
def test_fill_no_self_touch_many_on_invalid():
    compare_unordered_list_of_lists(
        list(fill_no_self_touch("A", 3, ["A", None, None, "C", "C", "A"])), [])
    
# ordered_partitions
# inputs:
#     - n: Number to split into partitions
#     - I: minimum size of a partition
# output:
#     - a list of partitions of n, where two partitions are distinct if they are 
#       in different orders

# Testing Strategy:
#     - Partition: n < I, n >= I
#     - Partition: output length = 0, 1, > 1
#     - Partition: I = 1, > 1
#     - Partition: # outputs not all one number: = 0, > 0

# n < I, output length = 0
# n = 3, I = 5
def test_ordered_partitions_less_than_minimum():
    compare_unordered_list_of_lists(ordered_partitions(3, I=5), [])
    
# n >= I, I = 1, output length > 1
# I = 1, n = 5
def test_ordered_partitions_minimum_one_order_needed():
    compare_unordered_list_of_lists(ordered_partitions(5, I=1), [
        [1, 1, 1, 1, 1],
        [1, 1, 1, 2],
        [1, 1, 2, 1],
        [1, 2, 1, 1],
        [2, 1, 1, 1],
        [1, 2, 2],
        [2, 1, 2],
        [2, 2, 1],
        [1, 1, 3],
        [1, 3, 1],
        [3, 1, 1],
        [1, 4],
        [4, 1],
        [5],
        [2, 3],
        [3, 2]])
    
# I = 1, outputs not all one number = 0
# I = 1, n = 2
def test_ordered_partitions_minimum_one_no_order_needed():
    compare_unordered_list_of_lists(ordered_partitions(2, I=1), [[1, 1], [2]])

# I > 1, output length = 1, outputs not all one number = 0
# I = 2, n = 4
def test_ordered_partitions_minimum_two_no_order_needed():
    compare_unordered_list_of_lists(ordered_partitions(4, I=2), [[2, 2], [4]])

# I > 1, output length > 1, outputs not all one number > 0
# I = 3, n = 8
def test_ordered_partitions_minimum_three_order_needed():
    compare_unordered_list_of_lists(ordered_partitions(8, I=3), [
        [3, 5],
        [5, 3],
        [4, 4],
        [8]])
    
# calc_partitions
# inputs:
#     - n: Number to split into partitions
#     - I: minimum size of a partition
# output:
#     - a list of partitions of n, where two partitions are the same if they have the same
#       elements in different orders

# Testing Strategy:
#     - Partition: n < I, n >= I
#     - Partition: output length = 0, 1, > 1
#     - Partition: I = 1, > 1
#     - Partition: # outputs not all one number: = 0, > 0

# n < I
# n = 4, I = 5, output length = 0
def test_calc_partitions_less_than_minimum():
    compare_unordered_list_of_lists(calc_partitions(4, I=5), [])
                                    
# n >= I, I = 1, outputs not all one number = 0
# I = 1, n = 2
def test_calc_partitions_minimum_one_no_order():
    compare_unordered_list_of_lists(calc_partitions(2, I=1), [[1,1], [2]])

# I = 1, outputs not all one number > 0
# I = 1, n = 6
def test_calc_partitions_minimum_one_has_order():
    compare_unordered_list_of_lists(calc_partitions(6, I=1), [
        [1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 2],
        [1, 1, 1, 3],
        [1, 1, 2, 2],
        [1, 2, 3],
        [1, 1, 4],
        [1, 5],
        [2, 2, 2],
        [2, 4],
        [3, 3],
        [6]])

# I > 1, outputs not all one number = 0
# I = 2, n = 4
def test_calc_partitions_minimum_two_no_order():
    compare_unordered_list_of_lists(calc_partitions(4, I=2), [[2,2], [4]])

# I > 1, outputs not all one number > 0
# I = 4, n = 20
def test_calc_partitions_minimum_four_has_order():
    compare_unordered_list_of_lists(calc_partitions(12, I=4), [
        [4, 4, 4],
        [4, 8],
        [5, 7],
        [6, 6],
        [12]])
        