import itertools
import random
import json
from enum import Enum
from abc import *
from math import comb, factorial

from .utilities import permutations_multi, add_two_no_touch, fill_no_within, add_one_no_self_touch, calc_partitions, ordered_partitions, cartesian_product_sets_unique, cartesian_product_sets_no_supersets
from .board import *

MUST_ELIMINATE = False

class RuleQualifier(Enum):
    """
    Represents a qualifier for the number of objects that follow a rule.
    I.e. whether no objects, at least one of the type of object, or every one of 
    a type of object follow a particular type of rjle
    """
    NONE = 0
    AT_LEAST_ONE = 1
    EVERY = 2
    
    def __str__(self):
        if self is RuleQualifier.NONE:
            return "No"
        elif self is RuleQualifier.AT_LEAST_ONE:
            return "At least one"
        elif self is RuleQualifier.EVERY:
            return "Every"
    
    def for_object(self, obj, num_object):
        """
        Returns a string representing this qualifier for a specific object
            e.g. "No gas cloud is" or "At least one asteroid is" or "Every comet is not"
        
        obj: The space object 
        num_object: How many of this space object are on the board
        """
        if self is RuleQualifier.NONE:
            if num_object == 1:
                return obj.singular()[:1].upper() + obj.singular()[1:] + " is not"
            else:
                return "No " + obj.name()+ " is"
        elif self is RuleQualifier.AT_LEAST_ONE:
            return "At least one " + obj.name() + " is"
        elif self is RuleQualifier.EVERY:
            if num_object == 1:
                return obj.singular()[:1].upper() + obj.singular()[1:] + " is"
            else:
                return "Every " + obj.name() + " is"  
            
    def code(self):
        """
        A compact string representation of this qualifier
        """
        if self is RuleQualifier.NONE:
            return "N"
        elif self is RuleQualifier.AT_LEAST_ONE:
            return "A"
        elif self is RuleQualifier.EVERY:
            return "E"
        
    @classmethod
    def parse(cls, s):
        """
        Returns a qualifier parsed from its compact string representation
        """
        if s == "N":
            return RuleQualifier.NONE
        elif s == "A":
            return RuleQualifier.AT_LEAST_ONE
        elif s == "E":
            return RuleQualifier.EVERY
    
    def to_json(self):
        """
        Returns a readable string version of this qualifier for use in a 
        json object
        """
        if self is RuleQualifier.NONE:
            return "NONE"
        elif self is RuleQualifier.AT_LEAST_ONE:
            return "AT_LEAST_ONE"
        elif self is RuleQualifier.EVERY:
            return "EVERY"

class Precision(Enum):
    """
    Represents a qualifier for how strictly the objects follow a rule.
    
    STRICT = the objects follow the rule at an exact number
    WITHIN = the objects fall within the bounds of the rule
    """
    STRICT = 0
    WITHIN = 1
    
    def __str__(self):
        if self is Precision.STRICT:
            return "exactly"
        elif self is Precision.WITHIN:
            return "at most" 
            
    def code(self):
        """
        A compact string representation of this qualifier
        """
        if self is Precision.STRICT:
            return "S"
        elif self is Precision.WITHIN:
            return "W"
        
    @classmethod
    def parse(cls, s):
        """
        Returns a qualifier parsed from its compact string representation
        """
        if s == "S":
            return Precision.STRICT
        elif s == "W":
            return Precision.WITHIN
    
    def to_json(self):
        """
        Returns a readable string version of this qualifier for use in a 
        json object
        """
        if self is Precision.STRICT:
            return "STRICT"
        elif self is Precision.WITHIN:
            return "WITHIN"
        
class Rule(ABC):
    @abstractmethod
    def is_satisfied(self, board):
        """
        Checks whether a board meets this constraint. Returns true if constraint is met.
        """
        pass
    
    @abstractmethod
    def is_immediately_limiting(self):
        """
        Returns true if this constraint limits the positions the space object can be in
        even when no objects are on the board.
        """
        pass

    @abstractmethod
    def disallowed_sectors(self):
        """
        If the constraint is immediately limited, returns the list of sector that the 
        space object relevant to the constraint is not allowed to be in. Otherwise,
        returns [].
        """
        return []
    
    @abstractmethod
    def fill_board(self, board, num_objects):
        """
        Given a board and the number of each space object that must appear on it,
        fills the board in all ways possible given this constraint.
        
        board: A partially filled Board
        num_objects: A dictionary mapping space objects to the number of times they
            are supposed to appear in the board.
            
        Returns: a list of boards that contain the same objects as the original board,
            plus filling in objects to meet this constraint. Returns all possible
            such boards.
        """
        pass
    
    @abstractmethod
    def affects(self):
        """
        Returns a list of space objects that are affected by this rule. Note that this is
        not the same as all of the space objects named in the constraint - e.g.
            "All gas clouds are next to an empty sector" does not affect empty sectors,
            since the other empty sectors may be wherever they like
        """
        pass
    
    @abstractmethod
    def completes(self):
        """
        Returns a list of all space object that this constraint can "complete" - that is, 
        when generating all possible boards using fill_board, this constraint will add in 
        every object of that type.
        """
        pass
    
    @abstractmethod
    def adds(self):
        """
        Returns a list of all space objects that can be added during fill_board
        """
        pass
    
    @abstractmethod
    def space_objects(self):
        """
        Returns all the space objects involved in this rule
        """
        pass
    
    @abstractmethod
    def allowed_rule(self, num_objects, constraints, other_rules):
        """
        Returns true if this rule is allowed to be included in research given
        a set of constraints and other rules
        """
        pass
        
    @classmethod
    @abstractmethod
    def generate_rule(cls, board, constraints, other_rules, *space_objects):
        """
        Generates a rule of this type for a particular board and space objects to relate 
        to each other. Returns None if no such rule exists, or if such a rule would be 
        redundant with the given constraints or other rules
        """
        pass
    
    @abstractmethod
    def real_strength(self, board, constraints):
        """
        Returns a numerical value 0-1 representing the strength of the rule based on 
        what combinations of object positions are eliminated. For a RelationRule, this
        is based on what object positions are eliminated given the positions of all 
        space_object2. Takes constraints into account.
        """
        pass
            
    @abstractmethod
    def base_strength(self, board):
        """
        Returns a numerical value 0-1 representing the strength of the rule based on 
        what combinations of object positions are eliminated. For a RelationRule, this
        is based on what object positions are eliminated given the positions of all 
        space_object2.
        """
        pass
    
    @abstractmethod
    def code(self):
        """
        Return compressed string code that represents this rule
        """
        pass
    
    @classmethod
    @abstractmethod
    def parse(cls, s):
        """
        Parse a compressed string representation s into a rule of this type
        """
        pass
    
    @abstractmethod
    def text(self, board):
        """
        Returns a readable text version of this rule given an input Board board.
        """
        pass
    
    @abstractmethod
    def to_json(self, board):
        """
        Create a json representation of this rule, given a particular board. The json
        representation should have the following fields:
            - ruleType: type of the rule
            - If the rule is a self-rule:
                - spaceObject: the space object in the rule
            - If the rule is a relation-rule:
                - spaceObject1: the space object in the rule
                - spaceObject2: the space object which spaceObject1 is related to in the rule
            - categoryName: the name of the category the rule is in (based on types of objects)
            - text: a readable text representation of the rule
            - other rule-specific fields   
        """
        pass

    @classmethod
    def parse(cls, rule_str):
        """
        Parses a rule string into a rule. The first character of the
        rule string determines what type of rule it is.
        """
        if rule_str[0] == "B":
            return BandRule.parse(rule_str)
        elif rule_str[0] == "O":
            return OppositeRule.parse(rule_str)
        elif rule_str[0] == "S":
            return OppositeSelfRule.parse(rule_str)
        elif rule_str[0] == "A":
            return AdjacentRule.parse(rule_str)
        elif rule_str[0] == "C":
            return AdjacentSelfRule.parse(rule_str)
        elif rule_str[0] == "W":
            return WithinRule.parse(rule_str)
        elif rule_str[0] == "P":
            return SectorsRule.parse(rule_str)
        
    def category_name(self):
        """
        Returns the category name for the rule, e.g. "Gas Clouds & Asteroids"
        """
        objs = self.space_objects()
        if objs[-1] is SpaceObject.Empty:
            objs = objs[:-1]
        obj_titles = [obj.category() for obj in objs]
        return " & ".join(obj_titles)
    
    def __hash__(self):
        return hash(self.code())
    
    @classmethod
    def rule_types_allowed(cls, num_objects, space_objects, rules, rule_type, self_rule_type, spots_per_obj):
        num_spots_uncovered = [spots_per_obj * num_objects[obj] for obj in space_objects]
        has_none_rule = [False] * len(space_objects)
        
        for rule in rules:
            if isinstance(rule, rule_type) or isinstance(rule, self_rule_type):
                shared_objects = set(rule.space_objects()) & set(space_objects)
                
                if set(rule.space_objects()) - {SpaceObject.Empty} == set(space_objects) - {SpaceObject.Empty}:
                    return False, False, False
                
                if len(shared_objects) > 0:
                    if rule.qualifier is RuleQualifier.NONE:
                        for i, obj in enumerate(space_objects):
                            if obj in shared_objects:
                                has_none_rule[i] = True
                    elif rule.qualifier is RuleQualifier.EVERY:
                        for i, obj in enumerate(space_objects):
                            if obj in shared_objects:
                                num_spots_uncovered[i] -= num_objects[rule.space_objects()[0]]
                    elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                        for i, obj in enumerate(space_objects):
                            if obj in shared_objects:
                                if isinstance(rule, rule_type):
                                    num_spots_uncovered[i] -= 1
                                else:
                                    num_spots_uncovered[i] -= 2
                                    
        allowed_none_rule = True
        allowed_at_least_one_rule = True
        allowed_every_rule = True
        
        for i, spots_uncovered in enumerate(num_spots_uncovered):
            if spots_uncovered == 0:
                allowed_none_rule = False
                
            every_increase = num_objects[space_objects[0]]
            if spots_uncovered < every_increase or (spots_uncovered == every_increase and has_none_rule[i]):
                allowed_every_rule = False
                
            if cls == rule_type:
                at_least_one_increase = 1
            elif cls == self_rule_type:
                at_least_one_increase = 2
                                
            if spots_uncovered < at_least_one_increase or (spots_uncovered == at_least_one_increase and has_none_rule[i]):
                allowed_at_least_one_rule = False
            
        return allowed_none_rule, allowed_at_least_one_rule, allowed_every_rule


class RelationRule(Rule):
    def space_objects(self):
        return [self.space_object1, self.space_object2]
    
    @classmethod
    @abstractmethod
    def eliminate_sectors(cls, board, constraints, data, space_object1, space_object2):
        """
        Create a rule that will eliminate possible positions of space_object1, where 
        space_object1 and data.elimination_object are ambiguous on survey/target
        
        Only the sectors in data.need_eliminated are ambiguous, and the sectors in 
        data.already_eliminated have been eliminated by other rules. To be viable,
        this rule must eliminate at least data.minimum sectors, and if possible 
        should eliminate data.goal sectors.
        """
        pass    
    
    @abstractmethod
    def positive_positions(self, board):
        """
        List of indices in board that follow this relation positively with respect to 
        the positions of object2. I.E., positions where object1 could be if the 
        qualifier was EVERY
        """
        pass
        
    def real_strength(self, board, constraints):
        # Constraints relevant to this rule
        relevant_constraints = [constraint for constraint in constraints if 
                                (isinstance(constraint, SelfRule) and constraint.space_object is self.space_object1)
                                or (isinstance(constraint, RelationRule) and 
                                    set(constraint.space_objects()) == set(self.space_objects()))]
                
        
        # Only consider the positions of space object 2
        base_board = Board([obj if obj is self.space_object2 else None for obj in board])
        # Build up all possible boards given the relevant constraints and positions of space object 2
        boards = [base_board]
        for constraint in relevant_constraints:
            next_boards = []
            for b in boards:
                next_boards.extend(constraint.fill_board(b, board.num_objects()))
            boards = next_boards
            
        next_boards = []
        for b in boards:
            # Collect remaining objects
            try:
                new_num_obj1 = b.num_objects()[self.space_object1]
            except KeyError:
                new_num_obj1 = 0 
            num_obj1 = board.num_objects()[self.space_object1] - new_num_obj1
            num_none = len(board) - board.num_objects()[self.space_object1] - board.num_objects()[self.space_object2]
            # Create all permutations of remaining objects to put in the board
            perms = permutations_multi({self.space_object1: num_obj1, None: num_none})

            for perm in perms:
                board_copy = b.copy()
                j = 0
                # Fill in board with this permutation of board objects
                for k, obj in enumerate(b):
                    if b[k] is None:
                        board_copy[k] = perm[j]
                        j += 1
                next_boards.append(board_copy)
        boards = next_boards
            
        # Count number of possible boards
        num_total_combos = len(boards)
        # Count number of possible boards that also follow this rule
        valid_boards = [b for b in boards if self.is_satisfied(b)]
        num_valid_combos = len(valid_boards)
        
        if num_total_combos == 1:
            return 0
        
        # Strength depends on how many combinations were eliminated
        return (num_total_combos - num_valid_combos)/(num_total_combos - 1)
    
    def base_strength(self, board):
        num_object1 = board.num_objects()[self.space_object1]
        num_object2 = board.num_objects()[self.space_object2]
        
        # Number of positions space object 1 could be in 
        num_positions = len(board) - num_object2
        # Number of positions space object 1 could be in given this rule with an "every" qualifier
        num_positive_positions = len(self.positive_positions(board))
                
        # Number of combinations of positions for object 1
        total_combos = comb(num_positions, num_object1)
        
        # Determine strength based on 
        if self.qualifier is RuleQualifier.NONE:
            valid_combos = comb(num_positions - num_positive_positions, num_object1)
            invalid_combos = total_combos - valid_combos
            if total_combos > 1:
                return invalid_combos/(total_combos - 1)
            else:
                return 0
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            invalid_combos = comb(num_positions - num_positive_positions, num_object1)
            if total_combos > 1:
                return invalid_combos/(total_combos - 1)
            else:
                return 0
        elif self.qualifier is RuleQualifier.EVERY:
            valid_combos = comb(num_positive_positions, num_object1)
            invalid_combos = total_combos - valid_combos
            if total_combos > 1:
                return invalid_combos/(total_combos - 1)
            else:
                return 0
        
        
