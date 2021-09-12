from planetx_game.rules import *

from ..assertion_utils import *

import pytest

# is_satisfied
# inputs:
#     - self: an OppositeRule
#     - board: a Board with even length
# output:
#     - true if board follows this rule, false otherwise

# Testing strategy:
#     - partition: output - true, false
#     - partition: # opposite - 0, 1, > 1
#     - partition: qualifier - every, at least one, none

# qualifier - every, opposite - 0, output - true
def test_is_satisfied_every_none_opposite_true():
    assert OppositeRule("A", "B", RuleQualifier.EVERY).is_satisfied(Board(["C", "D", "C", "E"])) == True

# qualifier - every, opposite - 0, output - false
def test_is_satisfied_every_none_opposite_false():
    assert OppositeRule("A", "B", RuleQualifier.EVERY).is_satisfied(Board(["A", "B", "C", "D"])) == False

# qualifier - every, opposite - 1, output - true
def test_is_satisfied_every_one_opposite_true():
    assert OppositeRule("A", "B", RuleQualifier.EVERY).is_satisfied(Board(["A", "C", "C", "B", "D", "E"])) == True

# qualifier - every, opposite - 1, output - false
def test_is_satisfed_every_one_opposite_false():
    assert OppositeRule("A", "B", RuleQualifier.EVERY).is_satisfied(Board(["A", "B", "C", "B", "D", "A"])) == False

# qualifier - every, opposite - > 1, output - true
def test_is_satisfied_every_many_opposite_true():
    assert OppositeRule("A", "B", RuleQualifier.EVERY).is_satisfied(Board(["C", "A", "A", "C", "C", "B", "B", "E"])) == True

# qualifier - every, opposite - > 1, output - false
def test_is_satisfied_every_many_opposite_false():
    assert OppositeRule("A", "B", RuleQualifier.EVERY).is_satisfied(Board(["A", "A", "A", "E", "B", "B", "C", "B"])) == False

# qualifier - at least one, opposite - 0, output - false
def test_is_satisfied_at_least_one_none_opposite():
    assert OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).is_satisfied(Board(["A", "C", "D", "B"])) == False

# qualifier - at least one, opposite - 1, output - true
def test_is_satisfied_at_least_one_one_opposite():
    assert OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).is_satisfied(Board(["A", "C", "D", "B", "D", "C"])) == True

# qualifier - at least one, opposite - > 1, output - true
def test_is_satisfied_at_least_one_many_opposite():
    assert OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).is_satisfied(Board(["B", "A", "C", "A", "B", "D"])) == True

# qualifier - none, opposite - 0, output - true
def test_is_satisfied_none_none_opposite():
    assert OppositeRule("A", "B", RuleQualifier.NONE).is_satisfied(Board(["A", "C", "E", "B"])) == True

# qualifier - none, opposite - 1, output - false
def test_is_satisfied_none_one_opposite():
    assert OppositeRule("A", "B", RuleQualifier.NONE).is_satisfied(Board(["C", "B", "D", "E", "A", "E"])) == False

# qualifier - none, opposite - > 1, output - false
def test_is_satisfied_none_many_opposite():
    assert OppositeRule("A", "B", RuleQualifier.NONE).is_satisfied(Board(["D", "B", "A", "D", "A", "B"])) == False
    
    
# fill_board
# inputs:
#     - self: an OppositeRule
#     - board: The starting board to fill
#     - num_objects: A dictionary mapping objects to the number of them that should be on the final board
# output:
#     - a generator of boards, deriving from board, adding a minimal number of obj1 and obj2 to ensure that 
#       this rule cannot be broken no matter what is added to the board, with no overlapping or duplicate
#       boards

# Testing Strategy:
#     - partition: qualifier - every, at least one, none
#     - partition: board - empty, not empty
#     - partition: board - contains obj1, does not contain obj1
#     - partition: board - contains obj2, does not contain obj2
#     - partition: board - contains other objects, does not contain other objects
#     - partition: board - valid, invalid
#     - partition: output length - 0, > 0

# qualifier - every, board - empty, output length - 0
def test_fill_board_every_empty_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board([None, None, None]), {"A": 1, "B": 1})), [])

# qualifier - every, board - empty, output length > 0
def test_fill_board_every_empty_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board([None, None, None, None]), {"A": 1, "B": 1})), [
            Board(["A", None, "B", None]),
            Board([None, "A", None, "B"]),
            Board(["B", None, "A", None]),
            Board([None, "B", None, "A"])])

