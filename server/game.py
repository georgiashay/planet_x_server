import random
from enum import Enum
import itertools
import json

from .board import *
from .board_type import *
from .constraints import *

class Rule:
    """
    Represents a rule describing where objects are on the board.
    """
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
        
    def category_name(self):
        """
        Returns the category name for the rule, e.g. "Gas Clouds & Asteroids"
        """
        objs = self.space_objects()
        if objs[-1] is SpaceObject.Empty:
            objs = objs[:-1]
        obj_titles = [obj.category() for obj in objs]
        return " & ".join(obj_titles)

class SelfRule(Rule):
    """
    A rule that relates one type of space object to other objects of the same type
    """
    def space_objects(self):
        """
        Returns all the space objects involved in this rule
        """
        return [self.space_object]

class RelationRule(Rule):
    """
    A rule that relates one type of space object to another
    """
    def space_objects(self):
        """
        Returns all the space objects involved in this rule
        """
        return [self.space_object1, self.space_object2]

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

class BandRule(SelfRule):
    """
    A type of rule which states that a specific type of object are in a band of a certain number
    of sectors.
    """
    def __init__(self, space_object, band_size):
        """
        Creates a BandRule stating that the space_objects are in a band of size band_size
        """
        self.space_object = space_object
        self.band_size = band_size
        
    def __repr__(self):
        return "<" + repr(self.space_object) + ", band: " + str(self.band_size) + ">"
    
    def __str__(self):
        return "The " + self.space_object.plural() + " are in a band of " + str(self.band_size) + "."
    
    def text(self, board):
        return str(self)
    
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
        
    @classmethod
    def generate_rule(cls, space_object, board):
        # Dwarf planets are already in a band
        if space_object is SpaceObject.DwarfPlanet:
            return None
        
        # Must be at least 2 objects to have a band rule
        if board.num_objects()[space_object] == 1:
            return None
        
        num_obj = board.num_objects()[space_object]
        # Won't generate a rule for too large of a band
        band_max = 2 * num_obj + 1 
       
        smallest_band = cls._smallest_band(space_object, board)
        
        if smallest_band > band_max:
            return None
        else:
            # Generate a random band size up to the max 
            # (The space objects are still within this size)
            rand_band = random.randint(smallest_band, band_max)
            return BandRule(space_object, rand_band)
        
    def code(self):
        return "B" + str(self.space_object) + str(self.band_size)
    
    @classmethod
    def parse(cls, s):
        space_object = SpaceObject.parse(s[1])
        band_size = int(s[2])
        return cls(space_object, band_size)
    
    def to_json(self, board):
        return {
            "ruleType": "BAND",
            "spaceObject": self.space_object.to_json(),
            "numSectors": self.band_size,
            "categoryName": self.category_name(),
            "text": self.text(board)
        }