class SelfRule(Rule):
    def space_objects(self):
        return [self.space_object]
    
    def real_strength(self, board, constraints):
        # Consider constraints relevant to this rule
        relevant_constraints = [constraint for constraint in constraints if 
                                (isinstance(constraint, SelfRule) and constraint.space_object is self.space_object)]
        
        # Build up all possible boards with this object
        base_board = Board([None] * len(board))
        boards = [base_board]
        for constraint in relevant_constraints:
            next_boards = []
            for b in boards:
                next_boards.extend(constraint.fill_board(b, board.num_objects()))
            boards = next_boards
            
        next_boards = []
        for b in boards:
            # Collect remaining objects
            try:
                new_num_obj = b.num_objects()[self.space_object]
            except KeyError:
                new_num_obj = 0 
            num_obj = board.num_objects()[self.space_object] - new_num_obj
            num_none = len(board) - board.num_objects()[self.space_object]
            # Create all permutations of remaining objects to put in the board
            perms = permutations_multi({self.space_object: num_obj, None: num_none})

            for perm in perms:
                board_copy = b.copy()
                j = 0
                # Fill in board with this permutation of board objects
                for k, obj in enumerate(b):
                    if b[k] is None:
                        board_copy[k] = perm[j]
                        j += 1
                next_boards.append(board_copy)
        boards = next_boards 
        
        # Determine how many of these boards are valid considering this rule
        num_total_combos = len(boards)
        valid_boards = [b for b in boards if self.is_satisfied(b)]
        num_valid_combos = len(valid_boards)
        
        if num_total_combos == 1:
            return 0
        
        # Assign a strength based on how many combinations were eliminated
        return (num_total_combos - num_valid_combos)/(num_total_combos - 1)
        
class AdjacentRule(RelationRule):
    """
    A rule stating that two objects are or aren't adjacent to one another
    """
    def __init__(self, space_object1, space_object2, qualifier):
        self.space_object1 = space_object1
        self.space_object2 = space_object2
        self.qualifier = qualifier
        
    def __repr__(self):
        return "<" + self.qualifier.name + " " + repr(self.space_object1) + " adjacent to " \
                + repr(self.space_object2) + ">"
    
    def __str__(self):
        return str(self.qualifier) + " " + self.space_object1.name() + " is adjacent to " + \
                self.space_object2.one() + " " + self.space_object2.name() + "."
    
    def text(self, board):
        num_object1 = board.num_objects()[self.space_object1]
        num_object2 = board.num_objects()[self.space_object2]
        return self.qualifier.for_object(self.space_object1, num_object1) + " adjacent to " + \
                self.space_object2.any_of(num_object2) + "."
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.qualifier == other.qualifier:
                if self.qualifier is RuleQualifier.NONE or self.qualifier is RuleQualifier.AT_LEAST_ONE:
                    # Mutual rules - i.e. space objects can be swapped
                    return self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2 or \
                            self.space_object1 == other.space_object2 and self.space_object2 == other.space_object1
                else:
                    # One way rules - i.e. space objects cannot be swapped
                    return self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2
            else:
                return False
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self.space_object1) + hash(self.space_object2) + hash(self.qualifier)
    
    def is_satisfied(self, board):
        if self.qualifier is RuleQualifier.NONE:
            return not any(board[i] is self.space_object1 and \
                           (board[i-1] is self.space_object2 or board[i+1] is self.space_object2) \
                           for i in range(len(board)))
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return any(board[i] is self.space_object1 and \
                           (board[i-1] is self.space_object2 or board[i+1] is self.space_object2) \
                           for i in range(len(board)))
        else:
            return all(board[i] is not self.space_object1 or \
                       (board[i-1] is self.space_object2 or board[i+1] is self.space_object2) \
                       for i in range(len(board)))
    
    def is_immediately_limiting(self):
        return False

    def disallowed_sectors(self):
        return []
    
    def _fill_board_none(self, board, num_objects):
        num_obj1 = num_objects[self.space_object1]
        num_obj2 = num_objects[self.space_object2]
        
        for i, obj in enumerate(board):
            if obj is self.space_object1:
                if board[i-1] is self.space_object2 or board[i+1] is self.space_object2:
                    # There are already two adjacent on this board, cannot meet rule
                    return []
                num_obj1 -= 1
            elif obj is self.space_object2:
                num_obj2 -= 1

        yield from add_two_no_touch(self.space_object1, self.space_object2, num_obj1, num_obj2, board.copy())    
    
    def _fill_board_every(self, original_board, board, num_obj1, num_obj1_left, num_obj2_left, start_i=0):
        # num_objects: how many should be on the board starting from start_i
        # num_objects_left: how many still need to be placed
        if num_obj1 == 0:
            return [ board ]
        
        new_boards = []
        for i in range(start_i, len(board)):
            obj = board[i]
            is_obj1 = obj is self.space_object1
            # Attempt to fill each position with an object1 if possible
            if obj is None or is_obj1:
                options = 0
                if is_obj1 or num_obj1_left > 0:
                    if board[i-1] is self.space_object2 or board[i+1] is self.space_object2:
                        options += 1
                        # If there is already an obj2 next to it, fill with obj1 and proceed
                        board_copy = board.copy()
                        board_copy[i] = self.space_object1
                        new_boards.extend(self._fill_board_every(original_board, board_copy, num_obj1 - 1, \
                                                                 num_obj1_left - (not is_obj1), num_obj2_left, i+1))
                    elif num_obj2_left > 0:
                        # Otherwise there must be obj2 left to use
                        if board[i-1] is None and (board[i-2] is not self.space_object1 or original_board[i-3] is self.space_object2):
                            # Do not put an obj2 on the left if there is a obj1
                            # already to the left of that, to avoid duplicate boards
                            options += 1
                            board_copy = board.copy()
                            board_copy[i] = self.space_object1
                            board_copy[i-1] = self.space_object2
                            new_boards.extend(self._fill_board_every(original_board, board_copy, num_obj1 - 1, \
                                                                     num_obj1_left - (not is_obj1), num_obj2_left - 1, i+1))
                    
                        if board[i+1] is None and (board[i+2] is not self.space_object1 or original_board[i+3] is self.space_object2):
                            # Do not put an obj2 on the right if there is a obj1
                            # to the right of that, to avoid duplicate boards
                            options += 1
                            board_copy = board.copy()
                            board_copy[i] = self.space_object1
                            board_copy[i+1] = self.space_object2
                            new_boards.extend(self._fill_board_every(original_board, board_copy, num_obj1 - 1, \
                                                                     num_obj1_left - (not is_obj1), num_obj2_left - 1, i+2))

                if is_obj1 and options == 0:
                    # Unable to place an obj2 next to an existing obj1
                    return []
            
        return new_boards
    
    def _prepare_board_every(self, board, num_obj2, lone):
        obj2_spots = []
        n = len(board)
        
        for i in lone:
            current_spots = set()
            if board[i-1] is None or board[i-1] is self.space_object2:
                current_spots.add(((i-1) + n)%n)
            if board[i+1] is None or board[i+1] is self.space_object2:
                current_spots.add((i+1)%n)
            obj2_spots.append(current_spots)
                    
        for obj2_indices in cartesian_product_sets_unique(obj2_spots):
            num_obj2_left = num_obj2
            board_copy = board.copy()
            for i in obj2_indices:
                num_obj2_left -= (board_copy[i] is not self.space_object2)
                board_copy[i] = self.space_object2
            if num_obj2_left >= 0:
                yield (num_obj2_left, board_copy)
                
    def _add_obj1_every(self, board, num_obj1, i=0):
        if num_obj1 == 0:
            yield board
            return
        
        if i >= len(board):
            return
        
        if board[i] is None and (board[i-1] is None or board[i-1] is self.space_object2 \
                                 or board[i+1] is None or board[i+1] is self.space_object2):
            board_copy = board.copy()
            board_copy[i] = self.space_object1
            yield from self._add_obj1_every(board_copy, num_obj1 - 1, i+1)
        yield from self._add_obj1_every(board, num_obj1, i+1)
    
    def _add_obj2_every(self, board, num_obj2):
        lone = []
        for i in range(len(board)):
            if board[i] is self.space_object1 \
            and board[i-1] is not self.space_object2 and board[i+1] is not self.space_object2:
                lone.append(i)
                
        obj2_spots = []
        n = len(board)
        
        for i in lone:
            current_spots = set()
            if board[i-1] is None:
                current_spots.add(((i-1) + n)%n)
            if board[i+1] is None:
                current_spots.add((i+1)%n)
            obj2_spots.append(current_spots)
                            
        for obj2_indices in cartesian_product_sets_no_supersets(obj2_spots):
            num_obj2_left = num_obj2
            board_copy = board.copy()
            for i in obj2_indices:
                num_obj2_left -= (board_copy[i] is not self.space_object2)
                board_copy[i] = self.space_object2
            if num_obj2_left >= 0:
                yield board_copy
                        
    def fill_board(self, board, num_objects):
        if self.qualifier is RuleQualifier.NONE:
            yield from self._fill_board_none(board, num_objects)
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            # Not yet supported
            return None
        else:
            num_obj1 = num_objects[self.space_object1]
            num_obj1_left = num_obj1
            num_obj2_left = num_objects[self.space_object2]
            
            for obj in board:
                if obj is self.space_object1:
                    num_obj1_left -= 1
                elif obj is self.space_object2:
                    num_obj2_left -= 1

            for starting_board in self._add_obj1_every(board, num_obj1_left):
                yield from self._add_obj2_every(starting_board, num_obj2_left)
        
            
    def affects(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object1, self.space_object2 ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object1 ]
    
    def completes(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object1, self.space_object2 ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object1 ]
    
    def adds(self):
        return [ self.space_object1, self.space_object2 ]
     
    
    def allowed_rule(self, num_objects, constraints, other_rules):
        for rule in other_rules:
            if set(self.space_objects()) - {SpaceObject.Empty} == set(rule.space_objects()) - {SpaceObject.Empty}:
                return False
            
        allowed_none_rule, allowed_at_least_one_rule, allowed_every_rule = \
        self.rule_types_allowed(num_objects, self.space_objects(), constraints + other_rules, AdjacentRule, AdjacentSelfRule, 2)
       
        if not allowed_none_rule and self.qualifier is RuleQualifier.NONE:
            return False
        
        if not allowed_at_least_one_rule and self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return False
        
        if not allowed_every_rule and self.qualifier is RuleQualifier.EVERY:
            return False
        
        return True
    
    @classmethod
    def generate_rule(cls, board, constraints, other_rules, space_object1, space_object2):
        num_object1 = board.num_objects()[space_object1]
        num_object2 = board.num_objects()[space_object2]
        space_objects = [space_object1, space_object2]
        
        for rule in other_rules:
            if set(space_objects) - {SpaceObject.Empty} == set(space_objects) - {SpaceObject.Empty}:
                return None
            
        allowed_none_rule, allowed_at_least_one_rule, allowed_every_rule = \
        cls.rule_types_allowed(board.num_objects(), space_objects, constraints + other_rules, AdjacentRule, AdjacentSelfRule, 2)
            
        if not allowed_none_rule and not allowed_at_least_one_rule and not allowed_every_rule:
            return None
        
        num_adjacent = 0
        num_any_adjacent = 0
        
        # Count how many object1s are adjacent to object2s 
        for i, obj in enumerate(board):
            if board[i-1] is space_object2 or board[i+1] is space_object2:
                if obj is space_object1:
                    num_adjacent += 1
                num_any_adjacent += 1
                          
        if MUST_ELIMINATE and num_any_adjacent == len(board) - space_object2:
            return None  
        
        # Create rule options
        if num_adjacent == 0:
            # None were adjacent
            qualifier_options = [RuleQualifier.NONE]
        elif num_adjacent < num_object1:
            # Some were adjacent
            qualifier_options = [RuleQualifier.AT_LEAST_ONE]
        else:
            # Every one was adjacent - also means at least one was 
            qualifier_options = [RuleQualifier.AT_LEAST_ONE, RuleQualifier.EVERY]
        
        # At least one just means every
        if num_object1 == 1:
            qualifier_options = [option for option in qualifier_options \
                                if option is not RuleQualifier.AT_LEAST_ONE]
        
        # Finding the object1s finds all the object2s
        if num_object1 >= 2 * num_object2:
            qualifier_options = [option for option in qualifier_options \
                                if option is not RuleQualifier.EVERY]
        
        if not allowed_every_rule:
            qualifier_options = [option for option in qualifier_options \
                                 if option is not RuleQualifier.EVERY]
            
        if not allowed_at_least_one_rule:
            qualifier_options = [option for option in qualifier_options \
                                 if option is not RuleQualifier.AT_LEAST_ONE]
            
        if not allowed_none_rule:
            qualifier_options = [option for option in qualifier_options \
                                 if option is not RuleQualifier.NONE]
        
        if len(qualifier_options) == 0:
            return None
        
        qualifier = random.choice(qualifier_options)
        return AdjacentRule(space_object1, space_object2, qualifier)
    
    @classmethod
    def eliminate_sectors(cls, board, constraints, data, space_object1, space_object2):  
        """
        Create a rule that will eliminate possible positions of space_object1, where 
        space_object1 and data.elimination_object are ambiguous on survey/target
        
        Only the sectors in data.need_eliminated are ambiguous, and the sectors in 
        data.already_eliminated have been eliminated by other rules. To be viable,
        this rule must eliminate at least data.minimum sectors, and if possible 
        should eliminate data.goal sectors.
        """
        # Some are already constrained, don't generate these rules
        if any(isinstance(constraint, cls) and constraint == cls(space_object1, space_object2, constraint.qualifier)
              for constraint in constraints):
            return None, None
        
        obj1_num_adjacent = 0
        el_adjacent = set()
        
        num_obj1 = board.num_objects()[space_object1]
        num_obj2 = board.num_objects()[space_object2]
        num_el = len(data.need_eliminated)
        
        # If the eliminated object is space object2, then space object1 "looks like" space object 2
        adjacent_objs = [space_object2]
        if data.elimination_object is space_object2:
            adjacent_objs.append(space_object1)
        
        # Count how many are adjacent
        for i, obj in enumerate(board):
            # An "object 2" is adjacent to this sector
            if board[i-1] in adjacent_objs or board[i+1] in adjacent_objs:
                if obj is space_object1:
                    # Count an object 1 being adjacent
                    obj1_num_adjacent += 1
                elif obj is data.elimination_object and i in data.need_eliminated:
                    # Add to list of sectors where the eliminated object is adjacent
                    el_adjacent.add(i)
                            
        # Only using "not adjacent" rules to avoid too powerful rules
        # There must be no object 1's ajacent to an 'object 2' 
        if obj1_num_adjacent == 0 and len(el_adjacent) > 0:
            eliminated = el_adjacent - data.already_eliminated
            # Must eliminate data.minimum new sectors
            if len(eliminated) >= data.minimum:
                rule = AdjacentRule(space_object1, space_object2, RuleQualifier.NONE)
                return eliminated, rule
        
        return None, None
    
    def positive_positions(self, board):
        return [i for i in range(len(board)) 
                 if board[i] is not self.space_object2 and 
                 (board[i-1] is self.space_object2 or board[i+1] is self.space_object2)]
    
    def code(self):
        return "A" + str(self.space_object1) + str(self.space_object2) + self.qualifier.code()
    
    @classmethod
    def parse(cls, s):
        space_object1 = SpaceObject.parse(s[1])
        space_object2 = SpaceObject.parse(s[2])
        qualifier = RuleQualifier.parse(s[3])
        return cls(space_object1, space_object2, qualifier)
    
    def to_json(self, board):
        return {
            "ruleType": "ADJACENT",
            "spaceObject1": self.space_object1.to_json(),
            "spaceObject2": self.space_object2.to_json(),
            "qualifier": self.qualifier.to_json(),
            "categoryName": self.category_name(),
            "text": self.text(board)
        }
    
    
