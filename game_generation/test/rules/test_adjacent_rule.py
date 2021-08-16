from planetx_game.rules import *

from ..assertion_utils import *

import pytest


# is_satisfied
# inputs:
#     - self: an AdjacentRule
#     - board: A board
# output:
#     - true if board follows this rule, false otherwise

# Testing strategy:
#     - partition: output: true, false
#     - partition: adjacent on edges, adjacent in middle, adjacent in both, not adjacent
#     - partition: qualifier - every, at least one, none

# qualifier - every, adjacent - edges, output = true
def test_is_satisfied_every_edges_true():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).is_satisfied(Board(["A", None, None, "B"])) == True
    
# qualifier - every, adjacent - edges, output = false
def test_is_satisfied_every_edges_false():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).is_satisfied(Board(["B", None, None, None, "A", "A"])) == False
    
# qualifier - every, adjacent - middle, output = true
def test_is_satisfied_every_middle_true():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).is_satisfied(Board([None, None, "B", "A"])) == True

# qualifier - every, adjacent - middle, output = false
def test_is_satisfied_every_middle_false():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).is_satisfied(Board([None, "A", "B", None, "A"])) == False

# qualifier - every, adjacent - both, output = true
def test_is_satisfied_every_both_true():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).is_satisfied(Board(["B", "A", None, None, "B", None, "B", "A"])) == True

# qualifier - every, adjacent - both, output = false
def test_is_satisfied_every_both_false():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).is_satisfied(Board(["B", None, "A", "B", None, "A", "A"])) == False
    
# qualifier - every, adjacent - none, output = true
def test_is_satisfied_every_none_true():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).is_satisfied(Board([None, None, None, None, None])) == True

# qualifier - every, adjacent - none, output = false
def test_is_satisfied_every_none_false():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).is_satisfied(Board(["A", None, "B", "B", None, "A", None])) == False
                                                                           
# qualifier - at least one, adjacent - edges, output = true
def test_is_satisfied_at_least_one_edges_true():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).is_satisfied(Board(["A", None, None, None, "B", "B"])) == True

# qualifier - at least one, adjacent - middle, output = true
def test_is_satisfied_at_least_one_middle_true():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).is_satisfied(Board([None, "A", "B", "A", None])) == True

# qualifier - at least one, adjacent - both, output = true
def test_is_satisfied_at_least_one_both_true():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).is_satisfied(Board(["A", None, "A", "B"])) == True

# qualifier - at least one, adjacent - none, output = false
def test_is_satisfied_at_least_one_none_false():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).is_satisfied(Board(["B", None, "A", None, "A", None])) == False

# qualifier - none, adjacent - edges, output = false
def test_is_satisfied_none_edges_false():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).is_satisfied(Board(["A", None, "B", None, "B"])) == False

# qualifier - none, adjacent - middle, output = false
def test_is_satisfied_none_middle_false():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).is_satisfied(Board([None, "A", "B", None, "A"])) == False

# qualifier - none, adjacent - both, output = false
def test_is_satisfied_none_both_false():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).is_satisfied(Board(["A", None, "B", "A", "B"])) == False

# qualifier - none, adajacent - none, output = true
def test_is_satisfied_none_none_true():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).is_satisfied(Board(["A", None, "B", None, None, "B", None])) == True
    
# fill_board
# inputs:
#     - self: An adjacent rule
#     - board: A board to start from
#     - num_objects: Dictionary mapping objects to the total amount of time they should appear
#       in the final board
# output:
#     - a list or a generator of boards starting from board with the minimum number of objects
#       from num_objects filled in to ensure that, going forward, any addition to the board 
#       will still fit this rule

# Testing strategy:
#     - partition: qualifier - every, at least one, none
#     - partition: board - empty, not empty
#     - partition: board - contains obj1, does not contain obj1
#     - partition: board - contains obj2, does not contain obj2
#     - partition: board - contains other objects, does not contain other objects
#     - partition: board - valid, invalid
#     - partition: output length - 0, > 0

# qualifier - every, board - empty, output length > 0
def test_fill_board_every_empty():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board([None, None, None, None, None]), {"A": 2, "B": 2})), rotate_boards([
            Board(["A", "B", "A", None, None]),
            Board(["A", "B", "B", "A", None]),
            Board(["B", "A", "A", "B", None])]))
    
# qualifier - every, board - contains others, output length > 0
def test_fill_board_every_on_others():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board([None, None, "C", None, None, "D"]), {"A": 2, "B": 2})), [
            Board(["A", "B", "C", "A", "B", "D"]),
            Board(["A", "B", "C", "B", "A", "D"]),
            Board(["B", "A", "C", "A", "B", "D"]),
            Board(["B", "A", "C", "B", "A", "D"])])

# qualifier - every, board - contains obj1, output length > 0
def test_fill_board_every_on_obj1():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["A", None, None, None, "A", None]), {"A": 3, "B": 2})), [
            Board(["A", "B", "A", None, "A", "B"]),
            Board(["A", "B", "A", "B", "A", None]),
            Board(["A", "A", "B", None, "A", "B"]),
            Board(["A", None, "A", "B", "A", "B"]),
            Board(["A", None, "B", "A", "A", "B"])])
    
# qualifier - every, board - contains others & obj1, output length > 0
def test_fill_board_every_on_obj1_and_others():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["C", "A", None, "C", None, None, None]), {"A": 2, "B": 3})), [
            Board(["C", "A", "B", "C", "A", "B", None]),
            Board(["C", "A", "B", "C", None, "A", "B"]),
            Board(["C", "A", "B", "C", "B", "A", None]),
            Board(["C", "A", "B", "C", None, "B", "A"])])

# qualifier - every, board - contains obj2, output length > 0
def test_fill_board_every_on_obj2():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["B", "B", None, None, None, None]), {"A": 2, "B": 3})), [
            Board(["B", "B", "A", None, None, "A"]),
            Board(["B", "B", "A", "A", "B", None]),
            Board(["B", "B", "A", None, "A", "B"]),
            Board(["B", "B", "A", "B", "A", None]),
            Board(["B", "B", "B", "A", None, "A"]),
            Board(["B", "B", None, "A", "B", "A"]),
            Board(["B", "B", None, "B", "A", "A"])])
    