class OppositeRule(RelationRule):
    """
    A rule stating that two types of objects are or are not opposite each other on the board
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
        
    @classmethod
    def generate_rule(cls, space_object1, space_object2, board):
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
    def eliminate_sectors(cls, space_object1, space_object2, data, board):
        """
        Create a rule that will eliminate possible positions of space_object1, where 
        space_object1 and data.elimination_object are ambiguous on survey/target
        
        Only the sectors in data.need_eliminated are ambiguous, and the sectors in 
        data.already_eliminated have been eliminated by other rules. To be viable,
        this rule must eliminate at least data.minimum sectors, and if possible 
        should eliminate data.goal sectors.
        """
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
                    
        el_num_opposite = len(el_opposite)
        
        # Uncomment to allow for "Planet X is directly opposite an <obj>" type rules
#         if obj1_num_opposite == num_obj1 and el_num_opposite < num_el:
#             el_positions = set(i for i, obj in enumerate(board) if obj is eliminated_object)
#             eliminated = el_positions - el_opposite - previously_eliminated 
#             if len(eliminated) >= minimum:
#                 rule = OppositeRule(space_object1, space_object2, RuleQualifier.EVERY, num_obj1, num_obj2)
#                 return eliminated, rule, eliminated, rule
        
        # Only allowing "not opposite" rules, since "is directly opposite" rules would be too powerful
        # This means that no object1s can appear to be opposite an object2 for this rule to be viable
        if obj1_num_opposite == 0 and el_num_opposite > 0:
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

class OppositeSelfRule(SelfRule):
    """
    A rule that some object is or is not opposite itself
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
    
    @classmethod
    def generate_rule(cls, space_object, board):
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
    
    @classmethod
    def generate_rule(cls, space_object1, space_object2, board):
        # Some are already constrained, don't generate these rules
        if (space_object1, space_object2) in {
            (SpaceObject.GasCloud, SpaceObject.Empty),
            (SpaceObject.PlanetX, SpaceObject.DwarfPlanet),
            (SpaceObject.DwarfPlanet, SpaceObject.PlanetX),
            (SpaceObject.BlackHole, SpaceObject.PlanetX),
            (SpaceObject.PlanetX, SpaceObject.BlackHole),
            (SpaceObject.BlackHole, SpaceObject.Empty)
        }:
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
    def eliminate_sectors(cls, space_object1, space_object2, data, board):  
        """
        Create a rule that will eliminate possible positions of space_object1, where 
        space_object1 and data.elimination_object are ambiguous on survey/target
        
        Only the sectors in data.need_eliminated are ambiguous, and the sectors in 
        data.already_eliminated have been eliminated by other rules. To be viable,
        this rule must eliminate at least data.minimum sectors, and if possible 
        should eliminate data.goal sectors.
        """
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
                    
        el_num_adjacent = len(el_adjacent)

        # Uncomment to allow "Planet X is adjacent to a <obj>" type rules
#         if obj1_num_adjacent == num_obj1 and el_num_adjacent < num_el:
#             el_positions = set(i for i, obj in enumerate(board) if obj is eliminated_object)
#             eliminated = el_positions - el_adjacent - previously_eliminated
#             if len(eliminated) >= minimum:
#                 rule = AdjacentRule(space_object1, space_object2, RuleQualifier.EVERY, num_obj1, num_obj2)
#                 return eliminated, rule, eliminated, rule
        
        # Only using "not adjacent" rules to avoid too powerful rules
        # There must be no object 1's ajacent to an 'object 2' 
        if obj1_num_adjacent == 0 and el_num_adjacent > 0:
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

class AdjacentSelfRule(SelfRule):
    """
    A rule stating that a type of object is or is not adjacent to the same type of object
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
    
    @classmethod
    def generate_rule(cls, space_object, board):
        # Their original rules already limit this significantly, would be redundant
        if space_object is SpaceObject.Comet or space_object is SpaceObject.Asteroid:
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

class WithinRule(RelationRule):
    """
    A rule stating that an object is or is not within a certain number of sectors of another object
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
    
    @classmethod
    def generate_rule(cls, space_object1, space_object2, board):
        num_object1 = board.num_objects()[space_object1]
        num_object2 = board.num_objects()[space_object2]
        
        # There must be more of object 2 (or at least the same amount) than object 1
        if num_object1 > num_object2:
            return None
        
        max_n = int(len(board)/3 - 1)
        
        min_sectors, max_sectors = cls._max_min_sectors_away(space_object1, space_object2, board)
        
        options = []
        
        if min_sectors > 2:
            # Create a random number of sectors that no object1 is within object2
            # This must be < min_sectors, because object1 is within that many sectors of object2.
            num_not_within = random.randrange(2, min_sectors)
            options.append((RuleQualifier.NONE, num_not_within))
        
        if max_sectors <= max_n:
            # Create a random number of sectors that every object1 is within object2
            # This must be at least max_sectors, to cover every possible object1
            num_within = random.randrange(max(2, max_sectors), max_n+1)
            options.append((RuleQualifier.EVERY, num_within))
            
        if len(options) == 0:
            return None
        
        # Choose a random rule
        qualifier, num_sectors = random.choice(options)
        return WithinRule(space_object1, space_object2, qualifier, num_sectors)
    
    @classmethod
    def eliminate_sectors(cls, space_object1, space_object2, data, board):
        """
        Create a rule that will eliminate possible positions of space_object1, where 
        space_object1 and data.elimination_object are ambiguous on survey/target
        
        Only the sectors in data.need_eliminated are ambiguous, and the sectors in 
        data.already_eliminated have been eliminated by other rules. To be viable,
        this rule must eliminate at least data.minimum sectors, and if possible 
        should eliminate data.goal sectors.
        """
        max_n = int(len(board)/3 - 1)
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
        
        el_sectors_away = el_sectors_away[:max_n+1]
        
        options = []
        for sectors_away, matching_el_indices in enumerate(el_sectors_away):
            if sectors_away < 2:
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

