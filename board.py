from copy import copy, deepcopy
from enum import Enum

class SpaceObject(Enum):
    Empty = 0
    Comet = 1
    Asteroid = 2
    DwarfPlanet = 3
    PlanetX = 4
    GasCloud = 5
    BlackHole = 6
    
    def initial(self):
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
        
    def name(self):
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
        return self.name() + "s"
    
    def singular(self):
        if self is SpaceObject.PlanetX:
            return self.name()
        else:
            return "the " + self.name()
        
    def any_of(self, num_object):
        if num_object == 1:
            return self.singular()
        else:
            return self.one() + " " + self.name()
    
    def one(self):
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

class Board:
    def __init__(self, objects=[]):
        if objects is None:
            pass
        else:
            self.objects = objects
            
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
        x = i % len(self)
        return self.objects[x]
    
    def __setitem__(self, i, item):
        x = i % len(self)
        self.objects[x] = item
    
    def check_constraints(self, constraints):
        for constraint in constraints:
            if not constraint.is_satisfied(self):
                return False
        return True
    
    def copy(self):
        return Board(deepcopy(self.objects))
    
    def num_objects(self):
        objects = {}
        for obj in self.objects:
            if obj in objects:
                objects[obj] += 1
            else:
                objects[obj] = 1
        return objects
    
    @classmethod
    def parse(self, board_string):
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