# qualifier - every, board - contains others & obj2, output length > 2
def test_fill_board_every_on_obj2_and_others():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["B", "C", "C", None, "C", None, None, "D", "B", None]), {"A": 2, "B": 3})), [
            Board(["B", "C", "C", None, "C", "A", "B", "D", "B", "A"]),
            Board(["B", "C", "C", None, "C", "B", "A", "D", "B", "A"])])

# qualifier - every, board - contains both, valid, output length > 0
def test_fill_board_every_on_both():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["A", "B", "A", None, "A", None, None, None, None, "A", None]), {"A": 5, "B": 4})), [
            Board(["A", "B", "A", "B", "A", "A", "B", None, "B", "A", None]),
            Board(["A", "B", "A", "B", "A", "A", "B", None, None, "A", "B"]),
            Board(["A", "B", "A", "B", "A", None, "A", "B", "B", "A", None]),
            Board(["A", "B", "A", "B", "A", None, "A", "B", None, "A", "B"]),
            Board(["A", "B", "A", "B", "A", None, None, "A", "B", "A", None]),
            Board(["A", "B", "A", "B", "A", None, "B", "A", None, "A", "B"]),
            Board(["A", "B", "A", "B", "A", None, None, "B", "A", "A", "B"]),
            Board(["A", "B", "A", None, "A", "B", "A", None, "B", "A", None]),
            Board(["A", "B", "A", None, "A", "B", "A", None, None, "A", "B"]),
            Board(["A", "B", "A", None, "A", "B", "B", "A", None, "A", "B"]),
            Board(["A", "B", "A", None, "A", "B", None, "A", "B", "A", None]),
            Board(["A", "B", "A", None, "A", "B", None, "B", "A", "A", "B"])])
    
# qualifier - every, board - contains others & both, output length > 0
def test_fill_board_every_on_both_and_others():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["A", "C", "D", None, None, "B", "C", "B", None, None, None, "A", None]), {"A": 3, "B": 4})), [
            Board(["A", "C", "D", "A", "B", "B", "C", "B", None, None, None, "A", "B"]),
            Board(["A", "C", "D", None, "A", "B", "C", "B", None, None, None, "A", "B"]),
            Board(["A", "C", "D", None, None, "B", "C", "B", "A", None, None, "A", "B"]),
            Board(["A", "C", "D", None, None, "B", "C", "B", "B", "A", None, "A", "B"]),
            Board(["A", "C", "D", None, None, "B", "C", "B", None, "A", "B", "A", "B"]),
            Board(["A", "C", "D", None, None, "B", "C", "B", None, "B", "A", "A", "B"])])

# qualifier - every, board - contains others, output length = 0
def test_fill_board_every_on_others_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["C", None, "D", None, "E", None, "C"]), {"A": 1, "B": 1})), [])

# qualifier - every, board - contains obj1, output length = 0
def test_fill_board_every_on_obj1_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board([None, "A", None, None, "A", None, None, "A", None]), {"A": 3, "B": 2})), [])
    
# qualifier - every, board - contains obj1 and others, output length = 0
def test_fill_board_every_on_obj1_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["C", "A", "C", None, None, "A", None, None]), {"A": 2, "B": 2})), [])

# qualifier - every, board - contains obj2, output length = 0
def test_fill_board_every_on_obj2_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["B", None, None, None, "B"]), {"A": 3, "B": 2})), [])
    
# qualifier - every, board - contains obj2 and others, output length = 0
def test_fill_board_every_on_obj2_and_ohers_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["B", "C", None, None, "B", None, "C", None, "D"]), {"A": 3, "B": 2})), [])

# qualifier - every, board - contains both, valid, output length = 0
def test_fill_board_every_on_both_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["A", "B", "A", None, None, None, "B", None, "A"]), {"A": 6, "B": 3})), [])

# qualifier - every, board - contains both and others, valid, output length = 0
def test_fill_board_every_on_both_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["C", "A", "B", None, None, "B", "D", None]), {"A": 4, "B": 2})), [])
    
# qualifier - every, board - invalid, output length = 0
def test_fill_board_every_invalid():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["C", "A", "A", "B", None, None, "D"]), {"A": 2, "B": 2})), [])

# qualifier - at least one, board - empty, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_empty():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, None, None, None, None, None]), {"A": 2, "B": 3})), rotate_boards([
            Board(["A", "B", None, None, None, None]),
            Board(["B", "A", None, None, None, None])]))

# qualifier - at least one, board - contains others, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_others():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, None, "C", None, None, None, "D", "E"]), {"A": 2, "B": 2})), [
            Board(["A", "B", "C", None, None, None, "D", "E"]),
            Board(["B", "A", "C", None, None, None, "D", "E"]),
            Board([None, None, "C", "A", "B", None, "D", "E"]),
            Board([None, None, "C", "B", "A", None, "D", "E"]),
            Board([None, None, "C", None, "A", "B", "D", "E"]),
            Board([None, None, "C", None, "B", "A", "D", "E"])])

# qualifier - at least one, board - contains obj1, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_obj1():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, None, "A", "A", None, None]), {"A": 3, "B": 2})), [
            Board([None, "B", "A", "A", None, None]),
            Board([None, None, "A", "A", "B", None]),
            Board(["A", None, "A", "A", None, "B"]),
            Board(["B", None, "A", "A", None, "A"]),
            Board(["B", "A", "A", "A", None, None]),
            Board([None, None, "A", "A", "A", "B"])])

# qualifier - at least one, board - contains obj1 and others, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_obj1_and_others():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, "C", "A", None, None, None]), {"A": 2, "B": 1})), [
            Board([None, "C", "A", "B", None, None]),
            Board(["A", "C", "A", None, None, "B"]),
            Board([None, "C", "A", "A", "B", None]),
            Board([None, "C", "A", None, "A", "B"]),
            Board(["B", "C", "A", None, None, "A"])])