class EliminationData:
    """
    A structure representing the objects that need eliminated as potential candidates for
    another object (Planet X)
    """
    def __init__(self, space_object, minimum, goal, need_eliminated, already_eliminated):
        self.elimination_object = space_object
        self.minimum = minimum
        self.goal = goal
        self.need_eliminated = need_eliminated
        self.already_eliminated = already_eliminated

class Equinox(Enum):
    """
    Represents a season on the board - i.e. one player
    """
    WINTER = 0
    SPRING = 1
    SUMMER = 2
    AUTUMN = 3
    
    def to_json(self):
        return self.name

class EliminationClue:
    """
    Represents a clue of the form "Sector n does not contain a <space object>" which
    are given at the beginning of the game
    """
    def __init__(self, sector_number, eliminated_object):
        """
        Creates an elimination clue that eliminates eliminated_object in sector sector_number
        """
        self.sector_num = sector_number
        self.eliminated_obj = eliminated_object
        
    def sector_number(self):
        """
        Returns the sector number for this clue
        """
        return self.sector_num
    
    def eliminated_object(self):
        """
        Returns what object this clue eliminates
        """
        return self.eliminated_obj
    
    def code(self):
        """
        Returns the two character code for this clue
        """
        return chr(65 + self.sector_number()) + str(self.eliminated_object())
    
    @classmethod
    def parse(cls, s):
        """
        Parses a two character code s and returns its corresponding EliminationClue
        """
        sector_code, object_code = s
        sector_number = ord(sector_code) - 65
        eliminated_object = SpaceObject.parse(object_code)
        return EliminationClue(sector_number, eliminated_object)
    
    def __repr__(self):
        return "<EliminationClue: no " + repr(self.eliminated_obj) + " in sector " + str(self.sector_num) + ">"
    
    def __str__(self):
        return "Sector " + str(self.sector_num+1) + " does not contain " + self.eliminated_obj.one() + \
                " " + self.eliminated_obj.name() + "."
    
    def to_json(self):
        return {
            "sector": self.sector_num,
            "eliminatedObject": self.eliminated_obj.to_json(),
            "text": str(self)
        }

