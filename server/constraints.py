import itertools

from .board import *

class Constraint:
    """
    Represents a board constraint, i.e. ways that objects must be placed on a board
    """
    def __init__(self):
        pass
    
    def is_satisfied(self, board):
        """
        Checks whether a board meets this constraint. Returns true if constraint is met.
        """
        return True

    def is_immediately_limiting(self):
        """
        Returns true if this constraint limits the positions the space object can be in
        even when no objects are on the board.
        """
        return False

    def disallowed_sectors(self):
        """
        If the constraint is immediately limited, returns the list of sector that the 
        space object relevant to the constraint is not allowed to be in. Otherwise,
        returns [].
        """
        return []
    
    def num_object_types(self):
        """
        Returns the number of space object types affected by this constraint.
        """
        return 1
    
    def fill_board(self, board, num_objects):
        """
        Given a board and the number of each space object that must appear on it,
        fills the board in all ways possible given this constraint.
        
        board: A partially filled Board
        num_objects: A dictionary mapping space objects to the number of times they
            are supposed to appear in the board.
            
        Returns: a list of boards that contain the same objects as the original board,
            plus filling in objects to meet this constraint. Returns all possible
            such boards.
        """
        return []
    
    def affects(self):
        """
        Returns a list of space objects that are affected by this rule. Note that this is
        not the same as all of the space objects named in the constraint - e.g.
            "All gas clouds are next to an empty sector" does not affect empty sectors,
            since the other empty sectors may be wherever they like
        """
        return []
    
    def completes(self):
        """
        Returns a list of all space object that this constraint can "complete" - that is, 
        when generating all possible boards using fill_board, this constraint will add in 
        every object of that type.
        """
        return []
        
    def adds(self):
        """
        Returns a list of all space objects that can be added during fill_board
        """
        return []
    
    def __repr__(self):
        return "<Constraint>"
    
    def __str__(self):
        return "Constraint"