# qualifier - at least one, board - contains obj2, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_obj2():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, None, None, "B", None, None, None]), {"A": 2, "B": 2})), [
            Board(["A", "B", None, "B", None, None, None]),
            Board(["A", None, None, "B", None, None, "B"]),
            Board([None, "A", "B", "B", None, None, None]),
            Board(["B", "A", None, "B", None, None, None]),
            Board([None, None, "A", "B", None, None, None]),
            Board([None, None, None, "B", "A", None, None]),
            Board([None, None, None, "B", "B", "A", None]),
            Board([None, None, None, "B", None, "A", "B"]),
            Board([None, None, None, "B", None, "B", "A"]),
            Board(["B", None, None, "B", None, None, "A"])])

# qualifier - at least one, board - contains obj2 and others, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_obj2_and_others():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, None, "C", "B", None, None, "C"]), {"A": 2, "B": 1})), [
            Board([None, None, "C", "B", "A", None, "C"])])

# qualifier - at least one, board - contains both, valid, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_both():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, None, "A", None, "B", None, None]), {"A": 2, "B": 3})), [
            Board([None, None, "A", "B", "B", None, None]),
            Board([None, "B", "A", None, "B", None, None]),
            Board(["A", None, "A", None, "B", None, "B"]),
            Board(["B", "A", "A", None, "B", None, None]),
            Board([None, None, "A", "A", "B", None, None]),
            Board([None, None, "A", None, "B", "A", None]),
            Board([None, None, "A", None, "B", "B", "A"]),
            Board(["B", None, "A", None, "B", None, "A"])])

# qualifier - at least one, board - contains both and others, valid, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_both_and_others():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, "A", "B", "C", None, None, None]), {"A": 2, "B": 2})), [
            Board([None, "A", "B", "C", None, None, None])])

# qualifier - at least one, board - contains others, output length = 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_others_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board(["C", None, "D", None, "D"]), {"A": 1, "B": 1})), [])

# qualifier - at least one, board - contains obj1 and others, output length = 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_obj1_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board(["C", "A", "D", None, None]), {"A": 1, "B": 1})), [])

# qualifier - at least one, board - contains obj2 and others, output length = 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_obj2_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, "C", "B", "C", None, None]), {"A": 2, "B": 3})), [])

# qualifier - at least one, board - contains both, valid, output length = 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_both_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, "A", None, "B", None, None]), {"A": 1, "B": 1})), [])

# qualifier - at least one, board - contains both and others, valid, output length = 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_both_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, None, "C", "A", "D", "B", None, "E"]), {"A": 1, "B": 3})), [])

# qualifier - none, board - empty, output length > 0
def test_fill_board_none_on_empty():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, None, None, None, None]), {"A": 2, "B": 1})), rotate_boards([
            Board(["A", None, "B", None, "A"])]))

# qualifier - none, board - contains others, output length > 0
def test_fill_board_none_on_others():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["C", None, None, None, "D"]), {"A": 1, "B": 1})), [
            Board(["C", "A", None, "B", "D"]),
            Board(["C", "B", None, "A", "D"])])

# qualifier - none, board - contains obj1, output length > 0
def test_fill_board_none_on_obj1():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["A", None, None, None, "A", None]), {"A": 2, "B": 1})), [
            Board(["A", None, "B", None, "A", None])])

# qualifier - none, board - contains obj1 and others, output length > 0
def test_fill_board_none_on_obj1_and_others():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["C", "A", None, None, None, "D", None, None]), {"A": 2, "B": 1})), [
            Board(["C", "A", "A", None, "B", "D", None, None]),
            Board(["C", "A", "A", None, None, "D", "B", None]),
            Board(["C", "A", "A", None, None, "D", None, "B"]),
            Board(["C", "A", None, "A", None, "D", "B", None]),
            Board(["C", "A", None, "A", None, "D", None, "B"]),
            Board(["C", "A", None, None, "A", "D", "B", None]),
            Board(["C", "A", None, None, "A", "D", None, "B"]),
            Board(["C", "A", None, "B", None, "D", "A", None]),
            Board(["C", "A", None, None, "B", "D", "A", None]),
            Board(["C", "A", None, "B", None, "D", None, "A"]),
            Board(["C", "A", None, None, "B", "D", None, "A"])])

# qualifier - none, board - contains obj2, output length > 0
def test_fill_board_none_on_obj2_and_others():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, None, "B", None, "B", None, None, None]), {"A": 1, "B": 3})), [
            Board(["A", None, "B", "B", "B", None, None, None]),
            Board(["A", None, "B", None, "B", "B", None, None]),
            Board(["A", None, "B", None, "B", None, "B", None]),
            Board(["B", None, "B", None, "B", None, "A", None]),
            Board([None, "B", "B", None, "B", None, "A", None]),
            Board([None, None, "B", "B", "B", None, "A", None]),
            Board([None, "B", "B", None, "B", None, None, "A"]),
            Board([None, None, "B", "B", "B", None, None, "A"]),
            Board([None, None, "B", None, "B", "B", None, "A"])])

# qualifier - none, board - contains obj2 and others, output length > 0
def test_fill_board_none_on_obj2_and_others():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, "C", "B", "C", None, None, "B", None, None]), {"A": 1, "B": 2})), [
            Board(["A", "C", "B", "C", None, None, "B", None, None]),
            Board([None, "C", "B", "C", "A", None, "B", None, None]),
            Board([None, "C", "B", "C", None, None, "B", None, "A"])])

# qualifier - none, board - contains both, valid, output length > 0
def test_fill_board_none_on_both():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["A", None, "B", None, None, None, None]), {"A": 2, "B": 2})), [
            Board(["A", None, "B", "B", None, "A", None]),
            Board(["A", None, "B", "B", None, None, "A"]),
            Board(["A", None, "B", None, "B", None, "A"])])

# qualifier - none, board - contains both and others, valid, output length > 0
def test_fill_board_none_on_both_and_others():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["A", None, None, "B", "C", None, None, "D"]), {"A": 2, "B": 1})), [
            Board(["A", "A", None, "B", "C", None, None, "D"]),
            Board(["A", None, None, "B", "C", "A", None, "D"]),
            Board(["A", None, None, "B", "C", None, "A", "D"])])

# qualifier - none, board - empty, output length = 0
def test_fill_board_none_on_empty_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, None, None, None]), {"A": 2, "B": 1})), [])

# qualifier - none, board - contains others, output length = 0
def test_fill_board_none_on_others_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["C", None, "D", None, None, None]), {"A": 2, "B": 2})), [])

