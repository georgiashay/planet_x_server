class SpaceObject:
    def __init__(self):
        self.short_name = "~"
        self.long_name = "N/A"
    
    def __repr__(self):
        return "<" + self.long_name + ">"
        
    def __str__(self):
        return self.short_name

class Comet(SpaceObject):
    def __init__(self):
        self.short_name = "C"
        self.long_name = "Comet"
        
class Asteroid(SpaceObject):
    def __init__(self):
        self.short_name = "A"
        self.long_name = "Asteroid"

class Empty(SpaceObject):
    def __init__(self):
        self.short_name = "[]"
        self.long_name = "Empty Sector"

class DwarfPlanet(SpaceObject):
    def __init__(self):
        self.short_name = "D"
        self.long_name = "Dwarf Planet"

class PlanetX(SpaceObject):
    def __init__(self):
        self.short_name = "X"
        self.long_name = "Planet X"
        
class GasCloud(SpaceObject):
    def __init__(self):
        self.short_name = "G"
        self.long_name = "Gas Cloud"

class BlackHole(SpaceObject):
    def __init__(self):
        self.short_name = "B"
        self.long_name = "Black Hole"

class Board:
    def __init__(self, objects=[]):
        if objects is None:
            pass
        else:
            self.objects = objects
            
    def __str__(self):
        s = "["
        for obj in self.objects:
            s += str(obj)
            s += ", "
        s = s[:-2]
        s += "]"
        return s
    
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