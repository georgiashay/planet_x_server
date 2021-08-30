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