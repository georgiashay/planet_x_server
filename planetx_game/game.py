import random
from enum import Enum
import itertools
import json

from .board import *
from .board_type import *
from .rules import *

ALLOW_OBJ_EMPTY_RESEARCH = True

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

                # Choose a random clue for this sector
                eliminated_object = random.choice(clue_options[sector])
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
    def generate_research(board, constraints, num_rules):
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
        singular_rules = [rule.generate_rule(board, constraints, [], obj) 
                          for rule in Research.SINGULAR_RULES for obj in normal_types]
        
        if ALLOW_OBJ_EMPTY_RESEARCH:
            singular_rules += [rule.generate_rule(board, constraints, [], obj, SpaceObject.Empty) 
                               for rule in Research.EMPTY_RULES for obj in normal_types]
            
        singular_rules = [rule for rule in singular_rules if rule is not None]
        singular_strengths = [rule.base_strength(board) for rule in singular_rules]
            
        # Pair rules combine any two normal objects (not Planet X or empty sectors)
        pair_types = list(itertools.combinations(normal_types, 2))
        
        pair_rules = [rule.generate_rule(board, constraints, [], obj1, obj2) for rule in Research.RELATION_RULES
                      for (obj1, obj2) in pair_types]
        pair_rules += [rule.generate_rule(board, constraints, [], obj2, obj1) for rule in Research.RELATION_RULES
                       for (obj1, obj2) in pair_types]
        pair_rules = [rule for rule in pair_rules if rule is not None]
        pair_strengths = [rule.base_strength(board) for rule in pair_rules]
            
        rules = []
        while len(rules) < total_singular_rules and len(singular_rules) > 0:
            i = random.choices(range(len(singular_rules)), k=1, weights=singular_strengths)[0]
            if singular_rules[i].allowed_rule(board.num_objects(), constraints, rules):
                rules.append(singular_rules[i])
            singular_rules.pop(i)
            singular_strengths.pop(i)
            
        while len(rules) < num_rules and len(pair_rules) > 0:
            i = random.choices(range(len(pair_rules)), k=1, weights=pair_strengths)[0]
            if pair_rules[i].allowed_rule(board.num_objects(), constraints, rules):
                rules.append(pair_rules[i])
            pair_rules.pop(i)
            pair_strengths.pop(i)

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
                eliminates, rand_rule = rule_type.eliminate_sectors(board, constraints, elimination_data, \
                                                                    SpaceObject.PlanetX, obj)
                
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
                    rule = rule_type.generate_rule(board, constraints, rules, SpaceObject.PlanetX, obj)
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
        research = Research.generate_research(board, board_type.constraints, board_type.num_research)
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