class OppositeRule(RelationRule):
    """
    A rule stating that two objects are or aren't opposite to one another
    """
    def __init__(self, space_object1, space_object2, qualifier):
        self.space_object1 = space_object1
        self.space_object2 = space_object2
        self.qualifier = qualifier
        
    def __repr__(self):
        return "<" + self.qualifier.name + " " + repr(self.space_object1) + " opposite " \
                + repr(self.space_object2) + ">"
    
    def __str__(self):
        return str(self.qualifier) + " " + self.space_object1.name() + " is directly opposite " + \
                self.space_object2.one() + " " + self.space_object2.name() + "."
    
    def text(self, board):
        num_object1 = board.num_objects()[self.space_object1]
        num_object2 = board.num_objects()[self.space_object2]
        return self.qualifier.for_object(self.space_object1, num_object1) + " directly opposite " + \
                self.space_object2.any_of(num_object2) + "." 
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.qualifier == other.qualifier:
                if self.qualifier is RuleQualifier.NONE or self.qualifier is RuleQualifier.AT_LEAST_ONE:
                    # Mutual rules - i.e. space objects can be swapped
                    return self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2 or \
                            self.space_object1 == other.space_object2 and self.space_object2 == other.space_object1
                else:
                    # One way rules - i.e. space objects cannot be swapped
                    return self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2
            else:
                return False
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self.space_object1) + hash(self.space_object2) + hash(self.qualifier)
    
    def is_satisfied(self, board):
        half = len(board) // 2
        opposite_idxs = [i for i in range(len(board)) if board[i] is self.space_object1 
                            and board[i+half] is self.space_object2]
        
        if self.qualifier is RuleQualifier.NONE:
            return len(opposite_idxs) == 0
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return len(opposite_idxs) > 0
        else:
            if self.space_object1 in board.num_objects():
                num_obj = board.num_objects()[self.space_object1]
            else:
                num_obj = 0
            return len(opposite_idxs) == num_obj
    
    def is_immediately_limiting(self):
        return False

    def disallowed_sectors(self):
        return []
    
    def _fill_board_none(self, board, num_objects):
        if not self.is_satisfied(board):
            # There are already two opposite in this board, cannot meet rule
            return []
        
        num_obj1 = num_objects[self.space_object1]
        num_obj2 = num_objects[self.space_object2]
        num_none = 0
        
        # Count number of objects remaining to acheive num_objects
        for obj in board:
            if obj is self.space_object1:
                num_obj1 -= 1
            elif obj is self.space_object2:
                num_obj2 -= 1
            elif obj is None:
                num_none += 1
        
        # Number of Nones that will be on the board
        num_none -= (num_obj1 + num_obj2)
        
        new_boards = []
        
        perms = permutations_multi({self.space_object1: num_obj1, self.space_object2: num_obj2, None: num_none})
        for p in perms:
            board_copy = board.copy()
            j = 0
            for i in range(len(board_copy)):
                if board_copy[i] is None:
                    board_copy[i] = p[j]
                    j += 1
            if self.is_satisfied(board_copy):
                yield board_copy
            
    def _fill_board_every(self, board, num_objects, num_objects_left, start_i=0):
        # num_objects: how many should be on the board starting from start_i
        # num_objects_left: how many still need to be placed
        num_obj1 = num_objects[self.space_object1]
        
        num_obj1_left = num_objects_left[self.space_object1]
        num_obj2_left = num_objects_left[self.space_object2]
                
        new_num_objects = num_objects.copy()
        new_num_objects_left = num_objects_left.copy()

        if num_obj1 == 0:
            yield board
        
        half = len(board) // 2
        
        for i in range(start_i, len(board)):
            obj = board[i]
            is_obj1 = obj is self.space_object1
            if obj is None or is_obj1:
                already_opp = (board[i + half] is self.space_object2)
                board_copy = board.copy()
                board_copy[i + half] = self.space_object2
                board_copy[i] = self.space_object1

                # Only valid if these objects were already there or if we have some left to place
                if (already_opp or num_obj2_left > 0) and (is_obj1 or num_obj1_left > 0):
                    # Subtract 1 from number of objects that should be on the rest of the board
                    new_num_objects[self.space_object1] = num_obj1 - 1
                    # Subtract 1 from number of objects left if objects were placed
                    new_num_objects_left[self.space_object1] = num_obj1_left - (not is_obj1)
                    new_num_objects_left[self.space_object2] = num_obj2_left - (not already_opp)
                    yield from self._fill_board_every(board_copy, new_num_objects, new_num_objects_left, i+1)
                    
    def fill_board(self, board, num_objects):
        if self.qualifier is RuleQualifier.NONE:
            return self._fill_board_none(board, num_objects)
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            # Not yet supported
            return None
        else:
            num_objects_left = num_objects.copy()
            for obj in board:
                if obj is self.space_object1 or obj is self.space_object2:
                    num_objects_left[obj] -= 1
                
            return self._fill_board_every(board, num_objects, num_objects_left)
            
    def affects(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object1, self.space_object2 ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object1 ]
    
    def completes(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object1, self.space_object2 ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object1 ]
    
    def adds(self):
        return [ self.space_object1, self.space_object2 ]
    
    def allowed_rule(self, num_objects, constraints, other_rules):
        num_object1 = num_objects[self.space_object1]
        num_object2 = num_objects[self.space_object2]
        
        prev_rules = constraints + other_rules
        num_spots_uncovered = num_object1
        has_none_rule = False
        
        num_objects[self.space_object1]
        num_objects[self.space_object2]
        
        # Some are already constrained, don't generate these rules
        prev_rules = constraints + other_rules
        num_spots_uncovered = 2 * num_object1
        has_none_rule = False

        # If we create an every rule, it will define num_object1 more objects adjacent to object 2
        # We should only do this if this wouldn't over-define adjacent objects
        every_allowed = (num_spots_uncovered > num_object1) or (not has_none_rule)
        # If we create an "at least one" rule, it will define 1 more object adjacent to object 2
        at_least_one_allowed = (num_spots_uncovered > 1) or (not has_none_rule)
         
        for rule in constraints:
            # Don't allow opposite rules with the same two objects as an existing constraint
            if isinstance(rule, OppositeRule) and \
            { self.space_object1, self.space_object2 } == { rule.space_object1, rule.space_object2 }:
                return False
            
        for rule in other_rules:
            # Don't allow relation rules with the same two objects as an existing rule
            if isinstance(rule, RelationRule) and \
            { self.space_object1, self.space_object2 } == { rule.space_object1, rule.space_object2 }:
                return False
            # Don't allow self rules with object1 if I am a rule with Empty as the second object
            elif isinstance(rule, SelfRule) and self.space_object2 == SpaceObject.Empty \
            and rule.space_object == self.space_object1:
                return False
            # If space object 1 already has a "not opposite to" rule, we need to limit what rules 
            # we can produce
            if isinstance(rule, OppositeRule) and (rule.space_object1 == self.space_object1 or \
            rule.space_object2 == self.space_object1) and rule.qualifier is RuleQualifier.NONE:
                has_none_rule = True
            elif isinstance(rule, OppositeSelfRule) and rule.space_object == self.space_object1 \
            and rule.qualifier is RuleQualifier.NONE:
                has_none_rule = True
            
        for rule in prev_rules:
            # Set the number of spots opposite to the space_object1's that could be any 
            # object, not just those defined in previous opposite rules
            if isinstance(rule, OppositeRule) and rule.space_object1 == self.space_object1:
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= num_object1
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 1
            elif isinstance(rule, OppositeRule) and rule.space_object2 == self.space_object1: 
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= num_objects[rule.space_object2]
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 1
            elif isinstance(rule, OppositeSelfRule) and rule.space_object == self.space_object1:
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= num_object1
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 2      
        
        # Opposite objects already totally defined, redundant to create another rule
        if num_spots_uncovered <= 0:
            return False
            
        # We should only do this if this wouldn't over-define opposite objects
        every_allowed = not has_none_rule
        at_least_one_allowed = (num_spots_uncovered > 1) or (not has_none_rule)
            
        if not every_allowed and self.qualifier is RuleQualifier.EVERY:
            return False
        
        if not at_least_one_allowed and self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return False
        
        return True
    
    @classmethod
    def generate_rule(cls, board, constraints, other_rules, space_object1, space_object2):
        num_object1 = board.num_objects()[space_object1]
        num_object2 = board.num_objects()[space_object2]
        
        # Some are already constrained, don't generate these rules
        prev_rules = constraints + other_rules
        num_spots_uncovered = num_object1
        has_none_rule = False
        
        for rule in constraints:
            # Don't allow opposite rules with the same two objects as an existing constraint
            if isinstance(rule, cls) and rule == cls(space_object1, space_object2, rule.qualifier):
                return None
            
        for rule in other_rules:
            # Don't allow relation rules with the same two objects as an existing rule
            if isinstance(rule, cls) and (rule.space_object1 == space_object1 or rule.space_object2 == space_object1) \
            and rule.qualifier is RuleQualifier.NONE:
                has_none_rule = True
            # Don't allow self rules with object1 if I am a rule with Empty as the second object
            elif isinstance(rule, OppositeSelfRule) and rule.space_object == space_object1 \
            and rule.qualifier is RuleQualifier.NONE:
                has_none_rule = True
            
        for rule in prev_rules:
            # Set the number of spots opposite to the space_object1's that could be any 
            # object, not just those defined in previous opposite rules
            if isinstance(rule, cls) and rule.space_object1 == space_object1:
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= num_object1
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 1
            elif isinstance(rule, cls) and rule.space_object2 == space_object1: 
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= board.num_objects()[rule.space_object2]
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 1
            elif isinstance(rule, OppositeSelfRule) and rule.space_object == space_object1:
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= num_object1
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 2      
        
        # Opposite objects already totally defined, redundant to create another rule
        if num_spots_uncovered <= 0:
            return None
            
        # We should only do this if this wouldn't over-define opposite objects
        can_generate_every = not has_none_rule
        can_generate_at_least_one = (num_spots_uncovered > 1) or (not has_none_rule)
            
        if MUST_ELIMINATE:
            if OppositeSelfRule(space_object2, RuleQualifier.EVERY).is_satisfied(board):
                return None
        
        # Board must have an even number of sectors for objects to be opposite each other
        if len(board) % 2 != 0:
            return None
        
        num_opposite = 0
        num_any_opposite = 0
        half = int(len(board) / 2)
        
        # Calculate how many object1's are opposite object2's 
        for i, obj in enumerate(board):
            if board[i+half] is space_object2:
                if obj is space_object1:
                    num_opposite += 1
                num_any_opposite += 1
                                
        if MUST_ELIMINATE and num_any_opposite == len(board) - num_object2:
            return None

        # List possible rules
        if num_opposite == 0:
            # No object1's are opposite object2
            qualifier_options = [RuleQualifier.NONE]
        elif num_opposite < num_object1:
            # Some object1's are opposite object2
            qualifier_options = [RuleQualifier.AT_LEAST_ONE]
        else:
            # Every object1 is opposite an object2, which also means at least one is
            qualifier_options = [RuleQualifier.AT_LEAST_ONE, RuleQualifier.EVERY]
                    
        if num_object1 == num_object2:
            # This would completely determine one object given the other, too powerful
            qualifier_options = [option for option in qualifier_options \
                                if option is not RuleQualifier.EVERY]

        if num_object1 == 1:
            # At least one is the same as every, so drop at least one
            qualifier_options = [option for option in qualifier_options \
                                    if option is not RuleQualifier.AT_LEAST_ONE]
                    
        if not can_generate_every:
            qualifier_options = [option for option in qualifier_options \
                                 if option is not RuleQualifier.EVERY]
            
        if not can_generate_at_least_one:
            qualifier_options = [option for option in qualifier_options \
                                 if option is not RuleQualifier.AT_LEAST_ONE]
            
        if len(qualifier_options) == 0:
            return None
        
        # Choose a random rule of the options
        qualifier = random.choice(qualifier_options)
        return OppositeRule(space_object1, space_object2, qualifier)
    
    @classmethod
    def eliminate_sectors(cls, board, constraints, data, space_object1, space_object2):
        # Some are already constrained, don't generate these rules
        if any(isinstance(constraint, cls) and constraint == cls(space_object1, space_object2, constraint.qualifier)
              for constraint in constraints):
            return None, None
        
        # Board must have an even number of sectors for objects to be opposite each other
        if len(board) % 2 != 0:
            return None, None
        
        half = int(len(board) / 2)

        obj1_num_opposite = 0
        el_opposite = set()
        
        num_obj1 = board.num_objects()[space_object1]
        num_obj2 = board.num_objects()[space_object2]
        num_el = len(data.need_eliminated)
        
        # If space_object2 is the object we are trying to eliminate, it is ambiguous
        # with space_object1 and we should check for objects being opposite it as well
        opposite_objs = [space_object2]
        if data.elimination_object is space_object2:
            opposite_objs.append(space_object1)
        
        for i, obj in enumerate(board):
            # Object opposite this sector "looks like" object 2
            if board[i + half] in opposite_objs:
                if obj is space_object1:
                    # Add to count of space object 1 being opposite "object 2"
                    obj1_num_opposite += 1
                elif obj is space_object2 and i in data.need_eliminated:
                    # Add sector to the list of ambiguous sectors also opposite "object 2"
                    el_opposite.add(i)
        
        # Only allowing "not opposite" rules, since "is directly opposite" rules would be too powerful
        # This means that no object1s can appear to be opposite an object2 for this rule to be viable
        if obj1_num_opposite == 0 and len(el_opposite) > 0:
            eliminated = el_opposite - data.already_eliminated
            # There must be at least data.minimum sectors that aren't already eliminated which
            # ARE opposite an "object 2" for enough sectors to be eliminated by this rule
            if len(eliminated) >= data.minimum:
                rule = OppositeRule(space_object1, space_object2, RuleQualifier.NONE)
                return eliminated, rule
        
        return None, None
    
    def positive_positions(self, board):
        if len(board) % 2 != 0:
            return []
        
        half = len(board) // 2
        
        return [i for i in range(len(board)) 
                 if board[i] is not self.space_object2 and 
                 board[i+half] is self.space_object2]
    
    def code(self):
        return "O" + str(self.space_object1) + str(self.space_object2) + self.qualifier.code()

    @classmethod
    def parse(cls, s):
        space_object1 = SpaceObject.parse(s[1])
        space_object2 = SpaceObject.parse(s[2])
        qualifier = RuleQualifier.parse(s[3])
        return cls(space_object1, space_object2, qualifier)
    
    def to_json(self, board):
        return {
            "ruleType": "OPPOSITE",
            "spaceObject1": self.space_object1.to_json(),
            "spaceObject2": self.space_object2.to_json(),
            "qualifier": self.qualifier.to_json(),
            "categoryName": self.category_name(),
            "text": self.text(board)
        }
    