# qualifier - none, board - contains obj1, output length = 0
def test_fill_board_none_on_obj1_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["A", None, None, "A", None, None]), {"A": 2, "B": 1})), [])

# qualifier - none, board - contains obj1 and others, output length = 0
def test_fill_board_none_on_obj1_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["A", "C", None, "A", None, None]), {"A": 3, "B": 1})), [])

# qualifier - none, board - contains obj2, output length = 0
def test_fill_board_none_on_obj2_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["B", None, None, "B", None]), {"A": 1, "B": 2})), [])

# qualifier - none, board - contains obj2 and others, output length = 0
def test_fill_board_none_on_obj2_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, None, "B", "C", "D", None, "B", None, None, "B"]), {"A": 1, "B": 3})), [])

# qualifier - none, board - contains both, output length = 0
def test_fill_board_none_on_both_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["A", None, "B", None, "A", None, "B", None]), {"A": 3, "B": 3})), [])

# qualifier - none, board - contains both and others, output length = 0
def test_fill_board_none_on_both_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, "C", None, "A", "C", None, "B", None, "D", "B"]), {"A": 3, "B": 3})), [])

# qualifier - none, board - invalid, output length = 0
def test_fill_board_none_on_invalid():
    compare_unordered_list_of_boards(
        list(AdjacentRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["A", None, None, "A", "B", None, "C"]), {"A": 2, "B": 2})), [])
    
# allowed_rule
# inputs:
#     - self: An adjacency rule, must be valid for the given board
#     - num_objects: A dictionary mapping objects to the number of times they should 
#                    appear in the final board
#     - constraints: A list of the constraints that all boards of this type must follow
#     - other_rules: A list of the other rules already created for this board
# output:
#     - True if this rule can be added to the research rules for this board, False if 
#       it is not allowed

# Testing strategy:
#     - partition: qualifier - every, at least one, none
#     - partition: rules - total length 0, > 0
#     - partition: rules contain equivalent rule, rules do not contain equivalent rule
#     - partition: rules contain related rule, rules do not contain related rule
#                  where a related rule is an adjacency rule containing obj1 or obj2
#     - partition: rules contains related self rule, rules does not contain related self rule
#     - partition: every adjacency defined, every adjacency not necessarily defined
#     - partition: rule would over-constrain adjacencies, rule would not over-constrain adjacencies
#     - partition: existing other_rule with same two objects, no existing other rule with same two objects
#     - partition: this rule is with empty, this rule is not with empty
#     - partition: existing self other_rule with same object, no existing self other_rule with same object
#     - partition: allowed - yes, no (because obj1), no (because obj2), no (because both)


# other rule with same two objects, not rule with empty
def test_allowed_rule_existing_same_objects_not_empty():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).allowed_rule(
        {"A": 3, "B": 3, "C": 4},
        [],
        [OppositeRule("B", "A", RuleQualifier.NONE)]) == False

# other rule with same two objects, rule with empty
def test_allowed_rule_existing_same_objects_empty():
    assert AdjacentRule("A", SpaceObject.Empty, RuleQualifier.AT_LEAST_ONE).allowed_rule(
        {"A": 1, "B": 2, "C": 3},
        [],
        [WithinRule("A", SpaceObject.Empty, Precision.STRICT, 4)]) == False

# self rule with same object, rule with empty
def test_allowed_rule_existing_same_object_self_empty():
    assert AdjacentRule("A", SpaceObject.Empty, RuleQualifier.NONE).allowed_rule(
        {"A": 2, "B": 1, "C": 3, "D": 2},
        [],
        [OppositeSelfRule("A", RuleQualifier.EVERY)]) == False
    
# qualifier - every, no related or equivalent, adjacencies not defined, empty constraints, empty rules, allowed
def test_allowed_rule_every_empty():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).allowed_rule(
        {"A": 3, "B": 4, "C": 2},
        [],
        []) == True

# qualifier - every, contains equivalent rule, not allowed (because both)
def test_allowed_rule_every_equivalent_rule():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).allowed_rule(
        {"A": 2, "B": 5, "C": 1, "D": 2},
        [AdjacentRule("A", "B", RuleQualifier.EVERY)],
        []) == False

# qualifier - every, contains related rule, adjacencies not all defined, allowed
def test_allowed_rule_every_related_rule_allowed():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).allowed_rule(
        {"A": 1, "B": 2, "C": 1},
        [],
        [AdjacentRule("A", "C", RuleQualifier.AT_LEAST_ONE)]) == True
    
# qualifier - every, contains related self rule, adjacencies not all defined, allowed
def test_allowed_rule_every_related_self_rule_allowed():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).allowed_rule(
        {"A": 2, "B": 2, "C": 2},
        [AdjacentSelfRule("A", RuleQualifier.NONE)],
        [AdjacentRule("B", "C", RuleQualifier.EVERY)]) == True

# qualifier - every, contains related rule, adjacencies not all defined, would over-constrain, not allowed (obj1)
def test_allowed_rule_every_related_rule_over_constrain_obj1():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).allowed_rule(
        {"A": 2, "B": 4, "C": 3, "D": 2},
        [AdjacentRule("A", "D", RuleQualifier.EVERY), AdjacentRule("A", "C", RuleQualifier.NONE)],
        []) == False
    
# qualifier - every, contains related self rule, adjacencies not all defined, would over-constrain, not allowed (obj1)
def test_allowed_rule_every_related_self_rule_over_constrain_obj1():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).allowed_rule(
        {"A": 2, "B": 3},
        [AdjacentSelfRule("A", RuleQualifier.EVERY)],
        [AdjacentRule("C", "A", RuleQualifier.NONE)]) == False

# qualifier - every, contains related rule, adjacencies not all defined, would over-constrain, not allowed (obj2)
def test_allowed_rule_every_related_rule_over_constrain_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).allowed_rule(
        {"A": 3, "B": 2, "C": 4, "D": 1, "E": 1},
        [AdjacentRule("B", "C", RuleQualifier.EVERY), AdjacentRule("B", "E", RuleQualifier.NONE)],
        [AdjacentRule("B", "D", RuleQualifier.AT_LEAST_ONE)]) == False
    
