import random
import itertools
import pickle
from copy import copy, deepcopy
import sys

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

class Constraint:
    def __init__(self):
        pass
    
    def is_satisfied(self, board):
        return True

    def is_immediatetly_limiting(self):
        return False
    
    def num_object_types(self):
        return 1
    
    def fill_board(self, board, num):
        return []
    
    def affects(self):
        return []

class CometConstraint(Constraint):
    @staticmethod
    def _generate_primes(n):
        primes = []
        for i in range(2, n+1):
            is_prime = True
            for prime in primes:
                if i % prime == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(i)
        return primes
                    
    def __init__(self, board_length):
        self.board_length = board_length
        self.prime_positions = self._generate_primes(board_length)
    
    def is_satisfied(self, board):
        for i, obj in enumerate(board):
            if type(obj) is Comet:
                if (i+1) not in self.prime_positions:
                    return False
        return True
    
    def is_immediately_limiting(self):
        return True
    
    def num_object_types(self):
        return 1
    
    def fill_board(self, board, num_objects):
        num_comets = num_objects[Comet]
        new_boards = []
        for prime_sublist in itertools.combinations(self.prime_positions, num_comets):
            if all(board[p-1] is None for p in prime_sublist):
                new_board = board.copy()
                for p in prime_sublist:
                    new_board[p-1] = Comet()
                new_boards.append(new_board)
        return new_boards
    
    def affects(self):
        return [ Comet ]
    
    def completes(self):
        return [ Comet ]
        
    def adds(self):
        return []

class AsteroidConstraint(Constraint):
    def __init__(self):
        pass
    
    def is_satisfied(self, board):
        for i, obj in enumerate(board):
            if type(obj) is Asteroid:
                if type(board[i-1]) is not Asteroid and type(board[i+1]) is not Asteroid:
                    return False
        return True

    def is_immediately_limiting(self):
        return False
    
    def num_object_types(self):
        return 1
    
    def fill_board(self, board, num_objects, start_i=0): 
        num_asteroids = num_objects[Asteroid]
        new_num_objects = deepcopy(num_objects)
        
        # Fill in board with runs of asteroids, starting new runs only at start_i and after
        
        # If there are no asteroids left, check if board is valid
        if num_asteroids == 0:
            if self.is_satisfied(board):
                return [board]
            else:
                return []
        
        # If there is a lone asteroid, find it and immediately add another asteroid clockwise
        for i in range(start_i - 1, len(board)):
            obj = board[i]
            if type(obj) is Asteroid and type(board[i-1]) is not Asteroid and type(board[i+1]) is not Asteroid:
                # Found a lone asteroid
                new_boards = []
                
                # Only fill asteroid runs to the right without combining runs
                if board[i+1] is None and type(board[i+2]) is not Asteroid:
                    board_copy = board.copy()
                    board_copy[i+1] = Asteroid()
                    new_num_objects[Asteroid] = num_asteroids - 1
                    new_boards.extend(self.fill_board(board_copy, new_num_objects, start_i))
                    
                return new_boards
            
        new_boards = []
        
        for i in range(len(board)):
            obj = board[i]
            if obj is None:
                # Continue an asteroid run without combining two runs
                if type(board[i-1]) is Asteroid and type(board[i+1]) is not Asteroid:
                    board_copy = board.copy()
                    board_copy[i] = Asteroid()
                    new_num_objects[Asteroid] = num_asteroids - 1
                    new_boards.extend(self.fill_board(board_copy, new_num_objects, start_i))
                # OR start a new asteroid run, if conditions allow
                elif i >= start_i and num_asteroids > 1 and type(board[i-1]) is not Asteroid and type(board[i+1]) is not Asteroid:
                    board_copy = board.copy()
                    board_copy[i] = Asteroid()
                    new_num_objects[Asteroid] = num_asteroids - 1
                    new_boards.extend(self.fill_board(board_copy, new_num_objects, i+1))
        
        return new_boards
        
    def affects(self):
        return [ Asteroid ]
    
    def completes(self):
        return [ Asteroid]
    
    def adds(self):
        return []

