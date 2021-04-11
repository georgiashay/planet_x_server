import random
import itertools
import pickle
from copy import copy, deepcopy
import sys
from enum import Enum
import os
import math

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
    
    def __repr__(self):
        return "<Constraint>"
    
    def __str__(self):
        return "Constraint"

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
            if type(obj) is SpaceObject.Comet:
                if (i+1) not in self.prime_positions:
                    return False
        return True
    
    def is_immediately_limiting(self):
        return True
    
    def num_object_types(self):
        return 1
    
    def fill_board(self, board, num_objects):
        num_comets = num_objects[SpaceObject.Comet]
        new_boards = []
        for prime_sublist in itertools.combinations(self.prime_positions, num_comets):
            if all(board[p-1] is None for p in prime_sublist):
                new_board = board.copy()
                for p in prime_sublist:
                    new_board[p-1] = SpaceObject.Comet
                new_boards.append(new_board)
        return new_boards
    
    def affects(self):
        return [ SpaceObject.Comet ]
    
    def completes(self):
        return [ SpaceObject.Comet ]
        
    def adds(self):
        return []
    
    def __repr__(self):
        return "<Comet Constraint: board size " + str(self.board_length) + ">"
    
    def __str__(self):
        return "Comet Constraint: board size " + str(self.board_length)

class AsteroidConstraint(Constraint):
    def __init__(self):
        pass
    
    def is_satisfied(self, board):
        for i, obj in enumerate(board):
            if obj is SpaceObject.Asteroid:
                if board[i-1] is not SpaceObject.Asteroid and board[i+1] is not SpaceObject.Asteroid:
                    return False
        return True

    def is_immediately_limiting(self):
        return False
    
    def num_object_types(self):
        return 1
    
    def fill_board(self, board, num_objects, start_i=0): 
        num_asteroids = num_objects[SpaceObject.Asteroid]
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
            if obj is SpaceObject.Asteroid and board[i-1] is not SpaceObject.Asteroid \
            and board[i+1] is not SpaceObject.Asteroid:
                # Found a lone asteroid
                new_boards = []
                
                # Only fill asteroid runs to the right without combining runs
                if board[i+1] is None and board[i+2] is not SpaceObject.Asteroid:
                    board_copy = board.copy()
                    board_copy[i+1] = SpaceObject.Asteroid
                    new_num_objects[SpaceObject.Asteroid] = num_asteroids - 1
                    new_boards.extend(self.fill_board(board_copy, new_num_objects, start_i))
                    
                return new_boards
            
        new_boards = []
        
        for i in range(len(board)):
            obj = board[i]
            if obj is None:
                # Continue an asteroid run without combining two runs
                if board[i-1] is SpaceObject.Asteroid and board[i+1] is not SpaceObject.Asteroid:
                    board_copy = board.copy()
                    board_copy[i] = SpaceObject.Asteroid
                    new_num_objects[SpaceObject.Asteroid] = num_asteroids - 1
                    new_boards.extend(self.fill_board(board_copy, new_num_objects, start_i))
                # OR start a new asteroid run, if conditions allow
                elif i >= start_i and num_asteroids > 1 and board[i-1] is not SpaceObject.Asteroid \
                and board[i+1] is not SpaceObject.Asteroid:
                    board_copy = board.copy()
                    board_copy[i] = SpaceObject.Asteroid
                    new_num_objects[SpaceObject.Asteroid] = num_asteroids - 1
                    new_boards.extend(self.fill_board(board_copy, new_num_objects, i+1))
        
        return new_boards
        
    def affects(self):
        return [ SpaceObject.Asteroid ]
    
    def completes(self):
        return [ SpaceObject.Asteroid ]
    
    def adds(self):
        return []
    
    def __repr__(self):
        return "<Asteroid Constraint>"
    
    def __str__(self):
        return "Asteroid Constraint"

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
    
    def __repr__(self):
        return "<Empty Constraint>"
    
    def __str__(self):
        return "Empty Constraint"

