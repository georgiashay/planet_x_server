from copy import copy, deepcopy
from enum import Enum

class SpaceObject(Enum):
    """
    Represents a space object that could appear in a sector of the board
    """
    Empty = 0
    Comet = 1
    Asteroid = 2
    DwarfPlanet = 3
    PlanetX = 4
    GasCloud = 5
    BlackHole = 6
    
    def initial(self):
        """
        Returns the one-character initial of the space object
        """
        if self is SpaceObject.Empty:
            return "E"
        elif self is SpaceObject.Comet:
            return "C"
        elif self is SpaceObject.Asteroid:
            return "A"
        elif self is SpaceObject.DwarfPlanet:
            return "D"
        elif self is SpaceObject.PlanetX:
            return "X"
        elif self is SpaceObject.GasCloud:
            return "G"
        elif self is SpaceObject.BlackHole:
            return "B"
        
    @classmethod
    def parse(cls, s):
        """
        Parses a one-character initial into a SpaceObject
        
        s: one-character initial 
        """
        if s == "E":
            return SpaceObject.Empty
        elif s == "C":
            return SpaceObject.Comet
        elif s == "A":
            return SpaceObject.Asteroid
        elif s == "D":
            return SpaceObject.DwarfPlanet
        elif s == "X":
            return SpaceObject.PlanetX
        elif s == "G":
            return SpaceObject.GasCloud
        elif s == "B":
            return SpaceObject.BlackHole
        
    def name(self):
        """
        Returns the name of the space object
        """
        if self is SpaceObject.Empty:
            return "empty sector"
        elif self is SpaceObject.Comet:
            return "comet"
        elif self is SpaceObject.Asteroid:
            return "asteroid"
        elif self is SpaceObject.DwarfPlanet:
            return "dwarf planet"
        elif self is SpaceObject.PlanetX:
            return "Planet X"
        elif self is SpaceObject.GasCloud:
            return "gas cloud"
        elif self is SpaceObject.BlackHole:
            return "black hole"
    
    def plural(self):
        """
        Returns the plural version of the name of the space object
        """
        return self.name() + "s"
    
    def singular(self):
        """
        Returns the name of the space object, given that only one of it exists. 
        i.e. if the space object is already proper noun, it will be its name; 
        otherwise it will prepend 'the' to the name of the space object.
        """
        if self is SpaceObject.PlanetX:
            return self.name()
        else:
            return "the " + self.name()
        
    def proper(self):
        """
        Returns the capitalized version of the space object.
        """
        words = self.name().split()
        proper_words = [word[:1].upper() + word[1:] for word in words]
        return " ".join(proper_words)
        
    def proper_plural(self):
        """
        Returns the capitalized version of the plural name of the space object.
        """
        return self.proper() + "s"
    
    def category(self):
        """
        Returns the name of the space object as it would appear in a rule category.
        e.g. "Asteroids & Comets" or "Planet X & Gas Clouds".
        """
        if self is SpaceObject.PlanetX:
            return self.name()
        else:
            return self.proper_plural()
        
    def any_of(self, num_object):
        """
        Returns the way to refer to one of this space object, given that there are 
        num_object of them on the board.
        
        num_object: The number of this type of space object that exist on the board
        """
        if num_object == 1:
            return self.singular()
        else:
            return self.one() + " " + self.name()
    
    def one(self):
        """
        Returns the article used to refer to one of this space object - i.e. "a" or "an"
        """
        if self is SpaceObject.Empty:
            return "an"
        elif self is SpaceObject.Comet:
            return "a"
        elif self is SpaceObject.Asteroid:
            return "an"
        elif self is SpaceObject.DwarfPlanet:
            return "a"
        elif self is SpaceObject.PlanetX:
            return "a"
        elif self is SpaceObject.GasCloud:
            return "a"
        elif self is SpaceObject.BlackHole:
            return "a"
    
    def __repr__(self):
        return "<" + self.name() + ">"
        
    def __str__(self):
        return self.initial()
    
    def to_json(self):
        """
        Returns a json representation of the object including its initial and name
        """
        return {
            "initial": self.initial(),
            "name": self.name()
        }

class Board:
    """
    Represents a game board with specific objects in its sectors
    """
    def __init__(self, objects=[]):
        """
        Create a Board with the space objects in objects, starting from sector 1.
        
        objects: A list of SpaceObject that are on the board, in order
        """
        if objects is None:
            self.objects = []
        else:
            self.objects = objects
           
        self.num_objs_valid = False
            
    def __str__(self):
        return "".join("-" if obj is None else str(obj) for obj in self.objects)
    
    def __repr__(self):
        return "<Board " + str(self) + ">"
    
    def __len__(self):
        return len(self.objects)
    
    def __iter__(self):
        for obj in self.objects:
            yield obj
            
    def __getitem__(self, i):
        if isinstance(i, slice) :
            return [self.objects[ii % len(self)] for ii in range(i.start or 0, i.stop or len(self), i.step or 1)]
        else:
            x = i % len(self)
            return self.objects[x]
    
    def __setitem__(self, i, item):
        x = i % len(self)
        self.objects[x] = item
        self.num_objs_valid = False
    
    def check_constraints(self, constraints):
        """
        Checks if the board meets a set of constraints. Returns true if 
        all constraints are met.
        
        constraints: A list of Constraint to check against.
        """
        for constraint in constraints:
            if not constraint.is_satisfied(self):
                return False
        return True
    
    def copy(self):
        """
        Create a new Board with this same objects as this Board.
        """
        return Board(copy(self.objects))
    
    def _calc_num_objects(self):
        objects = {}
        for obj in self.objects:
            if obj in objects:
                objects[obj] += 1
            else:
                objects[obj] = 1
        return objects
    
    def num_objects(self):
        """
        Returns a dictionary mapping SpaceObjects to the number of times that 
        that SpaceObject appears in this board.
        """
        if not self.num_objs_valid:
            self.num_objs = self._calc_num_objects()
        return self.num_objs
        
    @classmethod
    def parse(self, board_string):
        """
        Creates a Board by parsing a board string.
        
        board_string: A string which contains initials for each space object in
        the board, or - if that sector has not been assigned a space object yet.
        """
        objects = []
        for char in board_string:
            if char == "E":
                objects.append(SpaceObject.Empty)
            elif char == "C":
                objects.append(SpaceObject.Comet)
            elif char == "A":
                objects.append(SpaceObject.Asteroid)
            elif char == "D":
                objects.append(SpaceObject.DwarfPlanet)
            elif char == "X":
                objects.append(SpaceObject.PlanetX)
            elif char == "G":
                objects.append(SpaceObject.GasCloud)
            elif char == "B":
                objects.append(SpaceObject.BlackHole)
            elif char == "-":
                objects.append(None)
            else:
                return None
        return Board(objects)  
        
    def to_json(self):
        """
        Returns a json representation of this board, containing the following keys:
            - objects: a list of the json representation of each object on the board
            - size: the number of sectors of the board
            - numObjects: a dictionary mapping space object initials to the number of
                times that space object appears on the board.
        """
        return {
            "objects": [obj.to_json() for obj in self.objects],
            "size": len(self),
            "numObjects": {
                space_object.initial(): self.num_objects()[space_object]
                for space_object in self.num_objects()
            }
        }