# qualifier - every, board - contains obj1, board - invalid
def test_fill_board_every_on_obj1_invalid():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["A", None, None, "A", None, None]), {"A": 2, "B": 2})), [])

# qualifier - every, board - contains obj1, output length > 0
def test_fill_board_every_on_obj1_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board([None, "A", None, None, None, None]), {"A": 2, "B": 3})), [
            Board(["A", "A", None, "B", "B", None]),
            Board([None, "A", "A", None, "B", "B"]),
            Board(["B", "A", None, "A", "B", None]),
            Board([None, "A", "B", None, "B", "A"])])

# qualifier - every, board - contains obj2, output length = 0
def test_fill_board_every_on_obj2_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board([None, "B", None, None, None, "B", None, None]), {"A": 1, "B": 2})), [])

# qualifier - every, board - contains obj2, output length > 0
def test_fill_board_every_on_obj2_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["B", None, None, None, None, None]), {"A": 2, "B": 3})), [
            Board(["B", "A", "A", None, "B", "B"]),
            Board(["B", "A", None, "A", "B", None]),
            Board(["B", "A", "B", None, "B", "A"]),
            Board(["B", None, "A", "A", None, "B"]),
            Board(["B", "B", "A", None, "A", "B"]),
            Board(["B", "B", None, "A", "A", None]),
            Board(["B", None, "B", "A", None, "A"]),
            Board(["B", "B", "B", None, "A", "A"])])

# qualifier - every, board - contains other objects, output length = 0
def test_fill_board_every_on_others_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board([None, "C", "D", "E", "C", None]), {"A": 1, "B": 1})), [])

# qualifier - every, board - contains other objects, output length > 0
def test_fill_board_every_on_others_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["C", "D", None, None, None, None]), {"A": 1, "B": 2})), [
            Board(["C", "D", "A", None, None, "B"]),
            Board(["C", "D", "B", None, None, "A"])])

# qualifier - every, board - contains obj1 & others, board - invalid
def test_fill_board_every_on_obj1_and_others_invalid():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["A", "C", None, "C", None, "D"]), {"A": 1, "B": 1})), [])

# qualifier - every, board - contains obj1 & others, output length = 0
def test_fill_board_every_on_obj1_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["A", "C", None, None, None, "D"]), {"A": 2, "B": 2})), [])

# qualifier - every, board - contains obj1 & others, output length > 0
def test_fill_board_every_on_obj1_and_others_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["A", None, "C", None, None, "D", None, None]), {"A": 2, "B": 2})), [
            Board(["A", None, "C", "A", "B", "D", None, "B"]),
            Board(["A", None, "C", "B", "B", "D", None, "A"])])

# qualifier - every, board - contains obj2 & others, output length = 0
def test_fill_board_every_on_obj2_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["B", None, None, "C", "D", None]), {"A": 1, "B": 1})), [])

# qualifier - every, board - contains obj2 & others, output length > 0
def test_fill_board_every_on_obj2_and_others_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board([None, "B", None, None, "C", None, None, "D"]), {"A": 1, "B": 2})), [
            Board([None, "B", "A", None, "C", None, "B", "D"]),
            Board([None, "B", None, None, "C", "A", None, "D"]),
            Board([None, "B", "B", None, "C", None, "A", "D"])])
    
# qualifier - every, board - contains obj1 & obj2, board - invalid
def test_fill_board_every_on_both_invalid():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["A", None, "B", "A", None, None]), {"A": 2, "B": 2})), [])

# qualifier - every, board - contains obj1 & obj2, output length = 0
def test_fill_board_every_on_both_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["A", None, "B", None, None, "B"]), {"A": 2, "B": 2})), [])

# qualifier - every, board - contains obj1 & obj2, output length > 0
def test_fill_board_every_on_both_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["A", None, None, None, None, "B", None, None]), {"A": 2, "B": 3})), [
            Board(["A", "A", None, None, "B", "B", None, None]),
            Board(["A", None, "A", None, "B", "B", "B", None]),
            Board(["A", None, None, "A", "B", "B", None, "B"]),
            Board(["A", None, "B", None, "B", "B", "A", None]),
            Board(["A", None, None, "B", "B", "B", None, "A"])])

# qualifier - every, board - contains obj1 & obj2 & others, board - invalid
def test_fill_board_every_on_both_and_others_invalid():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["A", "B", None, "C", None, None]), {"A": 1, "B": 2})), [])