class GasCloudConstraint(Constraint):
    def __init__(self):
        pass
    
    def is_satisfied(self, board):
        idxs = [i for i in range(len(board)) if board[i] is SpaceObject.GasCloud]
        for i in idxs:
            if board[i-1] is not SpaceObject.Empty and board[i+1] is not SpaceObject.Empty:
                return False
        return True
    
    def is_immediately_limiting(self):
        return False
    
    def num_object_types(self):
        return 2
    
    def fill_board(self, board, num_objects, start_i=0):
        num_gas_clouds = num_objects[SpaceObject.GasCloud]
        num_empty = num_objects[SpaceObject.Empty]
        new_num_objects = deepcopy(num_objects)
        
        if num_gas_clouds == 0:
            return [ board ]

        new_boards = []
        for i in range(start_i, len(board)):
            obj = board[i]
            if obj is None:
                if board[i-1] is SpaceObject.Empty or board[i+1] is SpaceObject.Empty:
                    board_copy = board.copy()
                    board_copy[i] = SpaceObject.GasCloud
                    new_num_objects[SpaceObject.GasCloud] = num_gas_clouds - 1
                    new_boards.extend(self.fill_board(board_copy, new_num_objects, i+1))
                elif num_empty > 0:
                    if board[i-1] is None and board[i-2] is not SpaceObject.GasCloud:
                        board_copy = board.copy()
                        board_copy[i] = SpaceObject.GasCloud
                        board_copy[i-1] = SpaceObject.Empty
                        new_num_objects[SpaceObject.GasCloud] = num_gas_clouds - 1
                        new_num_objects[SpaceObject.Empty] = num_empty - 1
                        new_boards.extend(self.fill_board(board_copy, new_num_objects, i+1))

                    if board[i+1] is None and board[i+2] is not SpaceObject.GasCloud:
                        board_copy = board.copy()
                        board_copy[i] = SpaceObject.GasCloud
                        board_copy[i+1] = SpaceObject.Empty
                        new_num_objects[SpaceObject.GasCloud] = num_gas_clouds - 1
                        new_num_objects[SpaceObject.Empty] = num_empty - 1
                        new_boards.extend(self.fill_board(board_copy, new_num_objects, i+2))
                    
        return new_boards
    
    def affects(self):
        return [ SpaceObject.GasCloud ]
    
    def completes(self):
        return [ SpaceObject.GasCloud ]
    
    def adds(self):
        return [ SpaceObject.Empty ]
    
    def __repr__(self):
        return "<Gas Cloud Constraint>"
    
    def __str__(self):
        return "Gas Cloud Constraint"

class PlanetXConstraint(Constraint):
    def __init__(self):
        pass
    
    def is_satisfied(self, board):
        i = board.objects.index(SpaceObject.PlanetX)
        if board[i-1] is SpaceObject.DwarfPlanet or board[i+1] is SpaceObject.DwarfPlanet:
            return False
        elif board[i-1] is SpaceObject.BlackHole or board[i+1] is SpaceObject.BlackHole:
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
            if board[i-1] is not SpaceObject.DwarfPlanet and board[i-1] is not SpaceObject.BlackHole \
            and board[i+1] is not SpaceObject.DwarfPlanet and board[i+1] is not SpaceObject.BlackHole \
            and board[i] is None:
                board_copy = board.copy()
                board_copy[i] = SpaceObject.PlanetX
                new_boards.append(board_copy)
        return new_boards
    
    def affects(self):
        return [ SpaceObject.PlanetX, SpaceObject.DwarfPlanet, SpaceObject.BlackHole ]
    
    def completes(self):
        return [ SpaceObject.PlanetX ]
    
    def adds(self):
        return []
    
    def __repr__(self):
        return "<Planet X Constraint>"
    
    def __str__(self):
        return "Planet X Constraint"

class DwarfPlanetConstraint(Constraint):
    def __init__(self, band_size):
        self.band_size = band_size
        
    def is_satisfied(self, board):
        longest_no_planet_run = 0
        current_run = 0
        goal = len(board) - self.band_size
        for obj in board:
            if obj is SpaceObject.DwarfPlanet:
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
            if obj is SpaceObject.DwarfPlanet:
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
                board_copy[i] = SpaceObject.DwarfPlanet
                new_boards.extend(self._fill_band(board_copy, num_dwarf_planets - 1, band_start, i+1))
        return new_boards

    
    def fill_board(self, board, num_objects):
        if num_objects[SpaceObject.DwarfPlanet] < 2:
            return []
        
        new_boards = []
        for i in range(len(board)):
            if board[i] is None and board[i + self.band_size - 1] is None:
                board_copy = board.copy()
                board_copy[i] = SpaceObject.DwarfPlanet
                board_copy[i + self.band_size - 1] = SpaceObject.DwarfPlanet
                new_boards.extend(self._fill_band(board_copy, num_objects[SpaceObject.DwarfPlanet] - 2, i))
        return new_boards
    
    def affects(self):
        return [ SpaceObject.DwarfPlanet ]
    
    def completes(self):
        return [ SpaceObject.DwarfPlanet ]
    
    def adds(self):
        return []
    
    def __repr__(self):
        return "<Dwarf Planet Constraint: band size " + str(self.band_size) + ">"
    
    def __str__(self):
        return "Dwarf Planet Constraint: band size " + str(self.band_size)

