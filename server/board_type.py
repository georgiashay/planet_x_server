import random
import itertools
import sys
import os
import math

from .constraints import *
from .board import SpaceObject
    
class BoardType:
    """
    Represents a type of game board, defining the number of sectors, number of
        each space object which are supposed to appear on the board, the 
        constraints for placing space objects on the board, and the number
        of research and conference rules for the game.
    """
    def __init__(self, constraints, num_objects, num_research, num_conference):
        """
        Creates a BoardType.
        
        constraints: A list of constraints this type of board must follow
        num_objects: A dictionary mapping space objects to the number of that 
            space object that must appear in a board of this type
        num_research: The number of research rules for this type of board
        num_conference: The number of conference rules for this type of board
        """
        self.constraints = constraints
        self.num_objects = num_objects
        self.board_length = sum(num_objects[t] for t in num_objects)
        self.num_research = num_research
        self.num_conference = num_conference
    
    def unconstrained_objects(self):
        """
        Creates a list of space objects, conforming to the number of space objects
        present in this type of board but not necessarily adhering to the constraints
        for this type of board.
        """
        obj_list = []
        for obj in self.num_objects:
            for i in range(self.num_objects[obj]):
                obj_list.append(obj)
        random.shuffle(obj_list)
        return obj_list
    
    def generate_random_board(self):
        """
        Generates a random board of this type which meets constraints and the number of
        each space object that should be present.
        """
        objects = self.unconstrained_objects()
        board = Board(objects)
        while not board.check_constraints(self.constraints):
            random.shuffle(objects)
        return board
    
    def generate_all_boards_via_filtering(self):
        """
        Generates all possible Boards of this type. First, every permutation of the 
        space objects is generated, and then they are filtered by checking to see if 
        the resulting board meets the constraints for this type.
        """
        all_permutations = set(itertools.permutations(self.unconstrained_objects()))
        all_boards = [Board(permutation) for permutation in all_permutations]
        valid_boards = [board for board in all_perms if board.check_constraints(self.constraints)]
        return valid_boards

    def _subtract_num_objects(self, board):
        """
        Gets the number of each space object remaining to be placed on the board. Returns
        a dictionary mapping space objects to the number of that space object that has
        not yet been placed on the board.
        
        board: A board that has been partially filled with space objects
        """
        new_num_objects = copy(self.num_objects)
        for obj in board:
            if obj is not None:
                new_num_objects[obj] -= 1
        return new_num_objects
    
    def _list_objects(self, num_objects):
        """
        List all of the space objects for a board, repeating each space object
        the number of times that it appears on the board.
        
        num_objects: A dictionary mapping space objects to the number of times
            they should appear.
        """
        objs = []
        for obj in num_objects:
            for i in range(num_objects[obj]):
                objs.append(obj)
        return objs
    
    def _relevant_constraints(self, objects):
        """
        Returns a list of all constraints for this type of board that affect 
        placement of any object in the list objects.
        
        objects: A list of space objects.
        """
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
        """
        Generate all boards of this type by working up, i.e. adding in space objects that 
        follow each constraint until the board is full.
        
        parallel: If provided, will only generate some of the boards. It should be a tuple
            where the first number is the core number, and the second number is the total
            number of cores this process is run on. Boards passing the first constraint are
            eliminated if their indices are not the first number, modulo the second number.
        """
        # Sort constraints to attempt to create the best "bottom-up" approach.
        # They are sorted first by the number of space objects they affect - i.e. constraints
        # affecting only one space object go first
        # They are then sorted by the number of space objects they add - i.e. constraints which
        # add more types of space objects go first
        constraints = sorted(self.constraints, key=lambda c: (len(c.affects()), len(c.adds())))
        print("Constraints:")
        print("\n".join(str(c) for c in constraints))
        boards = [Board([None] * self.board_length)]
        next_boards = []
        
        # For each constraint, generate all boards (leaving some sectors undefined) which
        # meet that constraint. Build on top of boards passing previous constraints.
        for i, constraint in enumerate(constraints):
            print("Working on constraint " + str(i+1) + "/" + str(len(constraints)) + ": " + str(constraint))
            # For every board built from previous constraints, find all boards that can
            # satisfy this next constraint by adding to it.
            for j, board in enumerate(boards):