# qualifier - every, board - contains obj1 & obj2 & others, output length = 0
def test_fill_board_every_on_both_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["A", "B", None, "D", None, None, "C", None]), {"A": 3, "B": 3})), [])

# qualifier - every, board - contains obj1 & obj2 & others, output length > 0
def test_fill_board_every_on_both_and_others_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.EVERY).fill_board(
            Board(["C", None, "A", None, "B", None]), {"A": 2, "B": 2})), [
            Board(["C", "A", "A", None, "B", "B"])])

# qualifier - at least one, board - empty, output length = 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_empty_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, None, None]), {"A": 1, "B": 1})), [])

# qualifier - at least one, board - empty, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_empty_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, None, None, None, None, None]), {"A": 1, "B": 2})), rotate_boards([
            Board(["A", None, None, "B", None, None])]))
        
# qualifier - at least one, board - contains obj1, output length = 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_obj1_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board(["A", None, "A", None]), {"A": 2, "B": 2})), [])

# qualifier - at least one, board - contains obj1, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_obj1_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, "A", None, None, None, None]), {"A": 2, "B": 2})), [
            Board([None, "A", None, None, "B", None]),
            Board(["A", "A", None, "B", None, None]),
            Board([None, "A", "A", None, None, "B"]),
            Board(["B", "A", None, "A", None, None]),
            Board([None, "A", "B", None, None, "A"])])

# qualifier - at least one, board - contains obj2, output length = 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_obj2_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board(["B", None, "B", None]), {"A": 1, "B": 2})), [])

# qualifier - at least one, board - contains obj2, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_obj2_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, None, None, None, None, "B"]), {"A": 2, "B": 2})), [
            Board(["A", None, None, "B", None, "B"]),
            Board([None, "A", None, None, "B", "B"]),
            Board([None, None, "A", None, None, "B"]),
            Board(["B", None, None, "A", None, "B"]),
            Board([None, "B", None, None, "A", "B"])])

# qualifier - at least one, board - contains other objects, output length = 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_others_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board(["C", "D", None, None, "D", "D"]), {"A": 1, "B": 1})), [])

# qualifier - at least one, board - contains other objects, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_others_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board(["C", None, None, None, None, "D"]), {"A": 1, "B": 1})), [
            Board(["C", "A", None, None, "B", "D"]),
            Board(["C", "B", None, None, "A", "D"])])

# qualifier - at least one, board - contains obj1 & others, output length = 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_obj1_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board([None, "A", None, None, "C", None]), {"A": 1, "B": 2})), [])

# qualifier - at least one, board - contains obj1 & others, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_obj1_and_others_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board(["A", None, None, None, None, "D", None, None]), {"A": 2, "B": 2})), [
            Board(["A", None, None, None, "B", "D", None, None]),
            Board(["A", None, "A", None, None, "D", "B", None]),
            Board(["A", None, None, "A", None, "D", None, "B"]),
            Board(["A", None, "B", None, None, "D", "A", None]),
            Board(["A", None, None, "B", None, "D", None, "A"])])

# qualifier - at least one, board - contains obj2 & others, output length = 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_obj2_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board(["B", "C", None, "B", None, "D"]), {"A": 1, "B": 3})), [])

# qualifier - at least one, board - contains obj2 & others, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_obj2_and_others_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board(["D", "E", "B", None, None, None, None, None]), {"A": 2, "B": 2})), [
            Board(["D", "E", "B", "A", None, None, None, "B"]),
            Board(["D", "E", "B", None, None, None, "A", None]),
            Board(["D", "E", "B", "B", None, None, None, "A"])])

# qualifier - at least one, board - contains obj1 & obj2, output length = 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_both_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board(["A", "B", None, None, "B", None]), {"A": 2, "B": 2})), [])

# qualifier - at least one, board - contains obj1 & obj2, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_both_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board(["B", None, "A", None, None, None, None, None]), {"A": 3, "B": 4})), [
            Board(["B", "A", "A", None, None, "B", None, None]),
            Board(["B", None, "A", None, None, None, "B", None]),
            Board(["B", None, "A", "A", None, None, None, "B"]),
            Board(["B", None, "A", None, "A", None, None, None]),
            Board(["B", "B", "A", None, None, "A", None, None]),
            Board(["B", None, "A", "B", None, None, None, "A"])])

# qualifier - at least one, board - contains obj1 & obj2 & others, output length = 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_both_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board(["C", "B", "A", None, None, "B", "A", "D"]), {"A": 3, "B": 3})), [])

