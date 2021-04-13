import random
from enum import Enum
import itertools
import json

from board import *
from board_type import *
from constraints import *

class Rule:
    @classmethod
    def parse(cls, rule_str):
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

class SelfRule:
    pass

class RelationRule:
    pass

class RuleQualifier(Enum):
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
        if self is RuleQualifier.NONE:
            return "N"
        elif self is RuleQualifier.AT_LEAST_ONE:
            return "A"
        elif self is RuleQualifier.EVERY:
            return "E"
        
    @classmethod
    def parse(cls, s):
        if s == "N":
            return RuleQualifier.NONE
        elif s == "A":
            return RuleQualifier.AT_LEAST_ONE
        elif s == "E":
            return RuleQualifier.EVERY
    
    def to_json(self):
        if self is RuleQualifier.NONE:
            return "NONE"
        elif self is RuleQualifier.AT_LEAST_ONE:
            return "AT_LEAST_ONE"
        elif self is RuleQualifier.EVERY:
            return "EVERY"

class BandRule(SelfRule):
    def __init__(self, space_object, band_size):
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
        board_size = len(board)
        
        longest_run_between = 0
        run_between = 0
        for obj in board:
            if not obj is space_object:
                run_between += 1
            else:
                if run_between > longest_run_between:
                    longest_run_between = run_between
                run_between = 0
        
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
        
        if board.num_objects()[space_object] == 1:
            return None
        
        num_obj = board.num_objects()[space_object]
        band_max = 2 * num_obj + 1 
       
        smallest_band = cls._smallest_band(space_object, board)
        
        if smallest_band > band_max:
            return None
        else:
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
            "qualifier": self.qualifier.to_json(),
            "text": self.text(board)
        }

class OppositeRule(RelationRule):
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
        if len(board) % 2 != 0:
            return None
        
        num_opposite = 0
        half = int(len(board) / 2)
        
        for i, obj in enumerate(board):
            if obj is space_object1:
                if board[i+half] is space_object2:
                    num_opposite += 1
        
        num_object1 = board.num_objects()[space_object1]
        num_object2 = board.num_objects()[space_object2]
        
        if num_opposite == 0:
            qualifier_options = [RuleQualifier.NONE]
        elif num_opposite < num_object1:
            qualifier_options = [RuleQualifier.AT_LEAST_ONE]
        else:
            qualifier_options = [RuleQualifier.AT_LEAST_ONE, RuleQualifier.EVERY]
                    
        if num_object1 == num_object2:
            # This would completely determine one object given the other, too powerful
            qualifier_options = [option for option in qualifier_options \
                                if option is not RuleQualifier.EVERY]

        if num_object1 == 1:
            qualifier_options = [option for option in qualifier_options \
                                    if option is not RuleQualifier.AT_LEAST_ONE]
                    
        if len(qualifier_options) == 0:
            return None
        
        qualifier = random.choice(qualifier_options)
        return OppositeRule(space_object1, space_object2, qualifier)
    
    @classmethod
    def eliminate_sectors(cls, space_object1, space_object2, data, board):
        if len(board) % 2 != 0:
            return None, None
        
        half = int(len(board) / 2)

        obj1_num_opposite = 0
        el_opposite = set()
        
        num_obj1 = board.num_objects()[space_object1]
        num_obj2 = board.num_objects()[space_object2]
        num_el = len(data.need_eliminated)
        
        opposite_objs = [space_object2]
        if data.elimination_object is space_object2:
            opposite_objs.append(space_object1)
        
        for i, obj in enumerate(board):
            if board[i + half] in opposite_objs:
                if obj is space_object1:
                    obj1_num_opposite += 1
                elif obj is space_object2 and i in data.need_eliminated:
                    el_opposite.add(i)
                    
        el_num_opposite = len(el_opposite)
        
        # Uncomment to allow for "Planet X is directly opposite an <obj>" type rules
#         if obj1_num_opposite == num_obj1 and el_num_opposite < num_el:
#             el_positions = set(i for i, obj in enumerate(board) if obj is eliminated_object)
#             eliminated = el_positions - el_opposite - previously_eliminated 
#             if len(eliminated) >= minimum:
#                 rule = OppositeRule(space_object1, space_object2, RuleQualifier.EVERY, num_obj1, num_obj2)
#                 return eliminated, rule, eliminated, rule
        
        if obj1_num_opposite == 0 and el_num_opposite > 0:
            eliminated = el_opposite - data.already_eliminated
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
            "text": self.text(board)
        }