class BlackHoleConstraint(Constraint):
    def __init__(self):
        pass
    
    def is_satisfied(self, board):
        idxs = [i for i in range(len(board)) if board[i] is SpaceObject.BlackHole]
        for i in idxs:
            if board[i-1] is SpaceObject.Empty or board[i+1] is SpaceObject.Empty:
                return False
        return True
    
    def is_immediately_limiting(self):
        return False
    
    def num_object_types(self):
        return 2
    
    def fill_board(self, board, num_objects):
        new_boards = []
        for i, obj in enumerate(board):
            if obj is None and board[i-1] is not SpaceObject.Empty and board[i+1] is not SpaceObject.Empty:
                board_copy = board.copy()
                board_copy[i] = SpaceObject.BlackHole
                new_boards.append(board_copy)
        return new_boards
    
    def affects(self):
        return [ SpaceObject.BlackHole, SpaceObject.Empty ]
    
    def completes(self):
        return [ SpaceObject.BlackHole ]
    
    def adds(self):
        return []
    
    def __repr__(self):
        return "<Black Hole Constraint>"
    
    def __str__(self):
        return "Black Hole Constraint"

twelve_board_constraints = [CometConstraint(12), AsteroidConstraint(), PlanetXConstraint(), GasCloudConstraint() ]
eighteen_board_constraints = [CometConstraint(18), AsteroidConstraint(), DwarfPlanetConstraint(6), \
                              PlanetXConstraint(), GasCloudConstraint() ]
twentyfour_board_constraints = [ CometConstraint(24), AsteroidConstraint(), DwarfPlanetConstraint(6), \
                                BlackHoleConstraint(), PlanetXConstraint(), GasCloudConstraint() ]

twelve_board_numbers = {
    SpaceObject.PlanetX: 1,
    SpaceObject.Empty: 2,
    SpaceObject.GasCloud: 2,
    SpaceObject.DwarfPlanet: 1,
    SpaceObject.Asteroid: 4,
    SpaceObject.Comet: 2
}

eighteen_board_numbers = {
    SpaceObject.PlanetX: 1,
    SpaceObject.Empty: 5,
    SpaceObject.GasCloud: 2,
    SpaceObject.DwarfPlanet: 4,
    SpaceObject.Asteroid: 4,
    SpaceObject.Comet: 2
}

twentyfour_board_numbers = {
    SpaceObject.PlanetX: 1,
    SpaceObject.Empty: 6,
    SpaceObject.GasCloud: 3,
    SpaceObject.DwarfPlanet: 4,
    SpaceObject.Asteroid: 6,
    SpaceObject.Comet: 3,
    SpaceObject.BlackHole: 1
}
    