class NoConstraint(Constraint):
    def __init__(self):
        pass
    
    def is_satisfied(self, board):
        return True
    
    def is_immediately_limiting(self):
        return False
    
    def num_object_types(self):
        return 0
    
    def fill_board(self, board, num_objects):
        return [board]
    
    def affects(self):
        return []
    
    def completes(self):
        return []
    
    def adds(self):
        return []

class GasCloudConstraint(Constraint):
    def __init__(self):
        pass
    
    def is_satisfied(self, board):
        idxs = [i for i in range(len(board)) if type(board[i]) is GasCloud]
        for i in idxs:
            if type(board[i-1]) is not Empty and type(board[i+1]) is not Empty:
                return False
        return True
    
    def is_immediately_limiting(self):
        return False
    
    def num_object_types(self):
        return 2
    
    def fill_board(self, board, num_objects, start_i=0):
        num_gas_clouds = num_objects[GasCloud]
        num_empty = num_objects[Empty]
        new_num_objects = deepcopy(num_objects)
        
        if num_gas_clouds == 0:
            return [ board ]

        new_boards = []
        for i in range(start_i, len(board)):
            obj = board[i]
            if obj is None:
                if type(board[i-1]) is Empty or type(board[i+1]) is Empty:
                    board_copy = board.copy()
                    board_copy[i] = GasCloud()
                    new_num_objects[GasCloud] = num_gas_clouds - 1
                    new_boards.extend(self.fill_board(board_copy, new_num_objects, i+1))
                elif num_empty > 0:
                    if board[i-1] is None and type(board[i-2]) is not GasCloud:
                        board_copy = board.copy()
                        board_copy[i] = GasCloud()
                        board_copy[i-1] = Empty()
                        new_num_objects[GasCloud] = num_gas_clouds - 1
                        new_num_objects[Empty] = num_empty - 1
                        new_boards.extend(self.fill_board(board_copy, new_num_objects, i+1))

                    if board[i+1] is None and type(board[i+2]) is not GasCloud:
                        board_copy = board.copy()
                        board_copy[i] = GasCloud()
                        board_copy[i+1] = Empty()
                        new_num_objects[GasCloud] = num_gas_clouds - 1
                        new_num_objects[Empty] = num_empty - 1
                        new_boards.extend(self.fill_board(board_copy, new_num_objects, i+2))
                    
        return new_boards
    
    def affects(self):
        return [ GasCloud ]
    
    def completes(self):
        return [ GasCloud ]
    
    def adds(self):
        return [ Empty ]

class PlanetXConstraint(Constraint):
    def __init__(self):
        pass
    
    def is_satisfied(self, board):
        i = [type(obj) for obj in board].index(PlanetX)
        if type(board[i-1]) is DwarfPlanet or type(board[i+1]) is DwarfPlanet:
            return False
        elif type(board[i-1]) is BlackHole or type(board[i+1]) is BlackHole:
            return False
        else:
             return True
        
    def is_immediately_limiting(self):
        return False
    
    def num_object_types(self):
        return 3
    
    def fill_board(self, board, num_objects):
        new_boards = []
        for i, obj in enumerate(board):
            if type(board[i-1]) is not DwarfPlanet and type(board[i-1]) is not BlackHole \
                and type(board[i+1]) is not DwarfPlanet and type(board[i+1]) is not BlackHole \
                and board[i] is None:
                board_copy = board.copy()
                board_copy[i] = PlanetX()
                new_boards.append(board_copy)
        return new_boards
    
    def affects(self):
        return [ PlanetX, DwarfPlanet, BlackHole ]
    
    def completes(self):
        return [ PlanetX ]
    
    def adds(self):
        return []