class WithinRule(RelationRule):
    """
    A rule stating that two objects are or aren't within a certain number of sectors from each other
    """
    def __init__(self, space_object1, space_object2, qualifier, num_sectors):
        self.space_object1 = space_object1
        self.space_object2 = space_object2
        self.qualifier = qualifier
        self.num_sectors = num_sectors
        
    def __repr__(self):
        return "<" + self.qualifier.name + " " + repr(self.space_object1) + " within " + str(self.num_sectors) + \
                " sectors of " + repr(self.space_object2) + ">"
    
    def __str__(self):
        return str(self.qualifier) + " " + self.space_object1.name() + " is within " + str(self.num_sectors) + \
                " sectors of " + self.space_object2.one() + " " + self.space_object2.name() + "."
    
    def text(self, board):
        num_object1 = board.num_objects()[self.space_object1]
        num_object2 = board.num_objects()[self.space_object2]
        return self.qualifier.for_object(self.space_object1, num_object1) + " within " + \
                str(self.num_sectors) + " sectors of " + self.space_object2.any_of(num_object2) + "."
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.qualifier == other.qualifier and self.num_sectors == other.num_sectors:
                if self.qualifier is RuleQualifier.NONE or self.qualifier is RuleQualifier.AT_LEAST_ONE:
                    # Mutual rules - i.e. space objects can be swapped
                    return self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2 or \
                            self.space_object1 == other.space_object2 and self.space_object2 == other.space_object1
                else:
                    # One way rules - i.e. space objects cannot be swapped
                    return self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2
            else:
                return False
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self.space_object1) + hash(self.space_object2) + hash(self.qualifier) + self.num_sectors
    
    def covers(self, other):
        if isinstance(other, self.__class__):
            if self.qualifier == other.qualifier:
                if self.qualifier is RuleQualifier.NONE:
                    # Mutual rules - i.e. space objects can be swapped
                    return self.num_sectors >= other.num_sectors and \
                            (self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2 or \
                            self.space_object1 == other.space_object2 and self.space_object2 == other.space_object1)
                elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
                    # Mutual rules - i.e. space objects can be swapped
                    return self.num_sectors <= other.num_sectors and \
                            (self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2 or \
                            self.space_object1 == other.space_object2 and self.space_object2 == other.space_object1)
                else:
                    # One way rules - i.e. space objects cannot be swapped
                    return self.num_sectors <= other.num_sectors and \
                            self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2
            else:
                return False
        else:
            return False
        
    def _is_satisfied_none(self, board):
        prev = None
        countdown = 0
        is_valid = True
        # Maintain a count of how many sectors since we've seen an object1 or object2
        for i in range(-self.num_sectors, len(board)):
            obj = board[i]
            # If it hasn't been num_sectors and we see the other object, it doesn't satisfy the rule
            if obj is self.space_object1 or obj is self.space_object2:
                if countdown != 0 and obj != prev:
                    is_valid = False
                    break
                prev = obj
                # Restart the countdown
                countdown = self.num_sectors
            else:
                countdown = max(0, countdown - 1)
                
        return is_valid
    
    def _num_within(self, board):
        prev = None, None
        countdown = 0
        within_indices = set()
        # Maintain a countdown of how long it's been since we've seen an object1 or object 2
        for i in range(-self.num_sectors, len(board)):
            if board[i] is self.space_object2:
                if countdown > 0 and prev[0] is self.space_object1:
                    # We've seen an object1 within the past num_sectors, and we found an object 2
                    within_indices.add(i % len(board))
                prev = board[i], i
                countdown = self.num_sectors
            elif board[i] is self.space_object1:
                if countdown > 0 and prev[1] is self.space_object2:
                    # We've seen an object2 within the past num_sectors, and we found an object 1
                    within_indices.add(prev[1] % len(board))
                prev = board[i], i
                countdown = self.num_sectors
            else:
                countdown = max(0, countdown - 1)
        return len(within_indices)
    
    def is_satisfied(self, board):
        if self.qualifier is RuleQualifier.NONE:
            return self._is_satisfied_none(board)
        else:
            num_within = self._num_within(board)
            if self.qualifier is RuleQualifier.AT_LEAST_ONE:
                return num_within > 0
            else:
                if self.space_object1 in board.num_objects():
                    num_obj = board.num_objects()[self.space_object1]
                else:
                    num_obj = 0
                return num_within == num_obj
    
    def is_immediately_limiting(self):
        return False

    def disallowed_sectors(self):
        return []
    
    def _fill_board_none(self, board, num_objects):
        if not self.is_satisfied(board):
            # There are already some within this range, cannot meet rule
            return []
                
        num_obj1 = num_objects[self.space_object1]
        num_obj2 = num_objects[self.space_object2]
        
        if self.space_object1 in board.num_objects():
            num_obj1 -= board.num_objects()[self.space_object1]
        
        if self.space_object2 in board.num_objects():
            num_obj2 -= board.num_objects()[self.space_object2]
                
        return [Board(b) for b in fill_no_within({self.space_object1: num_obj1, self.space_object2: num_obj2}, \
                                                 board, self.num_sectors)]
   
    def _fill_board_every(self, board, num_obj1, num_objects_left, start_i=0):
        # num_obj1: how many should be on the board starting from start_i
        # num_objects_left: how many still need to be placed
        num_obj1_left = num_objects_left[self.space_object1]
        num_obj2_left = num_objects_left[self.space_object2]
                
        new_num_objects_left = num_objects_left.copy()

        if num_obj1 == 0:
            return [ board ]
        
        board_size = len(board)
                
        new_boards = []
        for i in range(start_i, board_size):
            obj = board[i]
            is_obj1 = obj is self.space_object1
            # Attempt to fill each position with an object1 is possible
            if obj is None or is_obj1:
                options = 0
                if is_obj1 or num_obj1_left > 0:
                    if any(board[j] is self.space_object2 for j in range(i-self.num_sectors, i+self.num_sectors+1)):
                        # If there is already an obj2 in range, fill with obj1 and proceed
                        options += 1
                        board_copy = board.copy()
                        board_copy[i] = self.space_object1
                        new_num_objects_left[self.space_object1] = num_obj1_left - (not is_obj1)
                        new_num_objects_left[self.space_object2] = num_obj2_left
                        new_boards.extend(self._fill_board_every(board_copy, num_obj1 - 1, new_num_objects_left, i+1))
                    elif num_obj2_left > 0:
                        # Otherwise there must be obj2 left to use
                        for j in range(i-self.num_sectors, i):
                            if board[j] is None:
                                
                                if not any(k >= 0 and board[k] is self.space_object1 for k in range(max(0, j-self.num_sectors), j)):
                                    options += 1
                                    board_copy = board.copy() 
                                    board_copy[i] = self.space_object1
                                    board_copy[j] = self.space_object2
                                    new_num_objects_left[self.space_object1] = num_obj1_left - (not is_obj1)
                                    new_num_objects_left[self.space_object2] = num_obj2_left - 1
                                    new_boards.extend(self._fill_board_every(board_copy, num_obj1 - 1, new_num_objects_left, i+1))

                        max_sector = min(i+self.num_sectors+1, len(board)+(i-self.num_sectors))
                        for j in range(i+1, max_sector):
                            if board[j] is None:
                                if not any(k < len(board) and board[k] is self.space_object1 for k in range(j+1, min(j+self.num_sectors+1, board_size))):
                                    options += 1
                                    board_copy = board.copy() 
                                    board_copy[i] = self.space_object1
                                    board_copy[j] = self.space_object2
                                    new_num_objects_left[self.space_object1] = num_obj1_left - (not is_obj1)
                                    new_num_objects_left[self.space_object2] = num_obj2_left - 1
                                    new_boards.extend(self._fill_board_every(board_copy, num_obj1 - 1, new_num_objects_left, i+1))

                    if is_obj1 and options == 0:
                        # Unable to place an obj2 next to an existing obj1
                        return []
                
        return new_boards
 
    def fill_board(self, board, num_objects):
        if self.qualifier is RuleQualifier.NONE:
            return self._fill_board_none(board, num_objects)
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            # Not yet supported
            return None
        else:
            num_objects_left = num_objects.copy()
            for obj in board:
                if obj is self.space_object1 or obj is self.space_object2:
                    num_objects_left[obj] -= 1
                
            return self._fill_board_every(board, num_objects[self.space_object1], num_objects_left)
            
    def affects(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object1, self.space_object2 ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object1 ]
    
    def completes(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object1, self.space_object2 ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object1 ]
    
    def adds(self):
        return [ self.space_object1, self.space_object2 ]
    
    @staticmethod
    def _circle_dist(i, j, size):
        """
        The distance between i and j on a circle of size size - i.e. modular distance
        """
        dist = abs(i - j)
        return min(dist, size - dist)
    
    @staticmethod
    def _max_min_sectors_away(space_object1, space_object2, board):
        """
        Calculate the minimum and maximum number of sectors any space_object1 is from space_object2
        """
        board_size = len(board)
        obj1_positions = [i for i, obj in enumerate(board) if obj is space_object1]
        obj2_positions = [i for i, obj in enumerate(board) if obj is space_object2]
        
        maximum_sectors = 0
        minimum_sectors = board_size
        for i in obj1_positions:
            # How far away this obj1 is from the nearest obj2
            sectors_away = min(WithinRule._circle_dist(i, j, board_size) for j in obj2_positions)
            if sectors_away > maximum_sectors:
                maximum_sectors = sectors_away
            if sectors_away < minimum_sectors:
                minimum_sectors = sectors_away
        
        return minimum_sectors, maximum_sectors
    
    @staticmethod
    def _max_between(space_object, board):
        max_run = 0
        current_run = 0
        for obj in board:
            if obj == space_object:
                if current_run > max_run:
                    max_run = current_run
                current_run = 0
            else:
                current_run += 1
                
        for obj in board:
            if obj == space_object:
                if current_run > max_run:
                    max_run = current_run
                break
            else:
                current_run += 1
                
        return max_run
    
    def allowed_rule(self, num_objects, constraints, other_rules):
        min_none = 2
        max_every = sum(num_objects.values())
        
        for constraint in constraints:
            # Don't add rule if there's already a Within constraint on these objects and this doesn't make it tighter
            if isinstance(constraint, WithinRule):
                if constraint.qualifier is RuleQualifier.NONE and \
                { self.space_object1, self.space_object2 } == { constraint.space_object1, constraint.space_object2 }:
                    if constraint.num_sectors + 1 > min_none:
                        min_none = constraint.num_sectors + 1
                elif constraint.qualifier is RuleQualifier.EVERY and \
                { self.space_object1, self.space_object2 } == { constraint.space_object1, constraint.space_object2 }:
                    if constraint.num_sectors - 1 < max_every:
                        max_every = constraint.num_sectors - 1
        
        for rule in other_rules:
            if isinstance(rule, RelationRule) and \
                { self.space_object1, self.space_object2 } == { rule.space_object1, rule.space_object2 }:
                    return False
            elif isinstance(rule, SelfRule) and self.space_object2 == SpaceObject.Empty \
            and rule.space_object == self.space_object1:
                return False

        if self.qualifier is RuleQualifier.EVERY:
            return self.num_sectors <= max_every
        elif self.qualifier is RuleQualifier.NONE:
            return self.num_sectors >= min_none
        else:
            return False
    
    @classmethod
    def generate_rule(cls, board, constraints, other_rules, space_object1, space_object2):
        min_none = 2
        max_every = len(board)
        
        # Some objects are already constrained, must constrain them even further or generate no rule
        for constraint in constraints:
            if isinstance(constraint, cls):
                if constraint.qualifier is RuleQualifier.NONE and \
                { space_object1, space_object2 } == { constraint.space_object1, constraint.space_object2 }:
                    if constraint.num_sectors + 1 > min_none:
                        min_none = constraint.num_sectors + 1
                elif constraint.qualifier is RuleQualifier.EVERY and \
                { space_object1, space_object2 } == { constraint.space_object1, constraint.space_object2 }:
                    if constraint.num_sectors - 1 < max_every:
                        max_every = constraint.num_sectors - 1
        
        num_object1 = board.num_objects()[space_object1]
        num_object2 = board.num_objects()[space_object2]
        
        # There must be more of object 2 (or at least the same amount) than object 1
        if num_object1 > num_object2:
            return None
        
        max_n = int(len(board)/3 - 1)
        max_every = min(max_every, max_n)
        
        min_sectors, max_sectors = cls._max_min_sectors_away(space_object1, space_object2, board)
        
        options = []
        
        if min_sectors > min_none:
            # Create a random number of sectors that no object1 is within object2
            # This must be < min_sectors, because object1 is within that many sectors of object2.
            num_not_within = random.randrange(min_none, min_sectors)
            options.append((RuleQualifier.NONE, num_not_within))
        
        if max_sectors <= max_every:
            if MUST_ELIMINATE:
                max_between_obj2 = cls._max_between(space_object2, board)
                max_for_eliminating = (max_between_obj2 - 1) // 2

                max_rule = min(max_for_eliminating, max_every)
            else:
                max_rule = max_n
                
            min_rule = max(2, max_sectors)
                    
            if min_rule <= max_rule:
                # Create a random number of sectors that every object1 is within object2
                # This must be at least max_sectors, to cover every possible object1
                num_within = random.randrange(min_rule, max_rule+1)
                options.append((RuleQualifier.EVERY, num_within))
            
        if len(options) == 0:
            return None
        
        # Choose a random rule
        qualifier, num_sectors = random.choice(options)
        return WithinRule(space_object1, space_object2, qualifier, num_sectors)
    
    @classmethod
    def eliminate_sectors(cls, board, constraints, data, space_object1, space_object2):
        """
        Create a rule that will eliminate possible positions of space_object1, where 
        space_object1 and data.elimination_object are ambiguous on survey/target
        
        Only the sectors in data.need_eliminated are ambiguous, and the sectors in 
        data.already_eliminated have been eliminated by other rules. To be viable,
        this rule must eliminate at least data.minimum sectors, and if possible 
        should eliminate data.goal sectors.
        """
        min_none = 2
        max_every = len(board)
        
        # Some objects are already constrained, must constrain them even further or generate no rule
        for constraint in constraints:
            if isinstance(constraint, cls):
                if constraint.qualifier is RuleQualifier.NONE and \
                { space_object1, space_object2 } == { constraint.space_object1, constraint.space_object2 }:
                    if constraint.num_sectors + 1 > min_none:
                        min_none = constraint.num_sectors + 1
                elif constraint.qualifier is RuleQualifier.EVERY and \
                (space_object1, space_object2) == (constraint.space_object1, constraint.space_object2):
                    if constraint.num_sectors - 1 < max_every:
                        max_every = constraint.num_sectors - 1
        
        max_n = int(len(board)/3 - 1)
        max_every = min(max_every, max_n)
        
        board_size = len(board)
        obj1_positions = [i for i, obj in enumerate(board) if obj is space_object1]
        el_positions = data.need_eliminated
        obj2_positions = [i for i, obj in enumerate(board) if obj is space_object2]
        
        # Object 2 appears same as object 1
        if data.elimination_object is space_object2:
            obj2_positions += obj1_positions
        
        # Get the maximum and minimum positions that object 1 is away from an "object 2"
        max_obj1 = 0
        min_obj1 = board_size
        for i in obj1_positions:
            sectors_away = min(WithinRule._circle_dist(i, j, board_size) for j in obj2_positions if j != i)
            if sectors_away > max_obj1:
                max_obj1 = sectors_away
            if sectors_away < min_obj1:
                min_obj1 = sectors_away
        
        # Get how many sectors each eliminated object is from an "object 2"
        # Organize them into an array, with each index containing the indices for elimination objects that are that
        # number of sectors from an "object 2"
        max_el = 0
        min_el = board_size
        el_sectors_away = set()
        el_sectors_away = [[]]
        for i in el_positions:
            sectors_away = min(WithinRule._circle_dist(i, j, board_size) for j in obj2_positions if j != i)
            if sectors_away > len(el_sectors_away) - 1:
                el_sectors_away.extend([[] for j in range(sectors_away-len(el_sectors_away)+1)])
            el_sectors_away[sectors_away].append(i)
            if sectors_away > max_el:
                max_el = sectors_away
            if sectors_away < min_el:
                min_el = sectors_away
                
        options = []
        for sectors_away, matching_el_indices in enumerate(el_sectors_away):
            if sectors_away < min_none or sectors_away > max_every:
                continue
            if sectors_away >= min_obj1:
                # An "every obj1 within n sectors rule" would eliminate the el_objs further than that
                eliminated = set(i for idx_list in el_sectors_away[sectors_away+1:] for i in idx_list)
                if len(eliminated) > 0:
                    eliminated -= data.already_eliminated
                    options.append((sectors_away, eliminated, RuleQualifier.EVERY))
            if sectors_away < max_obj1:
                # A "no obj1 within n sectors rule" would eliminate the el_objs that are within that range
                eliminated = set(i for idx_list in el_sectors_away[:sectors_away+1] for i in idx_list)
                if len(eliminated) > 0:
                    eliminated -= data.already_eliminated
                    options.append((sectors_away, eliminated, RuleQualifier.NONE))

        if len(options) == 0:
            return None, None
                
        max_num_eliminated = max(len(eliminated) for sectors, eliminated, qualifier in options)
        
        # Only consider rules eliminating the goal value if it at least one does
        if max_num_eliminated >= data.goal:
            options = [option for option in options if len(option[1]) >= data.goal]
           
        # In any case, rules must eliminate the minimum number of sectors
        options = [option for option in options if len(option[1]) >= data.minimum]

        if len(options) == 0:
            return None, None
        
        # Generate a random rule from the choices
        rand_rule_opts = random.choice(options)
        
        num_object1 = board.num_objects()[space_object1]
        num_object2 = board.num_objects()[space_object2]
        rand_rule = WithinRule(space_object1, space_object2, rand_rule_opts[2], rand_rule_opts[0])
        
        return rand_rule_opts[1], rand_rule

    def positive_positions(self, board):
        obj2_positions = [i for i, obj in enumerate(board) if obj is self.space_object2]
        within_positions = []
        board_size = len(board)
        
        for i in range(len(board)):
            if board[i] != self.space_object2:
                sectors_away = min(WithinRule._circle_dist(i, j, board_size) for j in obj2_positions)
                if sectors_away <= self.num_sectors:
                    within_positions.append(i)
        
        return within_positions
    
    def code(self):
        return "W" + str(self.space_object1) + str(self.space_object2) + self.qualifier.code() + str(self.num_sectors)
    
    @classmethod
    def parse(cls, s):
        space_object1 = SpaceObject.parse(s[1])
        space_object2 = SpaceObject.parse(s[2])
        qualifier = RuleQualifier.parse(s[3])
        num_sectors = int(s[4])
        return cls(space_object1, space_object2, qualifier, num_sectors)
    
    def to_json(self, board):
        return {
            "ruleType": "WITHIN",
            "spaceObject1": self.space_object1.to_json(),
            "spaceObject2": self.space_object2.to_json(),
            "numSectors": self.num_sectors,
            "qualifier": self.qualifier.to_json(),
            "categoryName": self.category_name(),
            "text": self.text(board)
        }
    