class StartingInformation:
    """
    Represents the starting information for a game. By default, each player has elimination clues for the 
    full length of the board, which are truncated when they choose a difficulty.
    """
    def __init__(self, clues):
        self.clues = clues

    @classmethod
    def generate_info(cls, board, constraints, num_clues=None):
        """
        Generates a set of starting information given a board and a set of constraints for that board.
        """
        clue_options = {}
        # Do not eliminate empty sectors or Planet X
        normal_types = [obj for obj in board.num_objects().keys() if obj is not SpaceObject.PlanetX \
                       and obj is not SpaceObject.Empty]
        
        # List possible objects to be eliminated in each sector
        for i, obj in enumerate(board):
            clue_options[i] = [obj_type for obj_type in normal_types if obj is not obj_type]
            
        if num_clues is None:
            num_clues = len(board)
        
        # If a sector never has a specific type of object according to the constraints, don't
        # provide an elimination clue for it in that sector
        limiting_constraints = [constraint for constraint in constraints if constraint.is_immediately_limiting()]
        for constraint in limiting_constraints:
            for obj, invalid_sectors in constraint.disallowed_sectors():
                for sector in invalid_sectors:
                    if obj in clue_options[sector]:
                        clue_options[sector].remove(obj)
              
        # Get the count of possible elimination clues for each object type
        object_counts = dict()
        for sector in clue_options:
            for obj in clue_options[sector]:
                if obj in object_counts:
                    object_counts[obj] += 1
                else:
                    object_counts[obj] = 1
        
        # Weight the objects according to a distribution that would make the clues more
        # even in their type of objects
        object_weights = { obj: 1/object_counts[obj] for obj in object_counts }
                
        clues = {}
        for equinox in Equinox:
            clues[equinox] = []
            # Randomly order the sectors for each season
            sectors = random.sample(range(len(board)), len(board))
            for sector in sectors:
                # If there are no clues left for a sector, continue
                if len(clue_options[sector]) == 0:
                    continue
                
                # Stop when there are enough clues
                if len(clues[equinox]) == num_clues:
                    break

                # Choose a random clue for this sector according to the weight distribution
                weights = [object_weights[obj] for obj in clue_options[sector]]
                eliminated_object = random.choices(clue_options[sector], weights=weights)[0]
                clues[equinox].append(EliminationClue(sector, eliminated_object))
                
        return StartingInformation(clues)
    
    def __str__(self):
        s = ""
        for equinox in self.clues:
            s += equinox.name + "\n"
            for clue in self.clues[equinox]:
                s += str(clue) + "\n"
            s += "\n"
        return s[:-1]
    
    def code(self):
        equinoxes = []
        # Equinox order: winter, spring, summer, fall
        # Join the clues with a | between each season, and no delimiter between the 
        # two-character clue codes
        for equinox in Equinox:
            codes = "".join(clue.code() for clue in self.clues[equinox])
            equinoxes.append(codes)
        return "|".join(equinoxes)
    
    @classmethod
    def parse(cls, s):
        clue_strs = s.split("|")
        clues = {}
        for equinox, clue_str in zip(Equinox, clue_strs):
            equinox_clues = []
            for i in range(0, len(clue_str), 2):
                equinox_clues.append(EliminationClue.parse(clue_str[i:i+2]))
            clues[equinox] = equinox_clues
        return cls(clues)
    
    def to_json(self):
        return {
            equinox.to_json(): [
                clue.to_json() for clue in self.clues[equinox]
            ]
            for equinox in self.clues
        }