class DwarfPlanetConstraint(Constraint):
    def __init__(self, band_size):
        self.band_size = band_size
        
    def is_satisfied(self, board):
        longest_no_planet_run = 0
        current_run = 0
        goal = len(board) - self.band_size
        for obj in board:
            if type(obj) is DwarfPlanet:
                if current_run > longest_no_planet_run:
                    longest_no_planet_run = current_run
                current_run = 0
            else:
                current_run += 1
                        
        if longest_no_planet_run == goal:
            return True
        
        if longest_no_planet_run > goal:
            return False
        
        for obj in board:
            if type(obj) is DwarfPlanet:
                if current_run == goal:
                    return True
                else:
                    return False
            else:
                current_run += 1
                
        
        return False
    
    def is_immediately_limiting(self):
        return False
    
    def num_object_types(self):
        return 1
    
    def _fill_band(self, board, num_dwarf_planets, band_start, i_start=None):
        if i_start is None:
            i_start = band_start
            
        if num_dwarf_planets == 0:
            return [ board ]
        
        new_boards = []
        for i in range(i_start, band_start + self.band_size - num_dwarf_planets):
            if board[i] is None:
                board_copy = board.copy()
                board_copy[i] = DwarfPlanet()
                new_boards.extend(self._fill_band(board_copy, num_dwarf_planets - 1, band_start, i+1))
        return new_boards

    
    def fill_board(self, board, num_objects):
        if num_objects[DwarfPlanet] < 2:
            return []
        
        new_boards = []
        for i in range(len(board)):
            if board[i] is None and board[i + self.band_size - 1] is None:
                board_copy = board.copy()
                board_copy[i] = DwarfPlanet()
                board_copy[i + self.band_size - 1] = DwarfPlanet()
                new_boards.extend(self._fill_band(board_copy, num_objects[DwarfPlanet] - 2, i))
        return new_boards
    
    def affects(self):
        return [ DwarfPlanet ]
    
    def completes(self):
        return [ DwarfPlanet ]
    
    def adds(self):
        return []

class BlackHoleConstraint(Constraint):
    def __init__(self):
        pass
    
    def is_satisfied(self, board):
        idxs = [i for i in range(len(board)) if type(board[i]) is BlackHole]
        for i in idxs:
            if type(board[i-1]) is Empty or type(board[i+1]) is Empty:
                return False
        return True
    
    def is_immediately_limiting(self):
        return False
    
    def num_object_types(self):
        return 2
    
    def fill_board(self, board, num_objects):
        new_boards = []
        for i, obj in enumerate(board):
            if obj is None and type(board[i-1]) is not Empty and type(board[i+1]) is not Empty:
                board_copy = board.copy()
                board_copy[i] = BlackHole()
                new_boards.append(board_copy)
        return new_boards
    
    def affects(self):
        return [ BlackHole, Empty ]
    
    def completes(self):
        return [ BlackHole ]
    
    def adds(self):
        return []

twelve_board_constraints = [CometConstraint(12), PlanetXConstraint(), GasCloudConstraint(), AsteroidConstraint()]
eighteen_board_constraints = [CometConstraint(18), PlanetXConstraint(), GasCloudConstraint(), \
                              DwarfPlanetConstraint(6), AsteroidConstraint() ]
twentyfour_board_constraints = [PlanetXConstraint(), GasCloudConstraint(), CometConstraint(24), \
                                DwarfPlanetConstraint(6), BlackHoleConstraint(), AsteroidConstraint() ]

twelve_board_numbers = {
    PlanetX: 1,
    Empty: 2,
    GasCloud: 2,
    DwarfPlanet: 1,
    Asteroid: 4,
    Comet: 2
}

eighteen_board_numbers = {
    PlanetX: 1,
    Empty: 5,
    GasCloud: 2,
    DwarfPlanet: 4,
    Asteroid: 4,
    Comet: 2
}

twentyfour_board_numbers = {
    PlanetX: 1,
    Empty: 6,
    GasCloud: 3,
    DwarfPlanet: 4,
    Asteroid: 6,
    Comet: 3,
    BlackHole: 1
}