# qualifier - at least one, board - contains obj1 & obj2 & others, output length > 0
@pytest.mark.skip("Not implemented yet")
def test_fill_board_at_least_one_on_both_and_others_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.AT_LEAST_ONE).fill_board(
            Board(["D", "B", "B", "A", None, None, None, None]), {"A": 2, "B": 3})), [
            Board(["D", "B", "B", "A", None, None, None, "B"]),
            Board(["D", "B", "B", "A", None, "A", None, None]),
            Board(["D", "B", "B", "A", None, None, "A", None])])

# qualifier - none, board - empty, output length = 0
def test_fill_board_none_on_empty_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, None]), {"A": 1, "B": 1})), [])

# qualifier - none, board - empty, output length > 0
def test_fill_board_none_on_empty_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, None, None, None, None, None]), {"A": 2, "B": 2})), [
            Board(["A", "A", "B", None, None, "B"]),
            Board(["A", "B", "A", None, "B", None]),
            Board(["A", "B", "B", "A", None, None]),
            Board(["A", "B", None, "A", "B", None]),
            Board(["A", "B", None, "A", None, "B"]),
            Board(["A", None, "B", "A", "B", None]),
            Board(["A", None, "B", "A", None, "B"]),
            Board(["A", None, None, "A", "B", "B"]),
            Board(["A", None, "B", None, "A", "B"]),
            Board(["A", "B", None, None, "B", "A"]),
            Board(["B", "A", "A", "B", None, None]),
            Board([None, "A", "B", "A", None, "B"]),
            Board(["B", "A", "B", None, "A", None]),
            Board(["B", "A", None, "B", "A", None]),
            Board(["B", "A", None, None, "A", "B"]),
            Board([None, "A", "B", "B", "A", None]),
            Board([None, "A", "B", None, "A", "B"]),
            Board([None, "A", None, "B", "A", "B"]),
            Board(["B", "A", None, "B", None, "A"]),
            Board([None, "B", "A", "A", "B", None]),
            Board(["B", None, "A", "B", "A", None]),
            Board(["B", "B", "A", None, None, "A"]),
            Board(["B", None, "A", "B", None, "A"]),
            Board(["B", None, "A", None, "B", "A"]),
            Board([None, "B", "A", "B", None, "A"]),
            Board([None, "B", "A", None, "B", "A"]),
            Board([None, None, "A", "B", "B", "A"]),
            Board([None, None, "B", "A", "A", "B"]),
            Board([None, "B", None, "A", "B", "A"]),
            Board(["B", None, None, "B", "A", "A"])])

# qualifier - none, board - contains obj1, output length = 0
def test_fill_board_none_on_obj1_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["A", None, None, "A"]), {"A": 2, "B": 1})), [])

# qualifier - none, board - contains obj1, output length > 0
def test_fill_board_none_on_obj1_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["A", None, None, None, None, None]), {"A": 2, "B": 1})), [
            Board(["A", "A", "B", None, None, None]),
            Board(["A", "A", None, None, None, "B"]),
            Board(["A", "B", "A", None, None, None]),
            Board(["A", None, "A", None, "B", None]),
            Board(["A", "B", None, "A", None, None]),
            Board(["A", None, "B", "A", None, None]),
            Board(["A", None, None, "A", "B", None]),
            Board(["A", None, None, "A", None, "B"]),
            Board(["A", None, "B", None, "A", None]),
            Board(["A", None, None, None, "A", "B"]),
            Board(["A", "B", None, None, None, "A"]),
            Board(["A", None, None, None, "B", "A"])])

# qualifier - none, board - contains obj2, output length = 0
def test_fill_board_none_on_obj2_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["B", None, "B", None, "B", None]), {"A": 1, "B": 3})), [])

# qualifier - none, board - contains obj2, output length > 0
def test_fill_board_none_on_obj2_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, None, "B", None, None, None]), {"A": 2, "B": 1})), [
            Board(["A", "A", "B", None, None, None]),
            Board(["A", None, "B", "A", None, None]),
            Board(["A", None, "B", None, "A", None]),
            Board([None, "A", "B", "A", None, None]),
            Board([None, "A", "B", None, "A", None]),
            Board([None, None, "B", "A", "A", None])])

# qualifier - none, board - contains other objects, output length = 0
def test_fill_board_none_on_other_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, "C", "D", None, "E", "D"]), {"A": 1, "B": 1})), [])