class Research:
    """
    Represents the research rules for a game
    """
    MAX_SINGULAR_RULES = 2
    RELATION_RULES = [OppositeRule, AdjacentRule, WithinRule]
    SINGULAR_RULES = [BandRule, OppositeSelfRule, AdjacentSelfRule]
    EMPTY_RULES = [AdjacentRule]
    
    def __init__(self, rules):
        self.rules = rules
    
    @staticmethod
    def generate_research(board, num_rules):
        """
        Generate a certain number of rules for a board
        """
        rules = []
        # Choose how many singular rules to include on the board (if possible)
        total_singular_rules = random.randrange(Research.MAX_SINGULAR_RULES+1)
        
        # Rules are not about Planet X or empty sectors
        normal_types = [obj for obj in board.num_objects().keys() if obj \
                        is not SpaceObject.PlanetX and obj is not SpaceObject.Empty]
        
        # Singular rules are either about one object or that object related to empty sectors
        singular_types = normal_types + [(obj, SpaceObject.Empty) for obj in normal_types]
        # Pair rules combine any two normal objects (not Planet X or empty sectors)
        pair_types = list(itertools.combinations(normal_types, 2))
        
        # Shuffle the rule types
        random.shuffle(singular_types)
        random.shuffle(pair_types)
        
        # Subtly weight the rules against repeating the same rule type
        # Weights are decreased when the rule type is used, but don't go to 0.
        num_rule_types = len(Research.RELATION_RULES) + len(Research.SINGULAR_RULES)
        rule_weight = math.ceil(num_rules * 1.5/num_rule_types)
        rule_weights = { rule_type: rule_weight for rule_type in Research.RELATION_RULES + Research.SINGULAR_RULES }
        
        # Create singular rules
        num_singular_rules = 0
        while num_singular_rules < total_singular_rules and len(singular_types):
            object_type = singular_types.pop()
            if type(object_type) is SpaceObject:
                # Try to generate a singular rule for any singular rule type
                rule_choices = [rule.generate_rule(object_type, board) \
                                for rule in Research.SINGULAR_RULES]
            else:
                # Try to generate a pair rule for the type and an empty sector for any empty rule type
                rule_choices = [rule.generate_rule(object_type[0], object_type[1], board) \
                               for rule in Research.EMPTY_RULES]
                
            # Pick one of the rules randomly according to the weights
            rule_choices = [rule for rule in rule_choices if rule is not None]
            weights = [rule_weights[type(rule)] for rule in rule_choices]
            if len(rule_choices):
                new_rule = random.choices(rule_choices, weights=weights)[0]
                # Decrease weight for this rule type
                if rule_weights[type(new_rule)] > 1:
                    rule_weights[type(new_rule)] -= 1
                rules.append(new_rule)
            num_singular_rules += 1
        
        # Generate pair rules
        while len(rules) < num_rules and len(pair_types):
            object1, object2 = pair_types.pop()
            # Generate pair rules for both orderings of object 1 and 2
            rule_choices = [rule.generate_rule(object1, object2, board) \
                           for rule in Research.RELATION_RULES]
            rule_choices.extend([rule.generate_rule(object2, object1, board) \
                                for rule in Research.RELATION_RULES])
            rule_choices = [rule for rule in rule_choices if rule is not None]
            
            # Pick one of the rules randomly according to the weightss
            weights = [rule_weights[type(rule)] for rule in rule_choices]
            if len(rule_choices):
                # Decrease the weight for this rule type
                new_rule = random.choices(rule_choices, weights=weights)[0]
                if rule_weights[type(new_rule)] > 1:
                    rule_weights[type(new_rule)] -= 1
                rules.append(new_rule)
        
        random.shuffle(rules)
        
        # Only return research if we were able to generate enough rules
        if len(rules) == num_rules:
            return Research(rules)
        else:
            return None
        
    def __str__(self):
        s = ""
        for i, rule in enumerate(self.rules):
            s += chr(65+i) + ". "
            s += str(rule)
            s += "\n"
        return s[:-1]
    
    def text(self, board):
        s = ""
        for i, rule in enumerate(self.rules):
            s += chr(65+i) + ". "
            s += rule.text(board)
            s += "\n"
        return s[:-1]
    
    def code(self):
        return "|".join(rule.code() for rule in self.rules)

    @classmethod
    def parse(cls, s):
        rule_strs = s.split("|")
        rules = [Rule.parse(rule_str) for rule_str in rule_strs]
        return cls(rules)
    
    def to_json(self, board):
        return [rule.to_json(board) for rule in self.rules]