# qualifier - every, contains related self rule, adjacencies not all defined, would over-constrain, not allowed (obj2)
def test_allowed_rule_every_related_self_rule_over_constrain_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).allowed_rule(
        {"A": 2, "B": 3, "C": 2, "E": 2},
        [AdjacentRule("E", "B", RuleQualifier.NONE), AdjacentSelfRule("B", RuleQualifier.AT_LEAST_ONE)],
        [AdjacentRule("C", "B", RuleQualifier.EVERY)]) == False

# qualifier - every, contains related rule, adjacencies not all defined, would over-constrain, not allowed (both)
def test_allowed_rule_every_related_rule_over_constrain_both():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).allowed_rule(
        {"A": 1, "B": 2, "C": 3, "D": 4},
        [AdjacentRule("A", "C", RuleQualifier.NONE), AdjacentRule("D", "B", RuleQualifier.NONE), AdjacentRule("A", "D", RuleQualifier.EVERY), AdjacentRule("B", "C", RuleQualifier.AT_LEAST_ONE)],
        []) == False
    
# qualifier - every, contains related self rule, adjacencies not all defined, would over-constrain, not allowed (both)
def test_allowed_rule_every_related_self_rule_over_constrain_both():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).allowed_rule(
        {"A": 2, "B": 2, "C": 3, "D": 3},
        [AdjacentSelfRule("A", RuleQualifier.EVERY), AdjacentRule("B", "D", RuleQualifier.EVERY)],
        [AdjacentRule("A", "C", RuleQualifier.NONE), AdjacentRule("C", "B", RuleQualifier.NONE)]) == False

# qualifier - at least one, no related or equivalent, adjacencies not defined, empty constraints, empty other_rules, allowed
def test_allowed_rule_at_least_one_empty():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).allowed_rule(
        {"A": 1, "B": 2, "C": 1},
        [],
        []) == True

# qualifier - at least one, contains equivalent rule, not allowed (because both)
def test_allowed_rule_at_least_one_equivalent():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).allowed_rule(
        {"A": 2, "B": 2, "C": 1, "D": 1},
        [],
        [AdjacentRule("B", "A", RuleQualifier.AT_LEAST_ONE)]) == False

# qualifier - at least one, contains related rule, adjacencies not all defined, allowed
def test_allowed_rule_at_least_one_related_allowed():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).allowed_rule(
        {"A": 2, "B": 2, "C": 2, "D": 2},
        [AdjacentRule("C", "A", RuleQualifier.AT_LEAST_ONE)],
        [AdjacentRule("A", "D", RuleQualifier.EVERY)]) == True

# qualifier - at least one, contains related self rule, adjacencies not all defined, allowed
def test_allowed_rule_at_least_one_related_self_allowed():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).allowed_rule(
        {"A": 2, "B": 2, "C": 1},
        [AdjacentSelfRule("A", RuleQualifier.EVERY)],
        []) == True

# qualifier - at least one, contains related rule, adjacencies not all defined, would over-constrain, not allowed (obj1)
def test_allowed_rule_at_least_one_related_over_constrain_obj1():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).allowed_rule(
        {"A": 2, "B": 1, "C": 3, "D": 1},
        [AdjacentRule("C", "A", RuleQualifier.EVERY)],
        [AdjacentRule("D", "A", RuleQualifier.NONE)]) == False

# qualifier - at least one, contains related self rule, adjacencies not all defined, would over-constrain, not allowed (obj1)
def test_allowed_rule_at_least_one_related_self_over_constrain_obj1():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).allowed_rule(
        {"A": 2, "B": 3, "C": 2, "D": 1},
        [AdjacentSelfRule("A", RuleQualifier.NONE), AdjacentRule("A", "C", RuleQualifier.EVERY)],
        [AdjacentRule("D", "A", RuleQualifier.AT_LEAST_ONE)]) == False
    
# qualifier - at least one, contains related rule, adjacencies not all defined, would over-constrain, not allowed (obj2)
def test_allowed_rule_at_least_one_related_over_constrain_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).allowed_rule(
        {"A": 1, "B": 3, "C": 2, "D": 2, "E": 1},
        [AdjacentRule("B", "C", RuleQualifier.EVERY)],
        [AdjacentRule("D", "B", RuleQualifier.EVERY), AdjacentRule("E", "B", RuleQualifier.NONE)]) == False

# qualifier - at least one, contains related self rule, adjacencies not all defined, would over-constrain, not allowed (obj2)
def test_allowed_rule_at_least_one_related_self_over_constrain_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).allowed_rule(
        {"A": 2, "B": 2, "C": 1, "D": 1, "E": 1},
        [AdjacentSelfRule("B", RuleQualifier.AT_LEAST_ONE)],
        [AdjacentRule("B", "D", RuleQualifier.NONE), AdjacentRule("E", "B", RuleQualifier.AT_LEAST_ONE)]) == False

# qualifier - at least one, contains related rule, adjacencies not all defined, would over-constrain, not allowed (both)
def test_allowed_rule_at_least_one_related_over_constrain_both():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).allowed_rule(
        {"A": 2, "B": 1, "C": 3, "D": 3, "E": 2},
        [AdjacentRule("A", "C", RuleQualifier.EVERY), AdjacentRule("B", "C", RuleQualifier.EVERY), AdjacentRule("B", "E", RuleQualifier.NONE)],
        [AdjacentRule("D", "A", RuleQualifier.AT_LEAST_ONE), AdjacentRule("E", "A", RuleQualifier.NONE)]) == False

# qualifier - at least one, contains related self rule, adjacencies not all defined, would over-constrain, not allowed (both)
def test_allowed_rule_at_least_one_related_self_over_constrain_both():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).allowed_rule(
        {"A": 2, "B": 2, "C": 3, "D": 2, "E": 1, "F": 1},
        [AdjacentSelfRule("A", RuleQualifier.NONE), AdjacentSelfRule("B", RuleQualifier.EVERY)],
        [AdjacentRule("A", "C", RuleQualifier.EVERY), AdjacentRule("D", "A", RuleQualifier.EVERY), AdjacentRule("B", "C", RuleQualifier.AT_LEAST_ONE), AdjacentRule("B", "F", RuleQualifier.NONE)]) == False


