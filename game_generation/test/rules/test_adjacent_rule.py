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