class BoardType:
    def __init__(self, constraints, num_objects):
        self.constraints = constraints
        self.num_objects = num_objects
        self.board_length = sum(num_objects[t] for t in num_objects)
    
    def unconstrained_objects(self):
        obj_list = []
        for obj_type in self.num_objects:
            obj = obj_type()
            for i in range(self.num_objects[obj_type]):
                obj_list.append(obj)
        random.shuffle(obj_list)
        return obj_list
    
    def generate_random_board(self):
        objects = self.unconstrained_objects()
        board = Board(objects)
        while not board.check_constraints(self.constraints):
            random.shuffle(objects)
        return board
    
    def generate_all_boards_via_filtering(self):
        all_permutations = set(itertools.permutations(self.unconstrained_objects()))
        all_boards = [Board(permutation) for permutation in all_permutations]
        valid_boards = [board for board in all_perms if board.check_constraints(self.constraints)]
        return valid_boards

    def _subtract_num_objects(self, board):
        new_num_objects = copy(self.num_objects)
        for obj in board:
            if obj is not None:
                new_num_objects[type(obj)] -= 1
        return new_num_objects
    
    def _list_objects(self, num_objects):
        objs = []
        for object_type in num_objects:
            t = object_type()
            for i in range(num_objects[object_type]):
                objs.append(t)
        return objs
    
    def _relevant_constraints(self, objects):
        constraints = set()
        constraints_for_types = {}
        
        for obj_type in self.num_objects:
            constraints_for_types[obj_type] = []
        
        for constraint in self.constraints:
            for effected in constraint.affects():
                if effected in constraints_for_types:
                    constraints_for_types[effected].append(constraint)
   
        for obj in objects:
            constraints.update(constraints_for_types[type(obj)])
        
        return constraints

    def generate_all_boards(self, parallel=None):
        constraints = sorted(self.constraints, key=lambda c: (len(c.affects()), len(c.adds())))
        print(constraints)
        boards = [Board([None] * self.board_length)]
        next_boards = []
        
        for i, constraint in enumerate(constraints):
            print("Working on constraint " + str(i+1) + "/" + str(len(constraints)))
            for j, board in enumerate(boards):
                print("Processing board " + str(j+1) + "/" + str(len(boards)), end="\r")
                new_num_objects = self._subtract_num_objects(board)
                next_boards.extend(constraint.fill_board(board, new_num_objects))
            print()
            if i == 0 and parallel is not None:
                index, cores = parallel
                next_boards = [board for i, board in enumerate(next_boards) if i % cores == index]
            boards = next_boards
            next_boards = []
        
        print("Finishing boards with remaining objects")
        for i, board in enumerate(boards):
            print("Processing board " + str(i+1) + "/" + str(len(boards)), end="\r")
            new_num_objects = self._subtract_num_objects(board)
            remaining_objects = self._list_objects(new_num_objects)
            relevant_constraints = self._relevant_constraints(remaining_objects)
            perms = set(itertools.permutations(remaining_objects))
            
            for perm in perms:
                board_copy = board.copy()
                j = 0
                for i, obj in enumerate(board):
                    if board[i] is None:
                        board_copy[i] = perm[j]
                        j += 1
                if board_copy.check_constraints(relevant_constraints):
                    next_boards.append(board_copy)
        print()
        return next_boards

twelve_type = BoardType(twelve_board_constraints, twelve_board_numbers)
eighteen_type = BoardType(eighteen_board_constraints, eighteen_board_numbers)
twentyfour_type = BoardType(twentyfour_board_constraints, twentyfour_board_numbers)

sector_types = {
    12: twelve_type,
    18: eighteen_type,
    24: twentyfour_type
}

help_string = "Usage: python generate_boards.py [number of sectors] [core number 0...n-1] [number of cores n] [output file name (pickle)]"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(help_string)
    elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print(help_string)
    else:
        try:
            num_sectors = int(sys.argv[1])
            board_type = sector_types[num_sectors]
            core_num = int(sys.argv[2])
            num_cores = int(sys.argv[3])
            parallel = (core_num, num_cores)
            filename = sys.argv[4]
            
            valid_boards = board_type.generate_all_boards(parallel)
            
            with open(filename, "wb") as f:
                pickle.dump(valid_boards, f)
            
            print("Added " + str(len(valid_boards)) + " boards to " + filename)
        except:
            print(help_string)

