import itertools
import random
import json
from enum import Enum
from abc import *

from .utilities import permutations_multi, add_two_no_touch, fill_no_within, add_one_no_self_touch
from .board import *
from .board_type import *

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
            e.g. "No gas cloud is" or "At least one asteriod is" or "Every comet is not"
        
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
    
    @classmethod
    @abstractmethod
    def generate_rule(cls, board, constraints, *space_objects):
        """
        Generates a rule of this type for a particular board and space objects to relate 
        to each other. Returns None if no such rule exists, or if such a rule would be 
        redundant with the given constraints.
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
    
class RelationRule(Rule):
    def space_objects(self):
        return [self.space_object1, self.space_object2]
    
    @classmethod
    @abstractmethod
    def eliminate_sectors(cls, board, data, space_object1, space_object2):
        """
        Create a rule that will eliminate possible positions of space_object1, where 
        space_object1 and data.elimination_object are ambiguous on survey/target
        
        Only the sectors in data.need_eliminated are ambiguous, and the sectors in 
        data.already_eliminated have been eliminated by other rules. To be viable,
        this rule must eliminate at least data.minimum sectors, and if possible 
        should eliminate data.goal sectors.
        """
        pass
    
class SelfRule(Rule):
    def space_objects(self):
        return [self.space_object]
        
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
        
        return add_two_no_touch(self.space_object1, self.space_object2, num_obj1, num_obj2, board.copy())    
    
    def _fill_board_every(self, board, num_obj1, num_obj1_left, num_obj2_left, start_i=0):
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
                        new_boards.extend(self._fill_board_every(board_copy, num_obj1 - 1, \
                                                                 num_obj1_left - (not is_obj1), num_obj2_left, i+1))
                    elif num_obj2_left > 0:
                        # Otherwise there must be obj2 left to use
                        if board[i-1] is None and (i-2 < 0 or board[i-2] is not self.space_object1):
                            # Do not put an obj2 on the left if there is a obj1
                            # already to the left of that, to avoid duplicate boards
                            # Only follow this restriction if we are looking at a space object that we placed 
                            # under this algorithm, not one that existed before: i.e. it's ok if said object 
                            # is around the end of the board (to the back)
                            options += 1
                            board_copy = board.copy()
                            board_copy[i] = self.space_object1
                            board_copy[i-1] = self.space_object2
                            new_boards.extend(self._fill_board_every(board_copy, num_obj1 - 1, \
                                                                     num_obj1_left - (not is_obj1), num_obj2_left - 1, i+1))
                    
                        if board[i+1] is None and (i+2 < len(board) or board[i+2] is not self.space_object1):
                            # Do not put an obj2 on the right if there is a obj1
                            # to the right of that, to avoid duplicate boards
                            # Only follow this restriction if we are looking at a space object that we placed 
                            # under this algorithm, not one that existed before: i.e. it's ok as long it's 
                            # not around the end of the board (to the front)
                            options += 1
                            board_copy = board.copy()
                            board_copy[i] = self.space_object1
                            board_copy[i+1] = self.space_object2
                            new_boards.extend(self._fill_board_every(board_copy, num_obj1 - 1, \
                                                                     num_obj1_left - (not is_obj1), num_obj2_left - 1, i+2))

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
            num_obj1 = num_objects[self.space_object1]
            num_obj1_left = num_obj1
            num_obj2_left = num_objects[self.space_object2]
            
            for obj in board:
                if obj is self.space_object1:
                    num_obj1_left -= 1
                elif obj is self.space_object2:
                    num_obj2_left -= 1
                
            return self._fill_board_every(board, num_obj1, num_obj1_left, num_obj2_left)
            
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
    
    @classmethod
    def generate_rule(cls, board, constraints, space_object1, space_object2):
        # Some are already constrained, don't generate these rules
        if any(isinstance(constraint, cls) and constraint == cls(space_object1, space_object2, constraint.qualifier)
              for constraint in constraints):
            return None

        num_adjacent = 0
        
        # Count how many object1s are adjacent to object2s 
        for i, obj in enumerate(board):
            if obj is space_object1:
                if board[i-1] is space_object2 or board[i+1] is space_object2:
                    num_adjacent += 1
        
        num_object1 = board.num_objects()[space_object1]
        num_object2 = board.num_objects()[space_object2]
        
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
        
        # Finding one object2 finds all object1s
        if num_object1 >= 2 * num_object2:
            qualifier_options = [option for option in qualifier_options \
                                if option is not RuleQualifier.EVERY]
            
        if len(qualifier_options) == 0:
            return None
        
        qualifier = random.choice(qualifier_options)
        return AdjacentRule(space_object1, space_object2, qualifier)
    
    @classmethod
    def eliminate_sectors(cls, space_object1, space_object2, data, board, constraints):  
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
            return None
        
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
            return len(opposite_idxs) == board.num_objects()[self.space_object1]
    
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
        
        for obj in board:
            if obj is self.space_object1:
                num_obj1 -= 1
            elif obj is self.space_object2:
                num_obj2 -= 1
            elif obj is None:
                num_none += 1
        
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

                if (already_opp or num_obj2_left > 0) and (is_obj1 or num_obj1_left > 0):
                    new_num_objects[self.space_object1] = num_obj1 - 1
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
    
    @classmethod
    def generate_rule(cls, board, constraints, space_object1, space_object2):
        # Some are already constrained, don't generate these rules
        if any(isinstance(constraint, cls) and constraint == cls(space_object1, space_object2, constraint.qualifier)
              for constraint in constraints):
            return None
        
        # Board must have an even number of sectors for objects to be opposite each other
        if len(board) % 2 != 0:
            return None
        
        num_opposite = 0
        half = int(len(board) / 2)
        
        # Calculate how many object1's are opposite object2's 
        for i, obj in enumerate(board):
            if obj is space_object1:
                if board[i+half] is space_object2:
                    num_opposite += 1
        
        num_object1 = board.num_objects()[space_object1]
        num_object2 = board.num_objects()[space_object2]
        
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
                    
        if len(qualifier_options) == 0:
            return None
        
        # Choose a random rule of the options
        qualifier = random.choice(qualifier_options)
        return OppositeRule(space_object1, space_object2, qualifier)
    
    @classmethod
    def eliminate_sectors(cls, space_object1, space_object2, data, board, constraints):
        # Some are already constrained, don't generate these rules
        if any(isinstance(constraint, cls) and constraint == cls(space_object1, space_object2, constraint.qualifier)
              for constraint in constraints):
            return None
        
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
        for i in range(-self.num_sectors, len(board)):
            obj = board[i]
            if obj is self.space_object1 or obj is self.space_object2:
                if countdown != 0 and obj != prev:
                    is_valid = False
                    break
                prev = obj
                countdown = self.num_sectors
            else:
                countdown = max(0, countdown - 1)
                
        return is_valid
    
    def _num_within(self, board):
        prev = None, None
        countdown = 0
        within_indices = set()
        for i in range(-self.num_sectors, len(board)):
            if board[i] is self.space_object1:
                if countdown > 0 and prev[0] is self.space_object2:
                    within_indices.add(i % len(board))
                prev = board[i], i
                countdown = self.num_sectors
            elif board[i] is self.space_object2:
                if countdown > 0 and prev[1] is not None:
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
                return num_within == board.num_objects()[self.space_object1]
    
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
    
    @classmethod
    def generate_rule(cls, board, constraints, space_object1, space_object2):
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
            max_between_obj2 = cls._max_between(space_object2, board)
            max_for_eliminating = (max_between_obj2 - 1) // 2
            
            max_rule = min(max_for_eliminating, max_every)
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
    def eliminate_sectors(cls, space_object1, space_object2, data, board, constraints):
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
    
    def _fill_board_runs(self, board, num_obj, start_i=0):
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
                    yield from self._fill_board_runs(board_copy, num_obj - 1, start_i)
                    
                return
                    
        for i in range(len(board)):
            obj = board[i]
            if obj is None:
                # Continue an asteroid run without combining two runs
                if board[i-1] is self.space_object and board[i+1] is not self.space_object:
                    board_copy = board.copy()
                    board_copy[i] = self.space_object
                    yield from self._fill_board_runs(board_copy, num_obj - 1, start_i)
                # OR start a new asteroid run, if conditions allow
                elif i >= start_i and num_obj > 1 and board[i-1] is not self.space_object \
                and board[i+1] is not self.space_object:
                    board_copy = board.copy()
                    board_copy[i] = self.space_object
                    yield from self._fill_board_runs(board_copy, num_obj - 1, i+1)
            
    def _prepare_board(self, board, num_obj, lone, run_backwards, start_i=None):
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
                    if board[i+1] is None and board[i+2] is not self.space_object:
                        board_copy = board.copy()
                        board_copy[i+1] = self.space_object
                        new_lone = lone - {i}
                        yield from self._prepare_board(board_copy, num_obj - 1, new_lone, run_backwards, i-1)
                        
                if board[i-1] is None:
                    new_run_backwards = run_backwards - { i }
                    if board[i+1] is self.space_object:
                        yield from self._prepare_board(board.copy(), num_obj, lone, new_run_backwards, i-1)
                        
                    num_left = num_obj
                    j = i - 1
                    board_copy = board.copy()
                    while num_left > 0:
                        if board[j] is None:
                            board_copy[j] = self.space_object
                            num_left -= 1
                            new_lone = lone - { j - 1 % len(board) }
                            yield from self._prepare_board(board_copy, num_left, new_lone, new_run_backwards, j-1)
                            board_copy = board_copy.copy()
                            j -= 1
                        elif board[j] is self.space_object:
                            j -= 1
                        else:
                            break
                                                
    def _fill_board_every(self, board, num_objects):
        num_left = num_objects[self.space_object] - sum(obj is self.space_object for obj in board)
        lone = set(i for i, obj in enumerate(board) if obj is self.space_object
                and board[i-1] is not self.space_object and board[i+1] is not self.space_object)
        run_backwards = set(i for i, obj in enumerate(board) if obj is self.space_object
                           and board[i-1] is None)
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
    
    @classmethod
    def generate_rule(cls, board, constraints, space_object):
        # Some constraints already limit this significantly and would be redundant
        if any((isinstance(constraint, cls) and constraint == cls(space_object, constraint.qualifier))
               or (isinstance(constraint, SectorRule) and constraint.space_object == space_object) 
               for constraint in constraints):
            return None
        
        num_obj = board.num_objects()[space_object]
        
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
            
        if len(qualifier_options) == 0:
            return None
        
        # Choose a random rule
        qualifier = random.choice(qualifier_options)
        return AdjacentSelfRule(space_object, qualifier)
    
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
        return str(self.qualifier) + " " + self.space_object1.name() + " is directly opposite another " + \
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
        
        for obj in board:
            if obj is self.space_object:
                num_obj -= 1
            elif obj is None:
                num_none += 1
        
        num_none -= num_obj
                
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
            
            prep_board = self._prepare_board_every(board)
            if prep_board is None:
                return []
            
            num_left = num_obj - sum(obj is self.space_object for obj in prep_board)
            
            if num_left < 0:
                return []
            
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
    
    @classmethod
    def generate_rule(cls, board, constraints, space_object):
        # Some constraints already limit this significantly and would be redundant
        if any((isinstance(constraint, cls) and constraint == cls(space_object, constraint.qualifier))
               or (isinstance(constraint, SectorRule) and constraint.space_object == space_object) 
               for constraint in constraints):
            return None
        
        # Board must have an even number of sectors for objects to be opposite each other
        if len(board) % 2 != 0:
            return None
        
        num_opposite = 0
        half = int(len(board) / 2)
        
        num_obj = board.num_objects()[space_object]
        
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
                    
        if len(qualifier_options) == 0:
            return None
        
        # Choose a random option
        qualifier = random.choice(qualifier_options)
        return OppositeSelfRule(space_object, qualifier)
    
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
    
    @classmethod
    def generate_rule(cls, board, constraints, space_object):
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
        
    def code(self):
        return "B" + str(self.space_object) + str(self.band_size) + self.precision.code()
    
    @classmethod
    def parse(cls, s):
        space_object = SpaceObject.parse(s[1])
        band_size = int(s[2])
        precision = Precision.parse(s[3])
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
        return set(range(self.board_size)) - set(self.positions)
    
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
    
    @classmethod
    def generate_rule(cls, board, constraints, space_object):
        # Will not generate generic rules of this type
        return None
        
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