class Conference:
    """
    Represents the conference rules for a game
    """
    RELATION_RULES = [OppositeRule, AdjacentRule, WithinRule]
    
    def __init__(self, rules):
        self.rules = rules
    
    @staticmethod
    def generate_conference(board, constraints, num_rules):
        """
        Generate a certain number of conference rules given a board and its constraints
        """
        # List all possible object types for the rule: Planet X and anything else 
        obj_types = [obj for obj in board.num_objects().keys() if obj is not SpaceObject.PlanetX ]
        possible_rules = [(obj, rule_type) \
                          for obj in obj_types for rule_type in Conference.RELATION_RULES]
        
        random.shuffle(possible_rules)
        
        rules = []
        # Must eliminate all empty sectors, since they look like Planet X
        elimination_sectors = set(i for i, obj in enumerate(board) if obj is SpaceObject.Empty)
        
        # Pre-eliminate all sectors that are impossible to be Planet X based on other constraints
        planetx_position = board.objects.index(SpaceObject.PlanetX)
        for i, obj in enumerate(board):
            if obj is SpaceObject.Empty:
                board_copy = board.copy()
                board_copy[planetx_position] = SpaceObject.Empty
                board_copy[i] = SpaceObject.PlanetX
                if not board_copy.check_constraints(constraints):
                    elimination_sectors.remove(i)
        
        # Keep track of which sectors have and have not been eliminated
        sectors_left = copy(elimination_sectors)
        eliminated = set()
        
        # Must eliminate at least ceil(# sectors left/# rules left) each time we choose a rule
        goal = math.ceil(len(sectors_left)/num_rules)
        minimum = goal
                                  
        for i in range(num_rules):
            for j, (obj, rule_type) in enumerate(possible_rules):
                # Try to eliminate sectors with this rule type
                elimination_data = EliminationData(SpaceObject.Empty, minimum, goal, elimination_sectors, eliminated)
                eliminates, rand_rule = rule_type.eliminate_sectors(SpaceObject.PlanetX, obj, elimination_data, board)
                
                # If it eliminates enough sectors, add it to the rule list
                if rand_rule is not None and len(eliminates) >= minimum:
                    rules.append(rand_rule)
                    possible_rules = [rule for rule in possible_rules if rule[0] is not obj]
                    
                    # Update what sectors need to be eliminated going forward
                    eliminated |= eliminates
                    sectors_left -= eliminates
                    rules_left = num_rules - i - 1
                    if rules_left > 0:
                        minimum = math.ceil(len(sectors_left)/rules_left)
                    break
        
        # If there are no sectors left to eliminate, generate any possible rules (no restrictions on 
        # sectors to eliminate)
        if len(sectors_left) == 0:
            for i in range(num_rules - len(rules)):
                for obj, rule_type in possible_rules:
                    rule = rule_type.generate_rule(SpaceObject.PlanetX, obj, board)
                    if rule is not None:
                        possible_rules = [rule for rule in possible_rules if rule[0] is not obj]
                        rules.append(rule)
                        break                 

        random.shuffle(rules)
        
        # Only return a conference if we are able to generate enough rules
        if len(rules) == num_rules:
            return Conference(rules)
        else:
            return None
    
    def __str__(self):
        s = ""
        for i, rule in enumerate(self.rules):
            s += "X" + str(i+1) + ". "
            s += str(rule)
            s += "\n"
        return s[:-1]
    
    def text(self, board):
        s = ""
        for i, rule in enumerate(self.rules):
            s += "X" + str(i+1) + ". "
            s += rule.text(board)
            s += "\n"
        return s[:-1]
    
    def code(self):
        return "|".join(rule.code() for rule in self.rules)
    
    @classmethod
    def parse(cls, s):
        rule_strs = s.split("|")
        rules = [Rule.parse(rule_str) for rule_str in rule_strs]
        return cls(rules)
    
    def to_json(self, board):
        return [rule.to_json(board) for rule in self.rules]

class Game:
    """
    Represents a game - including the board, starting information,
    research rules, and conference rules
    """
    def __init__(self, board, starting_info, research, conference):
        self.board = board
        self.starting_info = starting_info
        self.research = research
        self.conference = conference
    
    @classmethod
    def generate_from_board(cls, board, board_type):
        """
        Generate an entire game given a board
        """
        starting_info = StartingInformation.generate_info(board, board_type.constraints)
        research = Research.generate_research(board,board_type.num_research)
        conference = Conference.generate_conference(board, board_type.constraints, board_type.num_conference)
        if research is None or conference is None:
            return None
        return Game(board, starting_info, research, conference)
    
    def __str__(self):
        s = ""
        s += "Board: " + str(self.board) + "\n\n"
        s += "Research:\n"
        s += self.research.text(self.board) + "\n\n"
        s += "Conference:\n"
        s += self.conference.text(self.board) + "\n\n"
        s += "Starting Information:\n"
        s += str(self.starting_info)
        return s
        
    def code(self):
        """
        Compressed string representation of the game
        """
        s = ""
        s += str(len(self.board)) + "&"
        s += str(self.board) + "&"
        s += self.research.code() + "&"
        s += self.conference.code() + "&"
        s += self.starting_info.code()
        return s
    
    @classmethod
    def parse(cls, s):
        """
        Parse the game from a compressed string representation
        """
        components = s.split("&")
        board_size = int(components[0])
        board = Board.parse(components[1])
        research = Research.parse(components[2])
        conference = Conference.parse(components[3])
        starting_info = StartingInformation.parse(components[4])
        return cls(board, starting_info, research, conference)
    
    def to_json(self):
        return {
            "board": self.board.to_json(),
            "research": self.research.to_json(self.board),
            "conference": self.conference.to_json(self.board),
            "startingInformation": self.starting_info.to_json()
        }