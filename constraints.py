from board import *

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