class BoardType:
    def __init__(self, constraints, num_objects):
        self.constraints = constraints
        self.num_objects = num_objects
        self.board_length = sum(num_objects[t] for t in num_objects)
    
    def unconstrained_objects(self):
        obj_list = []
        for obj in self.num_objects:
            for i in range(self.num_objects[obj]):
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
                new_num_objects[obj] -= 1
        return new_num_objects
    
    def _list_objects(self, num_objects):
        objs = []
        for obj in num_objects:
            for i in range(num_objects[obj]):
                objs.append(obj)
        return objs
    
    def _relevant_constraints(self, objects):
        constraints = set()
        constraints_for_types = {}
        
        for obj in self.num_objects:
            constraints_for_types[obj] = []
        
        for constraint in self.constraints:
            for effected in constraint.affects():
                if effected in constraints_for_types:
                    constraints_for_types[effected].append(constraint)
   
        for obj in objects:
            constraints.update(constraints_for_types[obj])
        
        return constraints

    def generate_all_boards(self, parallel=None):
        constraints = sorted(self.constraints, key=lambda c: (len(c.affects()), len(c.adds())))
        print("Constraints:")
        print("\n".join(str(c) for c in constraints))
        boards = [Board([None] * self.board_length)]
        next_boards = []
        
        for i, constraint in enumerate(constraints):
            print("Working on constraint " + str(i+1) + "/" + str(len(constraints)) + ": " + str(constraint))
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
    
    def generate_boards_to_file(self, filename, chunk_size=float('inf'), parallel=None):
        constraints = sorted(self.constraints, key=lambda c: (len(c.affects()), len(c.adds())))
        print("Constraints:", flush=True)
        print("\n".join(str(c) for c in constraints), flush=True)
        print(flush=True)
        
        boards_file = None
        total_chunks = 1
        next_boards_file = open("tmp_boards_0.b", "w")
        boards = [Board([None] * self.board_length)]
        last_boards = 1
        
        for i, constraint in enumerate(constraints):
            print("Working on constraint " + str(i+1) + "/" + str(len(constraints)) + ": " + str(constraint), flush=True)
            more_boards = True
            chunk = 0
            num_boards = 0
            last_update = 0
            
            while more_boards:
                if len(boards) == 0:
                    if i == 0:
                        more_boards = False
                        break
                
                    while len(boards) < chunk_size:
                        board_str = boards_file.readline().rstrip("\r\n")
                        if len(board_str) == 0:
                            more_boards = False
                            break
                        else:
                            boards.append(Board.parse(board_str))

                #print("Processing chunk " + str(chunk+1) + "/" + str(total_chunks))
                for j, board in enumerate(boards):
                    #print("Processing chunk " + str(chunk + 1) + "/" + str(total_chunks) + 
                    #      ", board " + str(j+1) + "/" + str(len(boards)), end="         \r")
                    new_num_objects = self._subtract_num_objects(board)
                    new_boards = constraint.fill_board(board, new_num_objects)
                    for new_board in new_boards:
                        num_boards += 1
                        next_boards_file.write(str(new_board) + "\n")
                        
                    current_board = j + chunk_size * chunk + 1
                    current_percentage = int(current_board * 100/last_boards)
                    if current_percentage > last_update:
                        print(str(current_percentage) + "% complete: " + str(current_board) + "/" + str(last_boards), flush=True)
                        last_update = current_percentage
                
                boards = []
                chunk += 1
            print(flush=True)
            
            next_boards_file.close()

            if i == 0 and parallel is not None:
                index, cores = parallel
                with open("tmp_boards_0.b", "r") as f:
                    next_boards = f.readlines()
                next_boards = [board.rstrip("\r\n") for i, board in enumerate(next_boards) if i % cores == index]
                num_boards = len(next_boards)
                with open("tmp_boards_0.b", "w") as f:
                    f.write("\n".join(next_boards) + "\n")
                
            if boards_file:
                boards_file.close()
                os.remove("tmp_boards_" + str(i-1) + ".b")            
            
            boards_file = open("tmp_boards_" + str(i) + ".b", "r")
            if i + 1 < len(constraints):
                next_boards_file = open("tmp_boards_" + str(i+1) + ".b", "w")
            boards = []

            total_chunks = max(math.ceil(num_boards/chunk_size), 1)
            last_boards = num_boards
        
        if boards_file:
            boards_file.close()
            
        next_boards_file.close()
        
        boards_file = open("tmp_boards_" + str(len(constraints)-1) + ".b", "r")
        boards = []
        final_boards_file = open(filename, "w")
        
        more_boards = True
        
        print("Finishing boards with remaining objects", flush=True)
        chunk = 0
        last_update = 0
        while more_boards:
            if len(boards) == 0:
                while len(boards) < chunk_size:
                    board_str = boards_file.readline().rstrip("\r\n")
                    if len(board_str) == 0:
                        more_boards = False
                        break
                    else:
                        boards.append(Board.parse(board_str))
            
            #print("Processing chunk " + str(chunk+1) + "/" + str(total_chunks))
            for i, board in enumerate(boards):
                #print("Processing chunk " + str(chunk + 1) + "/" + str(total_chunks) + 
                #      ", board " + str(i+1) + "/" + str(len(boards)), end="        \r")
                new_num_objects = self._subtract_num_objects(board)
                remaining_objects = self._list_objects(new_num_objects)
                relevant_constraints = self._relevant_constraints(remaining_objects)
                perms = set(itertools.permutations(remaining_objects))

                for perm in perms:
                    board_copy = board.copy()
                    j = 0
                    for k, obj in enumerate(board):
                        if board[k] is None:
                            board_copy[k] = perm[j]
                            j += 1
                    if board_copy.check_constraints(relevant_constraints):
                        final_boards_file.write(str(board_copy) + "\n")
                                        
                current_board = i + chunk_size * chunk + 1
                current_percentage = int(current_board * 100/last_boards)
                if current_percentage > last_update:
                    print(str(current_percentage) + "% complete: " + str(current_board) + "/" + str(last_boards), flush=True)
                    last_update = current_percentage
                    
            boards = []
            chunk += 1
        print(flush=True)
        boards_file.close()
        os.remove("tmp_boards_" + str(len(constraints)-1) + ".b")
        final_boards_file.close()

twelve_type = BoardType(twelve_board_constraints, twelve_board_numbers)
eighteen_type = BoardType(eighteen_board_constraints, eighteen_board_numbers)
twentyfour_type = BoardType(twentyfour_board_constraints, twentyfour_board_numbers)

sector_types = {
    12: twelve_type,
    18: eighteen_type,
    24: twentyfour_type
}

help_string = "Usage: python generate_boards.py [number of sectors] [core number 0...n-1] [number of cores n] [# boards per chunk] [output file name]"

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
            chunk_size = int(sys.argv[4])
            filename = sys.argv[5]
            
            board_type.generate_boards_to_file(filename, parallel=parallel, chunk_size=chunk_size)
        except Exception as e:
            print(e)
            print(help_string)