class OppositeSelfRule(SelfRule):
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
        if len(board) % 2 != 0:
            return None
        
        num_opposite = 0
        half = int(len(board) / 2)
        
        num_obj = board.num_objects()[space_object]
        
        # If there is only one object it can't be opposite itself
        if num_obj == 1:
            return None
        
        for i, obj in enumerate(board):
            if obj is space_object:
                if board[i+half] is space_object:
                    num_opposite += 1
        
        
        if num_opposite == 0:
            qualifier_options = [RuleQualifier.NONE]
        elif num_opposite < num_obj:
            qualifier_options = [RuleQualifier.AT_LEAST_ONE]
        else:
            qualifier_options = [RuleQualifier.AT_LEAST_ONE, RuleQualifier.EVERY]

        # Finding one directly finds another, too powerful
        qualifier_options = [option for option in qualifier_options \
                            if option is not RuleQualifier.EVERY]

        if num_obj <= 2:
            # This would completely determine the locations given one of them, too powerful
            qualifier_options = [option for option in qualifier_options \
                                 if option is not RuleQualifier.AT_LEAST_ONE]
                    
        if len(qualifier_options) == 0:
            return None
        
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
            "text": self.text(board)
        }

class AdjacentRule(RelationRule):
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
        # Some are already constrained
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
        
        for i, obj in enumerate(board):
            if obj is space_object1:
                if board[i-1] is space_object2 or board[i+1] is space_object2:
                    num_adjacent += 1
        
        num_object1 = board.num_objects()[space_object1]
        num_object2 = board.num_objects()[space_object2]
        
        if num_adjacent == 0:
            qualifier_options = [RuleQualifier.NONE]
        elif num_adjacent < num_object1:
            qualifier_options = [RuleQualifier.AT_LEAST_ONE]
        else:
            qualifier_options = [RuleQualifier.AT_LEAST_ONE, RuleQualifier.EVERY]
        
        # At least one just means every
        if num_object1 == 1:
            qualifier_options = [option for option in qualifier_options \
                                if option is not RuleQualifier.AT_LEAST_ONE]
        
        # Finding one object2 finds all object3s
        if num_object1 >= 2 * num_object2:
            qualifier_options = [option for option in qualifier_options \
                                if option is not RuleQualifier.AT_LEAST_ONE]
            
        if len(qualifier_options) == 0:
            return None
        
        qualifier = random.choice(qualifier_options)
        return AdjacentRule(space_object1, space_object2, qualifier)
    
    @classmethod
    def eliminate_sectors(cls, space_object1, space_object2, data, board):        
        obj1_num_adjacent = 0
        el_adjacent = set()
        
        num_obj1 = board.num_objects()[space_object1]
        num_obj2 = board.num_objects()[space_object2]
        num_el = len(data.need_eliminated)
        
        adjacent_objs = [space_object2]
        if data.elimination_object is space_object2:
            adjacent_objs.append(space_object1)
        
        for i, obj in enumerate(board):
            if board[i-1] in adjacent_objs or board[i+1] in adjacent_objs:
                if obj is space_object1:
                    obj1_num_adjacent += 1
                elif obj is data.elimination_object and i in data.need_eliminated:
                    el_adjacent.add(i)
                    
        el_num_adjacent = len(el_adjacent)

        # Uncomment to allow "Planet X is adjacent to a <obj>" type rules
#         if obj1_num_adjacent == num_obj1 and el_num_adjacent < num_el:
#             el_positions = set(i for i, obj in enumerate(board) if obj is eliminated_object)
#             eliminated = el_positions - el_adjacent - previously_eliminated
#             if len(eliminated) >= minimum:
#                 rule = AdjacentRule(space_object1, space_object2, RuleQualifier.EVERY, num_obj1, num_obj2)
#                 return eliminated, rule, eliminated, rule
        
        if obj1_num_adjacent == 0 and el_num_adjacent > 0:
            eliminated = el_adjacent - data.already_eliminated
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
            "text": self.text(board)
        }

class AdjacentSelfRule(SelfRule):
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
            "text": self.text(board)
        }