class AdjacentSelfRule(SelfRule):
    """
    A rule stating that an object is or is not adjacent to another of the same object
    """
    def __init__(self, space_object, qualifier):
        self.space_object = space_object
        self.qualifier = qualifier
        
    def __repr__(self):
        return "<" + self.qualifier.name + " " + repr(self.space_object) + " adjacent to " \
                + repr(self.space_object) + ">"
    
    def __str__(self):
        return str(self.qualifier) + " " + self.space_object.name() + " is adjacent to another " + \
                self.space_object.name() + "."
    
    def text(self, board):
        num_object = board.num_objects()[self.space_object]
        return self.qualifier.for_object(self.space_object, num_object) + " adjacent to another " \
                + self.space_object.name() + "."
   
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.qualifier == other.qualifier and self.space_object == other.space_object
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self.space_object) + hash(self.qualifier)
    
    def is_satisfied(self, board):
        adjacent_idxs = [i for i in range(len(board)) if board[i] is self.space_object
                            and (board[i-1] is self.space_object or board[i+1] is self.space_object)]
        
        if self.qualifier is RuleQualifier.NONE:
            return len(adjacent_idxs) == 0
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return len(adjacent_idxs) > 0
        else:
            if self.space_object in board.num_objects():
                num_obj = board.num_objects()[self.space_object]
            else:
                num_obj = 0
            return len(adjacent_idxs) == num_obj
    
    def is_immediately_limiting(self):
        return False

    def disallowed_sectors(self):
        return []
    
    def _fill_board_none(self, board, num_objects):
        if not self.is_satisfied(board):
            # There are already two adjacent in this board, cannot meet rule
            return []
        
        num_obj = num_objects[self.space_object]  
        num_obj -= sum(obj is self.space_object for obj in board)
        
        board_perms = add_one_no_self_touch(self.space_object, num_obj, board.copy())
        return board_perms
    
    def _fill_board_runs(self, board, num_obj, start_i=0, t=0):
        # Fill in board with runs of asteroids, starting new runs only at start_i and after

        # If there are no asteroids left, check if board is valid
        if num_obj == 0:
            if self.is_satisfied(board):
                yield board
                return
            else:
                return
                   
        # If there is a lone asteroid, find it and immediately add another asteroid clockwise
        for i in range(start_i - 1, len(board)):
            obj = board[i]
            if obj is self.space_object and board[i-1] is not self.space_object \
            and board[i+1] is not self.space_object:
                # Found a lone asteroid
                # Only fill asteroid runs to the right without combining runs
                if board[i+1] is None and board[i+2] is not self.space_object:
                    board_copy = board.copy()
                    board_copy[i+1] = self.space_object
                    yield from self._fill_board_runs(board_copy, num_obj - 1, start_i, t+1)
                    
                return
                
        run_starts = [i for i in range(len(board)) if board[i] is self.space_object 
                      and board[i-1] is not self.space_object]
                
        for i in range(len(board)):
            obj = board[i]
            if obj is None:
                is_last_run = len(run_starts) == 0 or i < run_starts[0] or i >= run_starts[-1]
                # Continue an asteroid run without combining two runs
                if is_last_run and board[i-1] is self.space_object and board[i+1] is not self.space_object:
                    board_copy = board.copy()
                    board_copy[i] = self.space_object
                    yield from self._fill_board_runs(board_copy, num_obj - 1, start_i, t+1)
                # OR start a new asteroid run, if conditions allow
                elif i >= start_i and num_obj > 1 and board[i-1] is not self.space_object \
                and board[i+1] is not self.space_object:
                    board_copy = board.copy()
                    board_copy[i] = self.space_object
                    yield from self._fill_board_runs(board_copy, num_obj - 1, i+1, t+1)
            
    def _prepare_board(self, board, num_obj, lone, run_backwards, start_i=None):
        # Get board into a valid starting state
        # A valid starting state is one where there are no lone objects
        
        # lone: positions of lone objects
        # run_backwards: posititons of "starts" of object runs that can be continued backwards
        if start_i is None:
            start_i = len(board) - 1
        
        board_ready = len(lone) == 0 and len(run_backwards) == 0
        if board_ready:
            yield (num_obj, board) 

        if start_i <= 0:
            return
        
        for i in range(start_i, -1, -1):
            obj = board[i]
            if obj is self.space_object:
                if board[i-1] is not self.space_object and board[i+1] is not self.space_object:
                    # lone object
                    if board[i+1] is None and board[i+2] is not self.space_object:
                        # Add object to the right, remove from lone object list
                        board_copy = board.copy()
                        board_copy[i+1] = self.space_object
                        new_lone = lone - {i}
                        yield from self._prepare_board(board_copy, num_obj - 1, new_lone, run_backwards, i-1)
                        
                if board[i-1] is None:
                    # Continue this object run backwards
                    new_run_backwards = run_backwards - { i }
                    if board[i+1] is self.space_object:
                        # Continue it with 0 objects backwards
                        yield from self._prepare_board(board.copy(), num_obj, lone, new_run_backwards, i-1)
                        
                    num_left = num_obj
                    j = i - 1
                    board_copy = board.copy()
                    while num_left > 0:
                        if board[j] is None:
                            # Add an object to the run on the left
                            board_copy[j] = self.space_object
                            num_left -= 1
                            # If j-1 was lone, it isn't anymore
                            new_lone = lone - { j - 1 % len(board) }
                            # Add options where we stop the run here
                            yield from self._prepare_board(board_copy, num_left, new_lone, new_run_backwards, j-1)
                            board_copy = board_copy.copy()
                            j -= 1
                        elif board[j] is self.space_object:
                            # Object is already part of the run, keep going backwards
                            j -= 1
                        else:
                            # Hit another type of object, run is over
                            break
                                                
    def _fill_board_every(self, board, num_objects):
        num_left = num_objects[self.space_object] - sum(obj is self.space_object for obj in board)
        # Get current positions of lone objects
        lone = set(i for i, obj in enumerate(board) if obj is self.space_object
                and board[i-1] is not self.space_object and board[i+1] is not self.space_object)
        # Get current positions where we can continue an object run to the left
        run_backwards = set(i for i, obj in enumerate(board) if obj is self.space_object
                           and board[i-1] is None)
        # Prepare the board by getting boards starting from this one where there are no
        # lone objects, and where we try continuing runs to the left (which isn't
        # allowed in the _fill_board_runs algorithm)
        boards = self._prepare_board(board, num_left, lone, run_backwards)

        for num_obj, board in boards:
            yield from self._fill_board_runs(board, num_obj)
    
    def fill_board(self, board, num_objects):
        if self.qualifier is RuleQualifier.NONE:
            return self._fill_board_none(board, num_objects)
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            # Not yet supported
            return None
        else:  
            return self._fill_board_every(board, num_objects)
            
    def affects(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object ]
    
    def completes(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object ]
    
    def adds(self):
        return [ self.space_object ]
    
    def allowed_rule(self, num_objects, constraints, other_rules):
        prev_rules = constraints + other_rules
        num_obj = num_objects[self.space_object]
        num_spots_uncovered = 2 * num_obj
        has_none_rule = False

        for rule in constraints:
            # If this object already has an adjacent self constraint, don't add this rule
            if isinstance(rule, AdjacentSelfRule) and self.space_object == rule.space_object:
                return False
            # If this object has a sectors constraint, and adjacent rule would be too constraining
            elif isinstance(rule, SectorsRule) and rule.space_object == self.space_object:
                return False
            
        for rule in other_rules:
            # If there's already a rule with this object and empty, don't create this self rule
            if isinstance(rule, RelationRule) and self.space_object == rule.space_object1 and \
            rule.space_object2 == SpaceObject.Empty:
                return False
            # If there's already a self rule with this object, don't create this self rule
            elif isinstance(rule, SelfRule) and self.space_object == rule.space_object:
                return False
            
            # If this object has a "not" adjacent rule already, we need to limit whether
            # we can create more adjacent rules
            if isinstance(rule, AdjacentRule) and (rule.space_object1 == self.space_object or \
            rule.space_object2 == self.space_object) and rule.qualifier is RuleQualifier.NONE:
                has_none_rule = True
            elif isinstance(rule, AdjacentSelfRule) and rule.space_object == self.space_object \
            and rule.qualifier is RuleQualifier.NONE:
                has_none_rule = True
            
        for rule in prev_rules:
            # Count the number of "adjacent spots" not covered by current adjacency rules
            if isinstance(rule, AdjacentRule) and rule.space_object1 == self.space_object:
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= num_obj
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 1
            elif isinstance(rule, AdjacentRule) and rule.space_object2 == self.space_object: 
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= (num_objects[rule.space_object2] + 1) // 2
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 1
            elif isinstance(rule, AdjacentSelfRule) and rule.space_object == self.space_object:
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= num_obj
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 2   
            # If there is a band rule below a certain size, the objects must necessarily be 
            # adjacent so we shouldn't create this rule
            elif isinstance(rule, BandRule) and rule.space_object == self.space_object and \
            rule.band_size < 2 * num_obj - 1:
                return False
        
        # If we've defined all of the objects next to this one already, we shouldn't create 
        # more adjacency rules
        if num_spots_uncovered <= 0:
            return False
        
        # There must be room to define 2 more spots for the objects next to this one in order 
        # to create a self-adjacency rule
        at_least_one_allowed = (num_spots_uncovered > 2) or (not has_none_rule)
        
        if not at_least_one_allowed and self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return False
       
        return True
    
    @classmethod
    def generate_rule(cls, board, constraints, other_rules, space_object):
        # Some constraints already limit this significantly and would be redundant
        prev_rules = constraints + other_rules
        num_obj = board.num_objects()[space_object]
        num_spots_uncovered = 2 * num_obj
        has_none_rule = False

        for rule in constraints:
            # If this object already has an adjacent self constraint, don't add this rule
            if isinstance(rule, cls) and rule == cls(space_object, rule.qualifier):
                return None
            # If this object has a sectors constraint, and adjacent rule would be too constraining
            elif isinstance(rule, SectorsRule) and rule.space_object == space_object:
                return None
            
        for rule in other_rules:
            # If there's already a rule with this object and empty, don't create this self rule
            if isinstance(rule, AdjacentRule) and (rule.space_object1 == space_object or rule.space_object2 == space_object) \
            and rule.qualifier is RuleQualifier.NONE:
                has_none_rule = True
            # If there's already a self rule with this object, don't create this self rule
            elif isinstance(rule, cls) and rule.space_object == space_object \
            and rule.qualifier is RuleQualifier.NONE:
                has_none_rule = True
            
        for rule in prev_rules:
            # Count the number of "adjacent spots" not covered by current adjacency rules
            if isinstance(rule, AdjacentRule) and rule.space_object1 == space_object:
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= num_obj
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 1
            elif isinstance(rule, AdjacentRule) and rule.space_object2 == space_object: 
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= (board.num_objects()[rule.space_object2] + 1) // 2
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 1
            elif isinstance(rule, cls) and rule.space_object == space_object:
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= num_obj
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 2   
            # If there is a band rule below a certain size, the objects must necessarily be 
            # adjacent so we shouldn't create this rule
            elif isinstance(rule, BandRule) and rule.space_object == space_object and \
            rule.band_size < 2 * num_obj - 1:
                return None
    
        # If we've defined all of the objects next to this one already, we shouldn't create 
        # more adjacency rules
        if num_spots_uncovered <= 0:
            return None
        
        # There must be room to define 2 more spots for the objects next to this one in order 
        # to create a self-adjacency rule
        can_generate_at_least_one = (num_spots_uncovered > 2) or (not has_none_rule)
                
        # If there's only one object it can never be adjacent to itself
        if num_obj == 1:
            return None
        
        num_adjacent = 0
        
        # Count how many objects are adjacent
        for i, obj in enumerate(board):
            if obj is space_object:
                if board[i-1] is space_object or board[i+1] is space_object:
                    num_adjacent += 1
                            
        # Not using every, too powerful
        if num_adjacent == 0:
            qualifier_options = [RuleQualifier.NONE]
        else:
            qualifier_options = [RuleQualifier.AT_LEAST_ONE]
        
        # At least one would mean every for these cases
        if num_obj <= 2:
            qualifier_options = [option for option in qualifier_options \
                                if option is not RuleQualifier.AT_LEAST_ONE]
            
        if not can_generate_at_least_one:
            qualifier_options = [option for option in qualifier_options \
                                if option is not RuleQualifier.AT_LEAST_ONE]
                        
        if len(qualifier_options) == 0:
            return None
        
        # Choose a random rule
        qualifier = random.choice(qualifier_options)
        return AdjacentSelfRule(space_object, qualifier)
        
    @staticmethod
    def _repeats(partition):
        # Number of rearrangements of a partition possible without changing it
        counts = {}
        for val in partition:
            if val in counts:
                counts[val] += 1
            else:
                counts[val] = 1
        
        repeats = 1
        for val in counts:
            repeats *= factorial(counts[val])
            
        return repeats
    
    def base_factor(self, board):
        num_object = board.num_objects()[self.space_object]
        board_size = len(board)
        
        num_total_combos = comb(board_size, num_object)
                
        if self.qualifier is RuleQualifier.EVERY:
            num_positive_combos = 0
            for partition in calc_partitions(num_object, 2):
                repeats = AdjacentSelfRule._repeats(partition)
                combos = board_size
                # Must be enough spots to leave gaps between the objects
                spots_left = board_size - num_object - 1
                if spots_left >= len(partition) - 1:
                    # Number of ways to rearrange all the empty spots and the groupings of objects
                    combos *= int(factorial(spots_left)/factorial(spots_left - len(partition) + 1))
                else:
                    combos = 0
                # Number of unique combos
                combos //= repeats
                num_positive_combos += combos
                
            return num_positive_combos/num_total_combos
        else:
            if (board_size < 2 * num_object):
                return 0

            num_none_combos = board_size
            spots_left = board_size - num_object - 1
            # Must be enough spots to leave gaps between all the objects
            if spots_left >= num_object - 1:
                # Number of ways to rearrange all the empty spots and groupings of objects
                num_none_combos *= int(factorial(spots_left)/factorial(spots_left - num_object + 1))
            else:
                num_none_combos = 0
                
            # Number of unique combos
            num_none_combos //= factorial(num_object)
            
            if self.qualifier is RuleQualifier.NONE:
                return num_none_combos/num_total_combos
            elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
                return (num_total_combos - num_none_combos)/num_total_combos
        
    def base_strength(self, board):
        num_object = board.num_objects()[self.space_object]
        board_size = len(board)
        
        num_total_combos = comb(board_size, num_object)
                
        if self.qualifier is RuleQualifier.EVERY:
            num_positive_combos = 0
            for partition in calc_partitions(num_object):
                repeats = AdjacentSelfRule._repeats(partition)
                combos = board_size
                # Must be enough spots to leave gaps between the objects
                spots_left = board_size - num_object - 1
                if spots_left >= len(partition) - 1:
                    # Number of ways to rearrange all the empty spots and the groupings of objects
                    combos *= int(factorial(spots_left)/factorial(spots_left - len(partition) + 1))
                else:
                    combos = 0
                # Number of unique combos
                combos //= repeats
                num_positive_combos += combos
                
            return (num_total_combos - num_positive_combos)/(num_total_combos - 1)
        else:
            if (board_size < 2 * num_object):
                return 0

            num_none_combos = board_size
            spots_left = board_size - num_object - 1
            # Must be enough spots to leave gaps between all the objects
            if spots_left >= num_object - 1:
                # Number of ways to rearrange all the empty spots and groupings of objects
                num_none_combos *= int(factorial(spots_left)/factorial(spots_left - num_object + 1))
            else:
                num_none_combos = 0
                
            # Number of unique combos
            num_none_combos //= factorial(num_object)
            
            if self.qualifier is RuleQualifier.NONE:
                return (num_total_combos - num_none_combos)/(num_total_combos - 1)
            elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
                return num_none_combos/(num_total_combos - 1)
    
    def code(self):
        return "C" + str(self.space_object) + self.qualifier.code()
    
    @classmethod
    def parse(cls, s):
        space_object = SpaceObject.parse(s[1])
        qualifier = RuleQualifier.parse(s[2])
        return cls(space_object, qualifier)
    
    def to_json(self, board):
        return {
            "ruleType": "ADJACENT_SELF",
            "spaceObject": self.space_object.to_json(),
            "qualifier": self.qualifier.to_json(),
            "categoryName": self.category_name(),
            "text": self.text(board)
        }
    