# qualifier - none, no related or equivalent, adjacencies not defined, empty constraints, empty other_rules, allowed
def test_allowed_rule_none_empty():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).allowed_rule(
        {"A": 1, "B": 1},
        [],
        []) == True

# qualifier - none, contains equivalent rule, not allowed (because both)
def test_allowed_rule_none_equivalent():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).allowed_rule(
        {"A": 2, "B": 1, "C": 2},
        [],
        [AdjacentRule("B", "A", RuleQualifier.NONE)]) == False

# qualifier - none, contains related rule, adjacencies not all defined, allowed
def test_allowed_rule_none_related_allowed():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).allowed_rule(
        {"A": 3, "B": 2, "C": 1, "D": 1},
        [AdjacentRule("A", "C", RuleQualifier.AT_LEAST_ONE)],
        [AdjacentRule("D", "A", RuleQualifier.EVERY)]) == True

# qualifier - none, contains related self rule, adjacencies not all defined, allowed 
def test_allowed_rule_none_related_self_allowed():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).allowed_rule(
        {"A": 2, "B": 3, "C": 2, "D": 2, "E": 1},
        [AdjacentSelfRule("A", RuleQualifier.EVERY)],
        [AdjacentRule("C", "A", RuleQualifier.AT_LEAST_ONE)]) == True

# qualifier - none, contains related rule, adjacencies all defined, not allowed (because obj1)
def test_allowed_rule_none_related_fully_defined_obj1():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).allowed_rule(
        {"A": 2, "B": 3, "C": 1, "D": 2, "E": 1},
        [AdjacentRule("A", "C", RuleQualifier.EVERY), AdjacentRule("D", "A", RuleQualifier.AT_LEAST_ONE)],
        [AdjacentRule("A", "E", RuleQualifier.AT_LEAST_ONE)]) == False

# qualifier - none, contains related self rule, adjacencies all defined, not allowed (because obj1)
def test_allowed_rule_none_related_self_fully_defined_obj1():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).allowed_rule(
        {"A": 4, "B": 1, "C": 3, "D": 2},
        [AdjacentSelfRule("A", RuleQualifier.EVERY), AdjacentRule("A", "C", RuleQualifier.EVERY)],
        []) == False

# qualifier - none, contains related rule, adjacencies all defined, not allowed (because obj2)
def test_allowed_rule_none_related_fully_defined_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).allowed_rule(
        {"A": 3, "B": 2, "C": 2, "D": 2, "E": 1},
        [AdjacentRule("C", "B", RuleQualifier.EVERY), AdjacentRule("B", "D", RuleQualifier.AT_LEAST_ONE)],
        [AdjacentRule("E", "B", RuleQualifier.AT_LEAST_ONE)]) == False

# qualifier - none, contains related self rule, adjacencies all defined, not allowed (because obj2)
def test_allowed_rule_none_related_self_fully_defined_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).allowed_rule(
        {"A": 2, "B": 2, "C": 1, "D": 3},
        [AdjacentSelfRule("B", RuleQualifier.EVERY)],
        [AdjacentRule("B", "D", RuleQualifier.EVERY)]) == False

# qualifier - none, contains related rule, adjacencies all defined, not allowed (because both)
def test_allowed_rule_none_related_fully_defined_both():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).allowed_rule(
        {"A": 1, "B": 2, "C": 1, "D": 2},
        [AdjacentRule("D", "A", RuleQualifier.EVERY), AdjacentRule("B", "C", RuleQualifier.EVERY)],
        [AdjacentRule("D", "B", RuleQualifier.EVERY)]) == False

# qualifier - none, contains related self rule, adjacencies all defined, not allowed (because both)
def test_allowed_rule_none_related_self_fully_defined_both():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).allowed_rule(
        {"A": 1, "B": 2, "C": 2, "D": 3, "E": 1},
        [AdjacentRule("C", "A", RuleQualifier.EVERY), AdjacentSelfRule("B", RuleQualifier.AT_LEAST_ONE), AdjacentRule("B", "D", RuleQualifier.AT_LEAST_ONE), AdjacentRule("E", "B", RuleQualifier.AT_LEAST_ONE)],
        []) == False
    
# generate_rule
# inputs:
#     - board: The board to generate a rule for
#     - constraints: The existing constraints for this type of board
#     - other_rules: The already constructed research rules for this board
#     - space_object1: The object to generate the adjacent rule about
#     - space_object2: The object to relate to space_object1 in this rule
# output:
#     - A rule relating space_object1 to space_object2 by adjacency, or
#       None if no such rule can be generated

# Testing strategy:
#     - partition: rule not allowed based on previous rules, rule allowed based on previous rules
#     - partition: # obj1s adjacent to obj2: 0, some, all
#     - partition: # obj1s: = 1, > 1
#     - partition: # obj1 = 2 * # obj2, # obj1 != 2 * # obj2

# rule not allowed based on previous rules
def test_generate_rule_not_allowed():
    assert AdjacentRule.generate_rule(
        Board(["B", "A", "C", "A", "D", "E", "E", "F"]),
        [AdjacentRule("E", "A", RuleQualifier.NONE)],
        [AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE), AdjacentRule("D", "A", RuleQualifier.EVERY)],
        "A", "B") == None

# 0 obj1s adjacent, # obj1s = 1
def test_generate_rule_none_adjacent_one_object():
    assert AdjacentRule.generate_rule(
        Board(["C", "A", "D", "E", "E", "B"]),
        [], [], "A", "B") == \
    AdjacentRule("A", "B", RuleQualifier.NONE)

# 0 obj1s adjacent, # obj1s > 1, obj1 != 2 * obj2
def test_generate_rule_none_adjacent_multiple_objects():
    assert AdjacentRule.generate_rule(
        Board(["D", "D", "A", "C", "B", "D", "A", "E", "A"]),
        [], [], "A", "B") == \
    AdjacentRule("A", "B", RuleQualifier.NONE)

# 0 obj1s adjacent, # obj1s > 1, obj1 = 2 * obj2
def test_generate_rule_none_adjacent_twice_obj2():
    assert AdjacentRule.generate_rule(
        Board(["D", "A", "C", "C", "B", "E", "A"]),
        [], [], "A", "B") == \
    AdjacentRule("A", "B", RuleQualifier.NONE)