class WithinRule(RelationRule):
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
        dist = abs(i - j)
        return min(dist, size - dist)
    
    @staticmethod
    def _max_min_sectors_away(space_object1, space_object2, board):
        board_size = len(board)
        obj1_positions = [i for i, obj in enumerate(board) if obj is space_object1]
        obj2_positions = [i for i, obj in enumerate(board) if obj is space_object2]
        
        maximum_sectors = 0
        minimum_sectors = board_size
        for i in obj1_positions:
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
            num_not_within = random.randrange(2, min_sectors)
            options.append((RuleQualifier.NONE, num_not_within))
        
        if max_sectors <= max_n:
            num_within = random.randrange(max(2, max_sectors), max_n+1)
            options.append((RuleQualifier.EVERY, num_within))
            
        if len(options) == 0:
            return None
        
        qualifier, num_sectors = random.choice(options)
        return WithinRule(space_object1, space_object2, qualifier, num_sectors)
    
    @classmethod
    def eliminate_sectors(cls, space_object1, space_object2, data, board):
        max_n = int(len(board)/3 - 1)
        board_size = len(board)
        obj1_positions = [i for i, obj in enumerate(board) if obj is space_object1]
        el_positions = data.need_eliminated
        obj2_positions = [i for i, obj in enumerate(board) if obj is space_object2]
        
        if data.elimination_object is space_object2:
            obj2_positions += obj1_positions
        
        max_obj1 = 0
        min_obj1 = board_size
        for i in obj1_positions:
            sectors_away = min(WithinRule._circle_dist(i, j, board_size) for j in obj2_positions if j != i)
            if sectors_away > max_obj1:
                max_obj1 = sectors_away
            if sectors_away < min_obj1:
                min_obj1 = sectors_away
        
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
                eliminated = set(i for idx_list in el_sectors_away[sectors_away+1:] for i in idx_list)
                if len(eliminated) > 0:
                    eliminated -= data.already_eliminated
                    options.append((sectors_away, eliminated, RuleQualifier.EVERY))
            if sectors_away < max_obj1:
                eliminated = set(i for idx_list in el_sectors_away[:sectors_away+1] for i in idx_list)
                if len(eliminated) > 0:
                    eliminated -= data.already_eliminated
                    options.append((sectors_away, eliminated, RuleQualifier.NONE))

        if len(options) == 0:
            return None, None
                
        max_num_eliminated = max(len(eliminated) for sectors, eliminated, qualifier in options)
        
        if max_num_eliminated >= data.goal:
            options = [option for option in options if len(option[1]) >= data.goal]
           
        options = [option for option in options if len(option[1]) >= data.minimum]

        if len(options) == 0:
            return None, None
        
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
            "text": self.text(board)
        }

class EliminationData:
    def __init__(self, space_object, minimum, goal, need_eliminated, already_eliminated):
        self.elimination_object = space_object
        self.minimum = minimum
        self.goal = goal
        self.need_eliminated = need_eliminated
        self.already_eliminated = already_eliminated

class Equinox(Enum):
    WINTER = 0
    SPRING = 1
    SUMMER = 2
    FALL = 3
    
    def to_json(self):
        return self.name

class EliminationClue:
    def __init__(self, sector_number, eliminated_object):
        self.sector_num = sector_number
        self.eliminated_obj = eliminated_object
        
    def sector_number(self):
        return self.sector_num
    
    def eliminated_object(self):
        return self.eliminated_obj
    
    def code(self):
        return chr(65 + self.sector_number()) + str(self.eliminated_object())
    
    @classmethod
    def parse(cls, s):
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
    def __init__(self, clues):
        self.clues = clues

    @classmethod
    def generate_info(cls, board, constraints, num_clues=None):
        clue_options = {}
        normal_types = [obj for obj in board.num_objects().keys() if obj is not SpaceObject.PlanetX \
                       and obj is not SpaceObject.Empty]
        
        for i, obj in enumerate(board):
            clue_options[i] = [obj_type for obj_type in normal_types if obj is not obj_type]
            
        if num_clues is None:
            num_clues = len(board)
            
        limiting_constraints = [constraint for constraint in constraints if constraint.is_immediately_limiting()]
        for constraint in limiting_constraints:
            for obj, invalid_sectors in constraint.disallowed_sectors():
                for sector in invalid_sectors:
                    if obj in clue_options[sector]:
                        clue_options[sector].remove(obj)
                        
        object_counts = dict()
        for sector in clue_options:
            for obj in clue_options[sector]:
                if obj in object_counts:
                    object_counts[obj] += 1
                else:
                    object_counts[obj] = 1
        
        object_weights = { obj: 1/object_counts[obj] for obj in object_counts }
                
        clues = {}
        for equinox in Equinox:
            clues[equinox] = []
            sectors = random.sample(range(len(board)), len(board))
            for sector in sectors:
                if len(clue_options[sector]) == 0:
                    continue
                
                if len(clues[equinox]) == num_clues:
                    break

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
    MAX_SINGULAR_RULES = 2
    RELATION_RULES = [OppositeRule, AdjacentRule, WithinRule]
    SINGULAR_RULES = [BandRule, OppositeSelfRule, AdjacentSelfRule]
    EMPTY_RULES = [AdjacentRule]
    
    def __init__(self, rules):
        self.rules = rules
    
    @staticmethod
    def generate_research(board, num_rules):
        rules = []
        total_singular_rules = random.randrange(Research.MAX_SINGULAR_RULES+1)
        
        normal_types = [obj for obj in board.num_objects().keys() if obj \
                        is not SpaceObject.PlanetX and obj is not SpaceObject.Empty]
        singular_types = normal_types + [(obj, SpaceObject.Empty) for obj in normal_types]
        pair_types = list(itertools.combinations(normal_types, 2))
        
        random.shuffle(singular_types)
        random.shuffle(pair_types)
        
        num_rule_types = len(Research.RELATION_RULES) + len(Research.SINGULAR_RULES)
        rule_weight = math.ceil(num_rules * 1.5/num_rule_types)
        rule_weights = { rule_type: rule_weight for rule_type in Research.RELATION_RULES + Research.SINGULAR_RULES }
        
        num_singular_rules = 0
        while num_singular_rules < total_singular_rules and len(singular_types):
            object_type = singular_types.pop()
            if type(object_type) is SpaceObject:
                rule_choices = [rule.generate_rule(object_type, board) \
                                for rule in Research.SINGULAR_RULES]
            else:
                rule_choices = [rule.generate_rule(object_type[0], object_type[1], board) \
                               for rule in Research.EMPTY_RULES]
            rule_choices = [rule for rule in rule_choices if rule is not None]
            weights = [rule_weights[type(rule)] for rule in rule_choices]
            if len(rule_choices):
                new_rule = random.choices(rule_choices, weights=weights)[0]
                if rule_weights[type(new_rule)] > 1:
                    rule_weights[type(new_rule)] -= 1
                rules.append(new_rule)
            num_singular_rules += 1
        
        while len(rules) < num_rules and len(pair_types):
            object1, object2 = pair_types.pop()
            rule_choices = [rule.generate_rule(object1, object2, board) \
                           for rule in Research.RELATION_RULES]
            rule_choices.extend([rule.generate_rule(object2, object1, board) \
                                for rule in Research.RELATION_RULES])
            rule_choices = [rule for rule in rule_choices if rule is not None]
            weights = [rule_weights[type(rule)] for rule in rule_choices]
            if len(rule_choices):
                new_rule = random.choices(rule_choices, weights=weights)[0]
                if rule_weights[type(new_rule)] > 1:
                    rule_weights[type(new_rule)] -= 1
                rules.append(new_rule)
        
        random.shuffle(rules)
        
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
    RELATION_RULES = [OppositeRule, AdjacentRule, WithinRule]
    
    def __init__(self, rules):
        self.rules = rules
    
    @staticmethod
    def generate_conference(board, constraints, num_rules):
        obj_types = [obj for obj in board.num_objects().keys() if obj is not SpaceObject.PlanetX ]
        possible_rules = [(obj, rule_type) \
                          for obj in obj_types for rule_type in Conference.RELATION_RULES]
        