#                 print("Processing board " + str(j+1) + "/" + str(len(boards)), end="\r")
                new_num_objects = self._subtract_num_objects(board)
                next_boards.extend(constraint.fill_board(board, new_num_objects))
            print()
            # For the first constraint, filter out boards to parallelize the process.
            if i == 0 and parallel is not None:
                index, cores = parallel
                next_boards = [board for i, board in enumerate(next_boards) if i % cores == index]
            boards = next_boards
            next_boards = []
        
        # Fill in the remaining undefined sectors 
        print("Finishing boards with remaining objects")
        for i, board in enumerate(boards):
#             print("Processing board " + str(i+1) + "/" + str(len(boards)), end="\r")
            # Find what objects need added to this board, and what constraints affect that object
            new_num_objects = self._subtract_num_objects(board)
            remaining_objects = self._list_objects(new_num_objects)
            relevant_constraints = self._relevant_constraints(remaining_objects)
            # Create every permutation of the remaining objects to attempt to fit into the board 
            perms = set(itertools.permutations(remaining_objects))
            
            for perm in perms:
                board_copy = board.copy()
                j = 0
                # Fill in undefined sectors with this permutation of the remaining objects
                for i, obj in enumerate(board):
                    if board[i] is None:
                        board_copy[i] = perm[j]
                        j += 1
                # Ensure that the board follows the constraints
                if board_copy.check_constraints(relevant_constraints):
                    next_boards.append(board_copy)
        print()
        return next_boards
    
    def generate_boards_to_file(self, filename, chunk_size=float('inf'), parallel=None):
        """
        Generate all boards of this type by working up, i.e. adding in space objects that 
        follow each constraint until the board is full.
        
        filename: File to put the generated boards in, one per line
        chunk_size: Maximum number of boards to hold in memory at once
        parallel: If provided, will only generate some of the boards. It should be a tuple
            where the first number is the core number, and the second number is the total
            number of cores this process is run on. Boards passing the first constraint are
            eliminated if their indices are not the first number, modulo the second number.
        """
        # Sort constraints to attempt to create the best "bottom-up" approach.
        # They are sorted first by the number of space objects they affect - i.e. constraints
        # affecting only one space object go first
        # They are then sorted by the number of space objects they add - i.e. constraints which
        # add more types of space objects go first
        constraints = sorted(self.constraints, key=lambda c: (len(c.affects()), len(c.adds())))
        print("Constraints:", flush=True)
        print("\n".join(str(c) for c in constraints), flush=True)
        print(flush=True)
        
        # Keep two files at all times: boards_file and next_boards_file
        # boards_file is a temporary file holding boards that met all the previous constraints
        # next_boards_file will be continually appended to with new boards, built from the previous
        # ones, that meet the next constraint as well
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
            
            # Get more boards from the last boards file (up to chunk_size)
            while more_boards:
                if len(boards) == 0:
                    if i == 0:
                        # For the first constraint, the boards [Just one blank one] are already provided and not in a file
                        more_boards = False
                        break
                
                    # Read the boards file line by line and extract boards
                    while len(boards) < chunk_size:
                        board_str = boards_file.readline().rstrip("\r\n")
                        if len(board_str) == 0:
                            more_boards = False
                            break
                        else:
                            boards.append(Board.parse(board_str))

                # Create new boards from each previous board
                #print("Processing chunk " + str(chunk+1) + "/" + str(total_chunks))
                for j, board in enumerate(boards):
                    #print("Processing chunk " + str(chunk + 1) + "/" + str(total_chunks) + 
                    #      ", board " + str(j+1) + "/" + str(len(boards)), end="         \r")
                    # Create all possible boards from this previous board that meet 
                    # the current constraint
                    new_num_objects = self._subtract_num_objects(board)
                    new_boards = constraint.fill_board(board, new_num_objects)
                    for new_board in new_boards:
                        num_boards += 1
                        next_boards_file.write(str(new_board) + "\n")
                    
                    # Calculate percentage complete for logging
                    current_board = j + chunk_size * chunk + 1
                    current_percentage = int(current_board * 100/last_boards)
                    if current_percentage > last_update:
                        print(str(current_percentage) + "% complete: " + str(current_board) + "/" + str(last_boards), flush=True)
                        last_update = current_percentage
                
                boards = []
                chunk += 1
            print(flush=True)
            
            next_boards_file.close()

            # Filter boards for parallelization after the first constraint
            if i == 0 and parallel is not None:
                index, cores = parallel
                with open("tmp_boards_0.b", "r") as f:
                    next_boards = f.readlines()
                next_boards = [board.rstrip("\r\n") for i, board in enumerate(next_boards) if i % cores == index]
                num_boards = len(next_boards)
                with open("tmp_boards_0.b", "w") as f:
                    f.write("\n".join(next_boards) + "\n")
                
            # Remove temporary file
            if boards_file:
                boards_file.close()
                os.remove("tmp_boards_" + str(i-1) + ".b")            
            
            # Open new boards file and next boards file
            boards_file = open("tmp_boards_" + str(i) + ".b", "r")
            if i + 1 < len(constraints):
                next_boards_file = open("tmp_boards_" + str(i+1) + ".b", "w")
            boards = []

            total_chunks = max(math.ceil(num_boards/chunk_size), 1)
            last_boards = num_boards
        
        # Close temporary files
        if boards_file:
            boards_file.close()
            
        next_boards_file.close()
        
        # Open last boards file and final file to hold finished boards
        boards_file = open("tmp_boards_" + str(len(constraints)-1) + ".b", "r")
        boards = []
        final_boards_file = open(filename, "w")
        
        more_boards = True
        
        print("Finishing boards with remaining objects", flush=True)
        chunk = 0
        last_update = 0
        
        # Retrieve boards from the last board file
        while more_boards:
            if len(boards) == 0:
                # Pull in boards (up to chunk size)
                while len(boards) < chunk_size:
                    board_str = boards_file.readline().rstrip("\r\n")
                    if len(board_str) == 0:
                        more_boards = False
                        break
                    else:
                        boards.append(Board.parse(board_str))
            
            # Fill in all remaining boards
            #print("Processing chunk " + str(chunk+1) + "/" + str(total_chunks))
            for i, board in enumerate(boards):
                #print("Processing chunk " + str(chunk + 1) + "/" + str(total_chunks) + 
                #      ", board " + str(i+1) + "/" + str(len(boards)), end="        \r")
                # Collect remaining objects and all constraints relevant to them
                new_num_objects = self._subtract_num_objects(board)
                remaining_objects = self._list_objects(new_num_objects)
                relevant_constraints = self._relevant_constraints(remaining_objects)
                # Create all permutations of remaining objects to put in the board
                perms = set(itertools.permutations(remaining_objects))

                for perm in perms:
                    board_copy = board.copy()
                    j = 0
                    # Fill in board with this permutation of board objects
                    for k, obj in enumerate(board):
                        if board[k] is None:
                            board_copy[k] = perm[j]
                            j += 1
                            
                    # If the new board meets all relevant constraints, add it to the file
                    if board_copy.check_constraints(relevant_constraints):
                        final_boards_file.write(str(board_copy) + "\n")
                             
                # Calculate percentage for logging
                current_board = i + chunk_size * chunk + 1
                current_percentage = int(current_board * 100/last_boards)
                if current_percentage > last_update:
                    print(str(current_percentage) + "% complete: " + str(current_board) + "/" + str(last_boards), flush=True)
                    last_update = current_percentage
                    
            boards = []
            chunk += 1
        print(flush=True)
        
        # Clean up files
        boards_file.close()
        os.remove("tmp_boards_" + str(len(constraints)-1) + ".b")
        final_boards_file.close()

# Standard board types
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

twelve_type = BoardType(twelve_board_constraints, twelve_board_numbers, 6, 1)
eighteen_type = BoardType(eighteen_board_constraints, eighteen_board_numbers, 6, 2)
twentyfour_type = BoardType(twentyfour_board_constraints, twentyfour_board_numbers, 7, 3)

sector_types = {
    12: twelve_type,
    18: eighteen_type,
    24: twentyfour_type
}