# some obj1s adjacent, # obj1s > 1, obj1 != 2 * obj2
def test_generate_rule_some():
    assert AdjacentRule.generate_rule(
        Board(["D", "A", "B", "A", "C", "A", "E", "E", "A"]),
        [], [], "A", "B") == \
    AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE)

# some obj1s adjacent, # obj1s > 1, obj1 = 2 * obj2
def test_generate_rule_some_twice_obj2():
    assert AdjacentRule.generate_rule(
        Board(["A", "B", "A", "C", "C", "E", "A", "A", "D", "B", "F"]),
        [], [], "A", "B") == \
    AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE)

# all obj1s adjacent, # obj1s = 1
def test_generate_rule_all_one():
    assert AdjacentRule.generate_rule(
        Board(["D", "A", "B", "C", "D"]),
        [], [], "A", "B") == \
    AdjacentRule("A", "B", RuleQualifier.EVERY)

# all obj1s adjacent, # obj1s > 1, obj1 != 2 * obj2
def test_generate_rule_all_many():
    rule = AdjacentRule.generate_rule(
        Board(["A", "B", "A", "E", "D", "B", "A", "D"]),
        [], [], "A", "B")
    
    assert (rule == AdjacentRule("A", "B", RuleQualifier.EVERY) or \
            rule == AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE))

# all obj1s adjacent, # obj1s > 1, obj1 = 2 * obj2
def test_generate_rule_all_many_twice_obj2():
    assert AdjacentRule.generate_rule(
        Board(["C", "A", "B", "A", "D", "A", "B", "A", "E", "F"]),
        [], [], "A", "B") == \
    AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE)


# base_strength
# inputs:
#     - self: An AdjacentRule
#     - board: A board to evaluate the strength for
# output:
#     - A number 0-1 representing how strong the rule is. It is proportional to the number of scenarios
#       eliminated for the positions of object1, considering where object2 is. 0 means no scenarios are
#       eliminated considering this rule, and 1 means every scenario but one (the correct one) is eliminated
#       by this rule

# Testing strategy:
#     - partition: strength = 0, 0 < strength < 1, strength = 1
#     - partition: # obj1 = 1, > 1
#     - partition: # obj2 = obj1, < obj1, > obj1
#     - partition: qualifier - every, at least one, none

# qualifier - every, strength = 0, # obj1 = 1, # obj2 = # obj1
def test_base_strength_every_zero_one_obj1_one_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).base_strength(Board(["C", "A", "B"])) == 0

# qualifier - every, strength = 0, # obj1 = 1, # obj2 > # obj1
def test_base_strength_every_zero_one_obj1_many_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).base_strength(Board(["A", "B", "B"])) == 0
#     assert AdjacentRule("A", "B", RuleQualifier.EVERY).base_strength(Board(["A", "B", "B", "C"])) == 0
    
# qualifier - every, strength = 0, # obj1 > 1, # obj2 = # obj1
def test_base_strength_every_zero_many_obj1_same_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).base_strength(Board(["B", "C", "B", "A", "A"])) == 0

# qualifier - every, strength = 0, # obj1 > 1, # obj2 < # obj1
def test_base_strength_every_zero_many_obj1_fewer_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).base_strength(Board(["A", "A", "B"])) == 0

# qualifier - every, strength = 0, # obj1 > 1, # obj2 > # obj1
def test_base_strength_every_zero_many_obj1_more_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).base_strength(Board(["A", "B", "A", "D", "B", "A"])) == 0

# qualifier - every, 0 < strength < 1, # obj1 = 1, # obj2 = # obj1
def test_base_strength_every_mid_one_obj1_one_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).base_strength(Board(["A", "B", "C", "D", "E"])) == pytest.approx(2/3)

# qualifier - every, 0 < strength < 1, # obj1 = 1, # obj2 > # obj1
def test_base_strength_every_mid_one_obj1_many_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).base_strength(Board(["B", "C", "D", "A", "B", "E", "C", "C"])) == pytest.approx(2/5)

# qualifier - every, 0 < strength < 1, # obj1 > 1, # obj2 = # obj1
def test_base_strength_every_mid_many_obj1_same_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).base_strength(Board(["A", "A", "B", "C", "D", "D", "C", "B"])) == pytest.approx(9/14)

# qualifier - every, 0 < strength < 1, # obj1 > 1, # obj2 < # obj1
def test_base_strength_every_mid_many_obj1_fewer_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).base_strength(Board(["A", "B", "A", "C", "C", "A", "B", "D", "E"])) == pytest.approx(31/34)

# qualifier - every, 0 < strength < 1, # obj1 > 1, # obj2 > # obj1
def test_base_strength_every_mid_many_obj1_more_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).base_strength(Board(["B", "B", "D", "A", "B", "A", "E", "E"])) == pytest.approx(4/9)

# qualifier - every, strength = 1, # obj1 > 1, # obj2 = # obj1
def test_base_strength_every_one_many_obj1_same_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).base_strength(Board(["C", "A", "B", "B", "A", "E", "D"])) == 1

# qualifier - every, strength = 1, # obj1 > 1, # obj2 < # obj1
def test_base_strength_every_one_many_obj1_fewer_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).base_strength(Board(["C", "C", "A", "B", "A", "B", "A", "D"])) == 1

# qualifier - every, strength = 1, # obj1 > 1, # obj2 > # obj1
def test_base_strength_every_one_many_obj1_more_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.EVERY).base_strength(Board(["B", "B", "A", "D", "E", "A", "B"])) == 1

# qualifier - at least one, strength = 0, # obj1 = 1, # obj2 = # obj1
def test_base_strength_at_least_one_one_obj1_one_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).base_strength(Board(["A", "C", "B"])) == 0

# qualifier - at least one, strength = 0, # obj1 = 1, # obj2 > # obj1
def test_base_strength_at_least_one_one_obj1_more_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).base_strength(Board(["B", "C", "C", "B", "D", "B", "A"])) == 0

# qualifier - at least one, strength = 0, # obj1 > 1, # obj2 = # obj1
def test_base_strength_at_least_one_many_obj1_same_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).base_strength(Board(["B", "A", "C", "E", "B", "A"])) == 0