#         random.shuffle(possible_rules)
        
        rules = []
        elimination_sectors = set(i for i, obj in enumerate(board) if obj is SpaceObject.Empty)
        
        planetx_position = board.objects.index(SpaceObject.PlanetX)
        for i, obj in enumerate(board):
            if obj is SpaceObject.Empty:
                board_copy = board.copy()
                board_copy[planetx_position] = SpaceObject.Empty
                board_copy[i] = SpaceObject.PlanetX
                if not board_copy.check_constraints(constraints):
                    elimination_sectors.remove(i)
        
        sectors_left = copy(elimination_sectors)
        eliminated = set()
        
        goal = math.ceil(len(sectors_left)/num_rules)
        minimum = goal
                                  
        for i in range(num_rules):
            for j, (obj, rule_type) in enumerate(possible_rules):
                elimination_data = EliminationData(SpaceObject.Empty, minimum, goal, elimination_sectors, eliminated)
                eliminates, rand_rule = rule_type.eliminate_sectors(SpaceObject.PlanetX, obj, elimination_data, board)
                
                if rand_rule is not None and len(eliminates) >= minimum:
                    rules.append(rand_rule)
                    possible_rules = [rule for rule in possible_rules if rule[0] is not obj]
                        
                    eliminated |= eliminates
                    sectors_left -= eliminates
                    rules_left = num_rules - i - 1
                    if rules_left > 0:
                        minimum = math.ceil(len(sectors_left)/rules_left)
                    break
        
        if len(sectors_left) == 0:
            for i in range(num_rules - len(rules)):
                for obj, rule_type in possible_rules:
                    rule = rule_type.generate_rule(SpaceObject.PlanetX, obj, board)
                    if rule is not None:
                        possible_rules = [rule for rule in possible_rules if rule[0] is not obj]
                        rules.append(rule)
                        break                 

        random.shuffle(rules)
        
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
    def __init__(self, board, starting_info, research, conference):
        self.board = board
        self.starting_info = starting_info
        self.research = research
        self.conference = conference
    
    @classmethod
    def generate_from_board(cls, board, board_type):
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
        s = ""
        s += str(len(self.board)) + "&"
        s += str(self.board) + "&"
        s += self.research.code() + "&"
        s += self.conference.code() + "&"
        s += self.starting_info.code()
        return s
    
    @classmethod
    def parse(cls, s):
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