class OppositeSelfRule(SelfRule):
    """
    A rule stating that an object is or is not opposite to another of the same object
    """
    def __init__(self, space_object, qualifier):
        self.space_object = space_object
        self.qualifier = qualifier
    
    def __repr__(self):
        return "<" + self.qualifier.name + " " + repr(self.space_object) + " opposite " \
                + repr(self.space_object) + ">"
    
    def __str__(self):
        return str(self.qualifier) + " " + self.space_object.name() + " is directly opposite another " + \
                self.space_object.name() + "."
    
    def text(self, board):
        num_object = board.num_objects()[self.space_object]
        return self.qualifier.for_object(self.space_object, num_object) + " directly opposite another " + \
                self.space_object.name() + "."
   
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.qualifier == other.qualifier and self.space_object == other.space_object
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self.space_object) + hash(self.qualifier)
    
    def is_satisfied(self, board):
        if len(board) % 2 != 0:
            return self.qualifier is RuleQualifier.NONE
        
        half = len(board) // 2
        
        opposite_idxs = [i for i in range(len(board)) if board[i] is self.space_object
                            and board[i+half] is self.space_object]
        
        if self.qualifier is RuleQualifier.NONE:
            return len(opposite_idxs) == 0
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return len(opposite_idxs) > 0
        else:
            if self.space_object in board.num_objects():
                num_obj = board.num_objects()[self.space_object]
            else:
                num_obj = 0
            return len(opposite_idxs) == num_obj
    
    def is_immediately_limiting(self):
        return False

    def disallowed_sectors(self):
        return []
    
    def _fill_board_none(self, board, num_objects):
        if not self.is_satisfied(board):
            # There are already two opposite in this board, cannot meet rule
            return []
        
        num_obj = num_objects[self.space_object]
        num_none = 0
        
        # Number of None and obj1 needing to be added
        for obj in board:
            if obj is self.space_object:
                num_obj -= 1
            elif obj is None:
                num_none += 1
        
        num_none -= num_obj
                
        # Get all permutations and check which ones work
        perms = permutations_multi({self.space_object: num_obj, None: num_none})
        for p in perms:
            board_copy = board.copy()
            j = 0
            for i in range(len(board_copy)):
                if board_copy[i] is None:
                    board_copy[i] = p[j]
                    j += 1
            if self.is_satisfied(board_copy):
                yield board_copy
    
    def _prepare_board_every(self, board):
        # Ensure every space_object already on the board is opposite another space_object
        new_board = board.copy()
        half = len(board) // 2
        
        for i in range(half):
            if new_board[i] is self.space_object:
                if new_board[i+half] is None:
                    new_board[i+half] = self.space_object
                elif new_board[i+half] is not self.space_object:
                    return None
            elif new_board[i+half] is self.space_object:
                if new_board[i] is None:
                    new_board[i] = self.space_object
                elif new_board[i] is not self.space_object:
                    return None
        
        return new_board
    
    def _fill_board_every(self, board, num_obj_left, start_i=0):
        # num_objects: how many should be on the board starting from start_i
        # num_objects_left: how many still need to be placed
        if num_obj_left == 0:
            yield board
        
        half = len(board) // 2
        
        new_boards = []
        # Place 2 space_objects opposite each other
        for i in range(start_i, half):
            if board[i] is None:
                board_copy = board.copy()
                board_copy[i + half] = self.space_object
                board_copy[i] = self.space_object

                yield from self._fill_board_every(board_copy, num_obj_left - 2, i+1)
             
    def fill_board(self, board, num_objects):
        if self.qualifier is RuleQualifier.NONE:
            return self._fill_board_none(board, num_objects)
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            # Not yet supported
            return None
        else:  
            num_obj = num_objects[self.space_object]
            num_left = num_obj - sum(obj is self.space_object for obj in board)
            
            # Fill in space_objects opposite existing space_objects
            prep_board = self._prepare_board_every(board)
            if prep_board is None:
                return []
            
            # Check that we still have >= 0 space_objects left to place
            num_left = num_obj - sum(obj is self.space_object for obj in prep_board)
            
            if num_left < 0:
                return []
            
            # Get all combos of placing more space_objects opposite each other on the board
            return self._fill_board_every(prep_board, num_left)
            
    def affects(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object ]
    
    def completes(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object ]
    
    def adds(self):
        return [ self.space_object ]
    
    def allowed_rule(self, num_objects, constraints, other_rules):
        prev_rules = constraints + other_rules
        num_obj = num_objects[self.space_object]
        num_spots_uncovered = num_obj
        has_none_rule = False
        board_size = sum(num_objects.values())
        
        if board_size % 2 != 0:
            return False

        for rule in constraints:
            # If there's already an opposite self constraint, don't add this rule
            if isinstance(rule, OppositeSelfRule) and rule.space_object == self.space_object:
                return False
            # If there's a sectors constraint, an opposite self constraint would be too constraining
            elif isinstance(rule, SectorsRule) and rule.space_object == self.space_object:
                return False
            
        for rule in other_rules:
            # If there's already a relation rule between this space object and empty, don't add this rule
            if isinstance(rule, RelationRule) and self.space_object == rule.space_object1 and \
            rule.space_object2 == SpaceObject.Empty:
                return False
            # If there's already a self rule for this space object, don't add this rule
            elif isinstance(rule, SelfRule) and self.space_object == rule.space_object:
                return False
            # If there's already an not opposite rule for this object, we need to limit how many more 
            # opposite rules can be added
            if isinstance(rule, OppositeRule) and (rule.space_object1 == self.space_object or \
            rule.space_object2 == self.space_object) and rule.qualifier is RuleQualifier.NONE:
                has_none_rule = True
            elif isinstance(rule, OppositeSelfRule) and rule.space_object == self.space_object \
            and rule.qualifier is RuleQualifier.NONE:
                has_none_rule = True
            
        for rule in prev_rules:
            # Check how many spots opposite to this object are not covered by existing rules
            if isinstance(rule, OppositeRule) and rule.space_object1 == self.space_object:
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= num_obj
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 1
            elif isinstance(rule, OppositeRule) and rule.space_object2 == self.space_object: 
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= num_objects[rule.space_object2]
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 1
            elif isinstance(rule, OppositeSelfRule) and rule.space_object == self.space_object:
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= num_obj
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 2 
            # If the objects are in a band small enough, it is impossible for them to be opposite
            # each other so this rule shouldn't be added
            elif isinstance(rule, BandRule) and rule.space_object == self.space_object and \
            rule.band_size <= board_size // 2:
                return False
        
        # If all opposite spots have been covered, another opposite rule would be redundant
        if num_spots_uncovered <= 0:
            return False
       
        # To create a new opposite self rule, more than two spots must not be covered or 
        # there are no "none" rules to make it over-defined
        at_least_one_allowed = (num_spots_uncovered > 2) or (not has_none_rule)
        
        if not at_least_one_allowed and self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return False
        
        return True
        
    @classmethod
    def generate_rule(cls, board, constraints, other_rules, space_object):
        # Some constraints already limit this significantly and would be redundant
        prev_rules = constraints + other_rules
        num_obj = board.num_objects()[space_object]
        num_spots_uncovered = num_obj
        has_none_rule = False

        for rule in constraints:
            # If there's already an opposite self constraint, don't add this rule
            if isinstance(rule, cls) and rule == cls(space_object, rule.qualifier):
                return None
            # If there's a sectors constraint, an opposite self constraint would be too constraining
            elif isinstance(rule, SectorsRule) and rule.space_object == space_object:
                return None
            
        for rule in other_rules:
            # If there's already a relation rule between this space object and empty, don't add this rule
            if isinstance(rule, OppositeRule) and (rule.space_object1 == space_object or rule.space_object2 == space_object) \
            and rule.qualifier is RuleQualifier.NONE:
                has_none_rule = True
            # If there's already a self rule for this space object, don't add this rule
            elif isinstance(rule, cls) and rule.space_object == space_object \
            and rule.qualifier is RuleQualifier.NONE:
                has_none_rule = True
            
        for rule in prev_rules:
            # Check how many spots opposite to this object are not covered by existing rules
            if isinstance(rule, OppositeRule) and rule.space_object1 == space_object:
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= num_obj
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 1
            elif isinstance(rule, OppositeRule) and rule.space_object2 == space_object: 
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= board.num_objects()[rule.space_object2]
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 1
            elif isinstance(rule, cls) and rule.space_object == space_object:
                if rule.qualifier is RuleQualifier.EVERY:
                    num_spots_uncovered -= num_obj
                elif rule.qualifier is RuleQualifier.AT_LEAST_ONE:
                    num_spots_uncovered -= 2 
            # If the objects are in a band small enough, it is impossible for them to be opposite
            # each other so this rule shouldn't be added
            elif isinstance(rule, BandRule) and rule.space_object == space_object and \
            rule.band_size <= len(board) // 2:
                return None
        
        # If all opposite spots have been covered, another opposite rule would be redundant
        if num_spots_uncovered <= 0:
            return None

        # To create a new opposite self rule, more than two spots must not be covered or 
        # there are no "none" rules to make it over-defined
        can_generate_at_least_one = (num_spots_uncovered > 2) or (not has_none_rule)
        
        # Board must have an even number of sectors for objects to be opposite each other
        if len(board) % 2 != 0:
            return None
        
        num_opposite = 0
        half = int(len(board) / 2)
                
        # If there is only one object it can't be opposite itself
        if num_obj == 1:
            return None
        
        # Count how many of this space object are opposite another one
        for i, obj in enumerate(board):
            if obj is space_object:
                if board[i+half] is space_object:
                    num_opposite += 1
        
        # Create possible rules
        if num_opposite == 0:
            # None were opposite each other
            qualifier_options = [RuleQualifier.NONE]
        elif num_opposite < num_obj:
            # Some were opposite each other
            qualifier_options = [RuleQualifier.AT_LEAST_ONE]
        else:
            # Every one was opposite the other - also means at least one was
            qualifier_options = [RuleQualifier.AT_LEAST_ONE, RuleQualifier.EVERY]

        # Don't use EVERY qualifier as it would be too powerful
        qualifier_options = [option for option in qualifier_options \
                            if option is not RuleQualifier.EVERY]

        if num_obj <= 2:
            # This would completely determine the locations given one of them, too powerful
            qualifier_options = [option for option in qualifier_options \
                                 if option is not RuleQualifier.AT_LEAST_ONE]
            
        if not can_generate_at_least_one:
            qualifier_options = [option for option in qualifier_options \
                                 if option is not RuleQualifier.AT_LEAST_ONE]
                    
        if len(qualifier_options) == 0:
            return None
        
        # Choose a random option
        qualifier = random.choice(qualifier_options)
        return OppositeSelfRule(space_object, qualifier)
    
    def base_factor(self, board):
        if len(board) % 2 != 0:
            return 0
        
        num_object = board.num_objects()[self.space_object]
        half_num = num_object // 2
        board_size = len(board)
        half_size = board_size // 2
        
        num_total_combos = comb(board_size, num_object)
            
        if self.qualifier is RuleQualifier.EVERY:
            # Choose n/2 spots on half of the board to define where the space objects are 
            num_valid_combos = comb(half_size, half_num)
            return num_valid_combos/num_total_combos
        else:
            if len(board) < 2 * num_object:
                return 0
            
            # Choose spots for the space objects one by one
            num_none_combos = 1
            sectors_left = board_size
            for i in range(num_object):
                num_none_combos *= sectors_left
                sectors_left -= 2
            num_none_combos //= int(factorial(num_object))
            
            # Define strength based on how many combinations are eliminaed
            if self.qualifier is RuleQualifier.NONE:
                return num_none_combos/num_total_combos
            elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
                return (num_total_combos - num_none_combos)/num_total_combos
    
    def base_strength(self, board):
        if len(board) % 2 != 0:
            return 0
        
        num_object = board.num_objects()[self.space_object]
        half_num = num_object // 2
        board_size = len(board)
        half_size = board_size // 2
        
        num_total_combos = comb(board_size, num_object)
            
        if self.qualifier is RuleQualifier.EVERY:
            # Choose n/2 spots on half of the board to define where the space objects are 
            num_valid_combos = comb(half_size, half_num)
            return (num_total_combos - num_valid_combos)/(num_total_combos - 1)
        else:
            if len(board) < 2 * num_object:
                return 0
            
            # Choose spots for the space objects one by one
            num_none_combos = 1
            sectors_left = board_size
            for i in range(num_object):
                num_none_combos *= sectors_left
                sectors_left -= 2
            num_none_combos //= int(factorial(num_object))
            
            # Define strength based on how many combinations are eliminaed
            if self.qualifier is RuleQualifier.NONE:
                return (num_total_combos - num_none_combos)/(num_total_combos - 1)
            elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
                return num_none_combos/(num_total_combos - 1)
    
    def code(self):
        return "S" + str(self.space_object) + self.qualifier.code()
    
    @classmethod
    def parse(cls, s):
        space_object = SpaceObject.parse(s[1])
        qualifier = RuleQualifier.parse(s[2])
        return cls(space_object, qualifier)
    
    def to_json(self, board):
        return {
            "ruleType": "OPPOSITE_SELF",
            "spaceObject": self.space_object.to_json(),
            "qualifier": self.qualifier.to_json(),
            "categoryName": self.category_name(),
            "text": self.text(board)
        }
    
