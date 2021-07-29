from enum import Enum, auto
from datetime import datetime

from .board import SpaceObject

class ActionType(Enum):
    START_GAME = auto()
    PLAYER_TURN = auto()
    CONFERENCE_PHASE = auto()
    THEORY_PHASE = auto()
    LAST_ACTION = auto()
    END_GAME = auto()
    
class Action:
    def __init__(self, action_type, player_id, action_id=None):
        self.action_id = action_id
        self.action_type = action_type
        self.player_id = player_id

    def to_json(self):
        return {
            "actionType": self.action_type.name,
            "playerID": self.player_id
        }
    
class TurnType(Enum):
    SURVEY = auto()
    TARGET = auto()
    RESEARCH = auto()
    LOCATE_PLANET_X = auto()
    
    def __str__(self):
        return self.name.lower().replace("_", " ").title()
    
    def code(self):
        if self == TurnType.SURVEY:
            return "S"
        elif self == TurnType.TARGET:
            return "T"
        elif self == TurnType.RESEARCH:
            return "R"
        elif self == TurnType.LOCATE_PLANET_X:
            return "L"
        
    @classmethod
    def parse(cls, s):
        if s == "S":
            return TurnType.SURVEY
        elif s == "T":
            return TurnType.TARGET
        elif s == "R":
            return TurnType.RESEARCH
        elif s == "L":
            return TurnType.LOCATE_PLANET_X
    
class Turn:
    def __init__(self, turn_type, selection, sectors, player_id=None, turn_time=None):
        self.turn_type = turn_type
        self.player_id = player_id
        self.selection = selection or ""
        self.sectors = sectors or tuple()
        if turn_time is None:
            turn_time = datetime.now()
        self.turn_time = turn_time
        
    def __str__(self):
        return str(self.turn_type) + " " + str(self.selection) + " " + "-".join(str(s) for s in self.sectors)
            
    def to_json(self):
        return {
            "playerID": self.player_id,
            "type": self.turn_type.name,
            "selection": self.selection,
            "sectors": list(self.sectors),
            "text": str(self),
            "time": self.turn_time
        }
    
    def code(self):
        return self.turn_type.code() + str(self.selection) + ",".join(str(s) for s in self.sectors)
    
    @classmethod
    def parse(cls, player_id, turn_time, s):
        turn_type = TurnType.parse(s[0])
        selection = s[1]
        if len(s[2:]):
            sectors = tuple(int(c) for c in s[2:].split(","))
        else:
            sectors = tuple()
        return Turn(turn_type, selection, sectors, player_id, turn_time)
        
        
class Player:
    def __init__(self, player_id, num, name, sector, arrival):
        self.player_id = player_id
        self.num = num
        self.name = name
        self.sector = sector
        self.arrival = arrival
        
    def __str__(self):
        return "Player " + str(self.num) + ": " + self.name + " - # " + str(self.arrival) + \
            " in sector " + str(self.sector + 1)
    
    def __repr__(self):
        return "<Player " + str(self.num) + ": " + self.name + " (# " + str(self.arrival) + \
                " in sector " + str(self.sector + 1) + ")>"
    
    def to_json(self):
        return {
            "num": self.num,
            "name": self.name,
            "sector": self.sector,
            "arrival": self.arrival,
            "id": self.player_id
        }
    
class Theory:
    def __init__(self, space_object, sector, player_id=None, progress=0):
        self.space_object = space_object
        self.sector = sector
        self.progress = progress
        self.player_id = player_id
        
    def __str__(self):
        return "Theory: Sector " + str(self.sector + 1) + " is " + self.space_object.one() + " " + \
                self.space_object.name()
    
    def __repr__(self):
        return "<Theory: " + repr(self.space_object) + " in sector " + str(self.sector + 1) + ">"
    
    def revealed(self):
        return self.progress == 3
    
    def to_json(self):
        return {
            "space_object": self.space_object.to_json(),
            "sector": self.sector,
            "progress": self.progress,
            "revealed": self.revealed(),
            "playerID": self.player_id
        }