# qualifier - none, board - contains other objects, output length > 0
def test_fill_board_none_on_other_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, None, "C", None, None, "D"]), {"A": 1, "B": 1})), [
            Board(["A", "B", "C", None, None, "D"]),
            Board(["A", None, "C", None, "B", "D"]),
            Board([None, "A", "C", "B", None, "D"]),
            Board([None, None, "C", "A", "B", "D"]),
            Board(["B", "A", "C", None, None, "D"]),
            Board(["B", None, "C", None, "A", "D"]),
            Board([None, "B", "C", "A", None, "D"]),
            Board([None, None, "C", "B", "A", "D"])])

# qualifier - none, board - contains obj1 & others, output length = 0
def test_fill_board_none_on_obj1_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, "C", "A", "A", "E", "D", None, None]), {"A": 2, "B": 2})), [])

# qualifier - none, board - contains obj1 & others, output length > 0
def test_fill_board_none_on_obj1_and_others_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["D", "A", None, None, None, None, "C", None]), {"A": 2, "B": 1})), [
            Board(["D", "A", "A", "B", None, None, "C", None]),
            Board(["D", "A", "A", None, "B", None, "C", None]),
            Board(["D", "A", "A", None, None, None, "C", "B"]),
            Board(["D", "A", None, "A", "B", None, "C", None]),
            Board(["D", "A", None, None, "A", None, "C", "B"]),
            Board(["D", "A", None, None, None, "A", "C", "B"]),
            Board(["D", "A", "B", "A", None, None, "C", None]),
            Board(["D", "A", "B", None, "A", None, "C", None]),
            Board(["D", "A", "B", None, None, "A", "C", None]),
            Board(["D", "A", "B", None, None, None, "C", "A"]),
            Board(["D", "A", None, "B", "A", None, "C", None]),
            Board(["D", "A", None, "B", None, "A", "C", None]),
            Board(["D", "A", None, None, "B", "A", "C", None]),
            Board(["D", "A", None, None, "B", None, "C", "A"])])

# qualifier - none, board - contains obj2 & others, output length = 0
def test_fill_board_none_on_obj2_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["C", "B", "B", None, None, None]), {"A": 2, "B": 2})), [])

# qualifier - none, board - contains obj2 & others, output length > 0
def test_fill_board_none_on_obj2_and_others_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["B", None, "C", None, None, "D"]), {"A": 1, "B": 1})), [
            Board(["B", "A", "C", None, None, "D"]),
            Board(["B", None, "C", None, "A", "D"])])

# qualifier - none, board - contains obj1 & obj2, board invalid
def test_fill_board_none_on_both_invalid():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, "A", None, "A", None, "B", "B", None]), {"A": 3, "B": 2})), [])

# qualifier - none, board - contains obj1 & obj2, output length = 0
def test_fill_board_none_on_both_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, "A", "A", None, "B", None, None, "B"]), {"A": 5, "B": 3})), [])

# qualifier - none, board - contains obj1 & obj2, output length > 0
def test_fill_board_none_on_both_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["A", None, None, None, "B", None]), {"A": 2, "B": 1})), [
            Board(["A", None, "A", None, "B", None]),
            Board(["A", None, None, "A", "B", None]),
            Board(["A", None, None, None, "B", "A"])])

# qualifier - none, board - contains obj1 & obj2 & others, board invalid
def test_fill_board_none_on_both_and_others_invalid():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, "C", "B", None, None, "A"]), {"A": 2, "B": 1})), [])

# qualifier - none, board - contains obj1 & obj2 & others, output length = 0
def test_fill_board_none_on_both_and_others_no_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board(["A", None, "B", "C", None, "D", "E", "E"]), {"A": 1, "B": 3})), [])

# qualifier - none, board - contains obj1 & obj2 & others, output length > 0
def test_fill_board_none_on_both_and_others_some_solutions():
    compare_unordered_list_of_boards(
        list(OppositeRule("A", "B", RuleQualifier.NONE).fill_board(
            Board([None, "B", "C", "A", None, None, "D", None]), {"A": 2, "B": 2})), [
            Board(["A", "B", "C", "A", None, "B", "D", None]),
            Board([None, "B", "C", "A", "A", "B", "D", None]),
            Board(["B", "B", "C", "A", None, None, "D", "A"]),
            Board([None, "B", "C", "A", "B", None, "D", "A"]),
            Board([None, "B", "C", "A", None, "B", "D", "A"])])