class CometConstraint(Constraint):
    """
    A constraint representing the places that comets are allowed to be on a board,
    i.e. only in prime sectors.
    """
    @staticmethod
    def _generate_primes(n):
        """
        Generates a list of primes from 1 to n
        
        n: maximum of range to generate primes in
        """
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
        """
        Creates a comet constraint for boards of length board_length.
        
        board_length: The length of the board for this constraint
        """
        self.board_length = board_length
        self.prime_positions = self._generate_primes(board_length)
    
    def is_satisfied(self, board):
        for i, obj in enumerate(board):
            if obj is SpaceObject.Comet:
                if (i+1) not in self.prime_positions:
                    return False
        return True
    
    def is_immediately_limiting(self):
        return True
    
    def disallowed_sectors(self):
        disallowed = [i for i in range(self.board_length) if (i+1) not in self.prime_positions]
        return [(SpaceObject.Comet, disallowed)]
    
    def num_object_types(self):
        return 1
    
    def fill_board(self, board, num_objects):
        num_comets = num_objects[SpaceObject.Comet]
        new_boards = []
        # Generate all permutations for comet positions
        for prime_sublist in itertools.combinations(self.prime_positions, num_comets):
            # Puts those comets on the board if there is nothing there already
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
    """
    A constraint representing where asteroids can be on the board - they
    must be next to each other 
    """
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
    
    def disallowed_sectors(self):
        return []
    
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
    """
    Empty constraint, does not constrain the board.
    """
    def __init__(self):
        pass
    
    def is_satisfied(self, board):
        return True
    
    def is_immediately_limiting(self):
        return False
    
    def disallowed_sectors(self):
        return []
    
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
    """
    Constraint representing where the gas clouds must be on the board - i.e.
    next to at least one empty sector
    """
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
    
    def disallowed_sectors(self):
        return []
    
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
            # Attempt to fill each position with a gas cloud if possible
            if obj is None:
                if board[i-1] is SpaceObject.Empty or board[i+1] is SpaceObject.Empty:
                    # If there is already an empty sector next to it, fill with gas
                    # cloud and proceed
                    board_copy = board.copy()
                    board_copy[i] = SpaceObject.GasCloud
                    new_num_objects[SpaceObject.GasCloud] = num_gas_clouds - 1
                    new_boards.extend(self.fill_board(board_copy, new_num_objects, i+1))
                elif num_empty > 0:
                    # Otherwise there must be empty sectors left to use
                    if board[i-1] is None and board[i-2] is not SpaceObject.GasCloud:
                        # Do not put an empty sector on the left if there is a gas cloud 
                        # already to the left of that, to avoid duplicate boards
                        board_copy = board.copy()
                        board_copy[i] = SpaceObject.GasCloud
                        board_copy[i-1] = SpaceObject.Empty
                        new_num_objects[SpaceObject.GasCloud] = num_gas_clouds - 1
                        new_num_objects[SpaceObject.Empty] = num_empty - 1
                        new_boards.extend(self.fill_board(board_copy, new_num_objects, i+1))

                    if board[i+1] is None and board[i+2] is not SpaceObject.GasCloud:
                        # Do not put an empty sector on the right if there is a gas cloud
                        # to the right of that, to avoid duplicate boards
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
    """
    A constraint representing where Planet X can be - i.e. not next to 
    a dwarf planet or a black hole
    """
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
    
    def disallowed_sectors(self):
        return []
    
    def num_object_types(self):
        return 3
    
    def fill_board(self, board, num_objects):
        new_boards = []
        for i, obj in enumerate(board):
            # Try every position not filled and not next to dwarf planets or black holes
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
    """
    Constraint representing where dwarf planets must be on the board - i.e. 
    in a band
    """
    def __init__(self, band_size):
        """
        Creates a dwarf planet constraint, constraining dwarf planets to be in a band
        of band_size
        """
        self.band_size = band_size
        
    def is_satisfied(self, board):
        longest_no_planet_run = 0
        current_run = 0
        # For dwarf planets to be in a band of six, there must be exactly board length - band size 
        # consecutive sectors with no dwarf planetss 
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
        
        # Continue wrapping around board until we encounter a dwarf planet
        # This handles if the longest gap between dwarf planets wraps around the end of the board
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
    
    def disallowed_sectors(self):
        return []
    
    def num_object_types(self):
        return 1
    
    def _fill_band(self, board, num_dwarf_planets, band_start, i_start=None):
        """
        Given the start location of the dwarf planet band, fill in the remaining dwarf planets
        in the center of the band
        
        board: The Board to fill, with the start and end dwarf planet in the band already filled
        num_dwarf_planets: The number of dwarf planets to fill in the band 
        band_start: The index of the first dwarf planet in the band
        i_start: Dwarf planets can be filled in starting at index i_start and not before
        """
        if i_start is None:
            i_start = band_start
            
        if num_dwarf_planets == 0:
            return [ board ]
        
        new_boards = []
        for i in range(i_start, band_start + self.band_size - num_dwarf_planets):
            # Try every position possible for the next dwarf planet
            if board[i] is None:
                board_copy = board.copy()
                board_copy[i] = SpaceObject.DwarfPlanet
                # Place dwarf planet here and then recurse to fill in remaining dwarf planets
                new_boards.extend(self._fill_band(board_copy, num_dwarf_planets - 1, band_start, i+1))
        return new_boards

    
    def fill_board(self, board, num_objects):
        # Must be at least two dwarf planets (start & end of the band)
        if num_objects[SpaceObject.DwarfPlanet] < 2:
            return []
        
        new_boards = []
        for i in range(len(board)):
            # Try every start/end pair of dwarf planets for the band
            if board[i] is None and board[i + self.band_size - 1] is None:
                board_copy = board.copy()
                board_copy[i] = SpaceObject.DwarfPlanet
                board_copy[i + self.band_size - 1] = SpaceObject.DwarfPlanet
                # Fill in the dwarf planets inside the band
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
    """
    Represents a constraint on the location of black holes - i.e. cannot be adjacent
    to empty sectors
    """
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
    
    def disallowed_sectors(self):
        return []
    
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