class BandRule(SelfRule):
    """
    A rule stating that objects are in a band of a certain number of sectors
    """
    def __init__(self, space_object, band_size, precision):
        """
        Creates a BandRule stating that the space_objects are in a band of size band_size
        with precision precision
        """
        self.space_object = space_object
        self.band_size = band_size
        self.precision = precision
        
    def __repr__(self):
        return "<" + repr(self.space_object) + ", band: " + str(self.band_size) + ", precision: " + \
            self.precision.to_json() + ">"
    
    def __str__(self):
        return "The " + self.space_object.plural() + " are in a band of " + str(self.precision) + " " + \
            str(self.band_size) + "."
    
    def text(self, board):
        return str(self)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.band_size == other.band_size and self.space_object == other.space_object and \
                    self.precision == other.precision
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self.space_object) + self.band_size + hash(self.precision)
    
    @staticmethod
    def _smallest_band(space_object, board):
        """
        Finds the smallest band the space_objects are in on Board board.
        """
        board_size = len(board)
        
        # Find the longest run between space_objects
        longest_run_between = 0
        run_between = 0
        for obj in board:
            if not obj is space_object:
                run_between += 1
            else:
                if run_between > longest_run_between:
                    longest_run_between = run_between
                run_between = 0
        
        # Continue looking from the start, since the board is a circle
        for obj in board:
            if not obj is space_object:
                run_between += 1
            else:
                if run_between > longest_run_between:
                    longest_run_between = run_between
                break
        
        smallest_band = board_size - longest_run_between
        
        return smallest_band
        
    def is_satisfied(self, board):
        smallest_band = self._smallest_band(self.space_object, board)
        
        if self.precision == Precision.STRICT:
            return smallest_band == self.band_size
        elif self.precision == Precision.WITHIN:
            return smallest_band <= self.band_size
    
    def is_immediately_limiting(self):
        return False

    def disallowed_sectors(self):
        return []
    
    def _fill_band(self, board, num_obj, band_start, i_start=None):
        """
        Given the start location of the band, fill in the remaining objects in the center of the 
        band
        
        board: The Board to fill, with the start and end object in the band already filled
        num_obj: The number of objects to fill in the band 
        band_start: The index of the first object in the band
        i_start: objects can be filled in starting at index i_start and not before
        """
        if i_start is None:
            i_start = band_start
            
        if num_obj == 0:
            yield board
            return
        
        for i in range(i_start, band_start + self.band_size - num_obj):
            # Try every position possible for the next object
            if board[i] is None:
                board_copy = board.copy()
                board_copy[i] = self.space_object
                # Place object here and then recurse to fill in remaining objects
                yield from self._fill_band(board_copy, num_obj - 1, band_start, i+1)
    
    def _fill_board_exact(self, board, num_objects, exact_size):
        # Must be at least two dwarf planets (start & end of the band)
        if num_objects[self.space_object] < 2:
            return
        
        for i in range(len(board)):
            # Try every start/end pair of objects for the band
            if board[i] is None and board[i + exact_size - 1] is None:
                board_copy = board.copy()
                board_copy[i] = self.space_object
                board_copy[i + exact_size - 1] = self.space_object
                # Fill in the dwarf planets inside the band
                yield from self._fill_band(board_copy, num_objects[self.space_object] - 2, i)
    
    def fill_board(self, board, num_objects):
        if self.precision is Precision.STRICT:
            yield from self._fill_board_exact(board, num_objects, self.band_size)
        else:
            min_size = num_objects[self.space_object]
            max_size = self.band_size
            for size in range(min_size, max_size+1):
                yield from self._fill_board_exact(board, num_objects, size)
            
    def affects(self):
        return [ self.space_object ]
    
    def completes(self):
        return [ self.space_object ]
    
    def adds(self):
        return [ self.space_object ]
    
    def allowed_rule(self, num_objects, constraints, other_rules):
        # If there's already a band rule constraint for this object, do not add another
        if any(isinstance(constraint, BandRule) and constraint.space_object == self.space_object 
              for constraint in constraints):
            return False
        
        for rule in other_rules:
            # If there is a relation rule between this object and empty, do not add this rule
            if isinstance(rule, RelationRule) and self.space_object == rule.space_object1 and \
            rule.space_object2 == SpaceObject.Empty:
                return False
            # If there is a self rule for this object, do not add this rule
            elif isinstance(rule, SelfRule) and self.space_object == rule.space_object:
                return False
        
        return True
    
    @classmethod
    def generate_rule(cls, board, constraints, other_rules, space_object):
        # Some objects are already constrained to be in bands, don't generate
        # similar rules
        if any(isinstance(constraint, cls) and constraint.space_object == space_object 
              for constraint in constraints):
            return None
                
        # Must be at least 2 objects to have a band rule
        if board.num_objects()[space_object] == 1:
            return None
        
        num_obj = board.num_objects()[space_object]
        # Won't generate a rule for too large or small of a band
        band_max = min(2 * num_obj + 1, len(board) // 2)
       
        smallest_band = cls._smallest_band(space_object, board)
        band_min = max(smallest_band, num_obj + 1)
        
        if band_min > band_max:
            return None
        else:
            # Generate a random band size up to the max 
            # (The space objects are still within this size)
            rand_band = random.randint(band_min, band_max)
            return BandRule(space_object, rand_band, Precision.WITHIN)
     
    def base_factor(self, board):
        num_object = board.num_objects()[self.space_object]
        # Valid only for band_size < len(board)/2
        if self.precision is Precision.STRICT:
            band_locations = len(board)
            inner_band_combos = comb(self.band_size - 2, num_object - 2)
            num_positive_combos = band_locations * inner_band_combos
        elif self.precision is Precision.WITHIN:
            band_locations = len(board)
            right_band_combos = comb(self.band_size - 1, num_object - 1)
            num_positive_combos = band_locations * right_band_combos
            
        num_total_combos = comb(len(board), num_object)
        return num_positive_combos/num_total_combos
                
    def base_strength(self, board):
        num_object = board.num_objects()[self.space_object]
        # Valid only for band_size < len(board)/2
        if self.precision is Precision.STRICT:
            band_locations = len(board)
            inner_band_combos = comb(self.band_size - 2, num_object - 2)
            num_positive_combos = band_locations * inner_band_combos
        elif self.precision is Precision.WITHIN:
            band_locations = len(board)
            right_band_combos = comb(self.band_size - 1, num_object - 1)
            num_positive_combos = band_locations * right_band_combos
            
        num_total_combos = comb(len(board), num_object)
        return (num_total_combos - num_positive_combos)/(num_total_combos - 1)
    
    def code(self):
        return "B" + str(self.space_object) + self.precision.code() + str(self.band_size)
    
    @classmethod
    def parse(cls, s):
        space_object = SpaceObject.parse(s[1])
        precision = Precision.parse(s[2])
        band_size = int(s[3:])
        return cls(space_object, band_size, precision)
    
    def to_json(self, board):
        return {
            "ruleType": "BAND",
            "spaceObject": self.space_object.to_json(),
            "numSectors": self.band_size,
            "precision": self.precision.to_json(),
            "categoryName": self.category_name(),
            "text": self.text(board)
        }

class SectorsRule(SelfRule):
    """
    A rule stating that objects are only in particular sectors
    """
    def __init__(self, space_object, positions, board_size):
        self.space_object = space_object
        self.positions = positions
        self.board_size = board_size
        
    def __repr__(self):
        return "<" + repr(self.space_object) + ", positions: " + str(self.positions) + ">"
    
    def __str__(self):
        return "The " + self.space_object.plural() + " are only in sectors " + \
            ", ".join([str(i+1) for i in self.positions]) + "."
    
    def text(self, board):
        return str(self)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.positions == other.positions
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self.space_object) + hash(self.board_size) + hash(tuple(positions))
        
    def is_satisfied(self, board):
        for i, obj in enumerate(board):
            if obj is self.space_object:
                if i not in self.positions:
                    return False
        return True
    
    def is_immediately_limiting(self):
        return True

    def disallowed_sectors(self):
        return [ (self.space_object, set(range(self.board_size)) - set(self.positions)) ]
    
    def fill_board(self, board, num_objects):
        if not self.is_satisfied(board):
            return
        
        obj_positions = {i for i, obj in enumerate(board) if obj is self.space_object}
        rem_positions = self.positions - obj_positions 
        num_obj = num_objects[self.space_object] - len(obj_positions)
        # Generate all permutations for object positions
        for idx_sublist in itertools.combinations(rem_positions, num_obj):
            # Puts those comets on the board if there is nothing there already
            if all(board[i] is None for i in idx_sublist):
                new_board = board.copy()
                for i in idx_sublist:
                    new_board[i] = self.space_object
                yield new_board
            
    def affects(self):
        return [ self.space_object ]
    
    def completes(self):
        return [ self.space_object ]
    
    def adds(self):
        return [ self.space_object ]
    
    def allowed_rule(self, num_objects, constraints, other_rules):
        return False
    
    @classmethod
    def generate_rule(cls, board, constraints, other_rules, space_object):
        # Will not generate generic rules of this type
        return None
    
    def base_factor(self, board):
        num_object = board.num_objects()[self.space_object]
        total_combos = comb(len(board), num_object)
        valid_combos = comb(len(self.positions), num_object)
        return valid_combos/total_combos
        
    def base_strength(self, board):
        num_object = board.num_objects()[self.space_object]
        total_combos = comb(len(board), num_object)
        valid_combos = comb(len(self.positions), num_object)
        return (total_combos - valid_combos)/(total_combos - 1)
    
    def code(self):
        return "P" + str(self.space_object) + "".join(chr(i + 65) for i in self.positions)
    
    @classmethod
    def parse(cls, s):
        space_object = SpaceObject.parse(s[1])
        positions = [ord(c) - 65 for c in s[2:]]
        return cls(space_object, positions)
    
    def to_json(self, board):
        return {
            "ruleType": "SECTORS",
            "spaceObject": self.space_object.to_json(),
            "allowedSectors": self.positions,
            "categoryName": self.category_name(),
            "text": self.text(board)
        }
    
class CometRule(SectorsRule):
    @staticmethod
    def _generate_prime_indices(n):
        """
        Generates a set of primes from 1 to n, minus one
        
        n: maximum of range to generate primes in
        """
        primes = set()
        for i in range(2, n+1):
            is_prime = True
            for prime in primes:
                if i % (prime+1) == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.add(i-1)
        return primes
    
    def __init__(self, board_size):
        super().__init__(SpaceObject.Comet, self._generate_prime_indices(board_size), board_size)