# qualifier - at least one, strength = 0, # obj1 > 1, # obj2 < # obj1
def test_base_strength_at_least_one_many_obj1_fewer_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).base_strength(Board(["D", "A", "B", "A"])) == 0

# qualifier - at least one, strength = 0, # obj1 > 1, # obj2 > # obj1
def test_base_strength_at_least_one_many_obj1_more_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).base_strength(Board(["A", "A", "B", "C", "B", "B", "D"])) == 0

# qualifier - at least one, 0 < strength < 1, # obj1 = 1, # obj2 = # obj1
def test_base_strength_at_least_one_mid_one_obj1_one_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).base_strength(Board(["C", "A", "B", "C", "D", "E"])) == pytest.approx(3/4)

# qualifier - at least one, 0 < strength < 1, # obj1 = 1, # obj2 > # obj1
def test_base_strength_at_least_one_mid_one_obj1_many_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).base_strength(Board(["B", "C", "D", "E", "F", "B", "A"])) == pytest.approx(2/4)

# qualifier - at least one, 0 < strength < 1, # obj1 > 1, # obj2 = # obj1
def test_base_strength_at_least_one_mid_many_obj1_same_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).base_strength(Board(["A", "B", "C", "C", "D", "A", "B", "D"])) == pytest.approx(1/14)

# qualifier - at least one, 0 < strength < 1, # obj1 > 1, # obj2 < # obj1
def test_base_strength_at_least_one_mid_many_obj1_fewer_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).base_strength(Board(["B", "C", "A", "D", "E", "D", "A"])) == pytest.approx(6/14)

# qualifier - at least one, 0 < strength < 1, # obj1 > 1, # obj2 > # obj1
def test_base_strength_at_least_one_mid_many_obj1_more_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.AT_LEAST_ONE).base_strength(Board(["B", "A", "B", "B", "A", "C", "C", "D", "E", "F"])) == pytest.approx(6/20)

# qualifier - none, 0 < strength < 1, # obj1 = 1, # obj2 = # obj1
def test_base_strength_none_mid_one_obj1_one_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).base_strength(Board(["C", "B", "D", "E", "A"])) == pytest.approx(2/3)

# qualifier - none, 0 < strength < 1, # obj1 = 1, # obj2 > # obj1
def test_base_strength_none_mid_one_obj1_many_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).base_strength(Board(["B", "C", "B", "D", "A", "A", "E", "D"])) == pytest.approx(12/14) 

# qualifier - none, 0 < strength < 1, # obj1 > 1, # obj2 = # obj1
def test_base_strength_none_mid_many_obj1_same_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).base_strength(Board(["B", "D", "E", "B", "C", "A", "E", "A", "F", "F"])) == pytest.approx(22/27)

# qualifier - none, 0 < strength < 1, # obj1 > 1, # obj2 < # obj1
def test_base_strength_none_mid_many_obj1_fewer_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).base_strength(Board(["D", "B", "C", "C", "A", "F", "E", "A"])) == pytest.approx(11/20)

# qualifier - none, 0 < strength < 1, # obj1 > 1, # obj2 > # obj1
def test_base_strength_none_mid_many_obj1_more_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).base_strength(Board(["D", "B", "B", "C", "E", "D", "B", "F", "A", "F", "A"])) == pytest.approx(22/27)

# qualifier - none, strength = 1, # obj1 = 1, # obj2 = # obj1
def test_base_strength_none_one_one_obj1_one_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).base_strength(Board(["C", "B", "C", "A"])) == 1

# qualifier - none, strength = 1, # obj1 = 1, # obj2 > # obj1
def test_base_strength_none_one_one_obj1_more_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).base_strength(Board(["B", "C", "B", "D", "A", "D"])) == 1

# qualifier - none, strength = 1, # obj1 > 1, # obj2 = # obj1
def test_base_strength_none_one_many_obj1_same_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).base_strength(Board(["B", "B", "C", "A", "A", "D"])) == 1

# qualifier - none, strength = 1, # obj1 > 1, # obj2 < # obj1
def test_base_strength_none_one_many_obj1_fewer_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).base_strength(Board(["A", "C", "B", "D", "A"])) == 1

# qualifier - none, strength = 1, # obj1 > 1, # obj2 > # obj1
def test_base_strength_none_one_many_obj1_more_obj2():
    assert AdjacentRule("A", "B", RuleQualifier.NONE).base_strength(Board(["B", "C", "A", "D", "B", "D", "A", "A", "E"])) == 1
    
# code
# inputs:
#     - self: An adjacent rule
# outputs:
#     - A four character string code representing the adjacent rule

# Testing Strategy:
#     - partition: qualifier - every, at least one, none

# qualifier - every
def test_code_every():
    assert AdjacentRule(SpaceObject.Asteroid, SpaceObject.Comet, RuleQualifier.EVERY).code() == "AACE"

# qualifier - at least one
def test_code_at_least_one():
    assert AdjacentRule(SpaceObject.DwarfPlanet, SpaceObject.Empty, RuleQualifier.AT_LEAST_ONE).code() == "ADEA"

# qualifier - none
def test_code_none():
    assert AdjacentRule(SpaceObject.GasCloud, SpaceObject.PlanetX, RuleQualifier.NONE).code() == "AGXN"
    

# parse
# inputs:
#     - s: A four letter string code representing an adjacent rule
# output:
#     - The adjacent rule represented by the code

# Testing strategy:
#     - partition: qualifier - every, at least one, none

# qualifier - every
def test_parse_every():
    assert Rule.parse("ACGE") == AdjacentRule(SpaceObject.Comet, SpaceObject.GasCloud, RuleQualifier.EVERY)
    
# qualifier - at least one
def test_parse_at_least_one():
    assert Rule.parse("ADAA") == AdjacentRule(SpaceObject.DwarfPlanet, SpaceObject.Asteroid, RuleQualifier.AT_LEAST_ONE)

# qualifier - none
def test_parse_none():
    assert Rule.parse("AXBN") == AdjacentRule(SpaceObject.PlanetX, SpaceObject.BlackHole, RuleQualifier.NONE)