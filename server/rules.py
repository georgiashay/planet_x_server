class AdjacentRule(RelationRule):
    """
    A rule stating that two objects are or aren't adjacent to one another
    """
    def __init__(self, space_object1, space_object2, qualifier):
        self.space_object1 = space_object1
        self.space_object2 = space_object2
        self.qualifier = qualifier
        
    def __repr__(self):
        return "<" + self.qualifier.name + " " + repr(self.space_object1) + " adjacent to " \
                + repr(self.space_object2) + ">"
    
    def __str__(self):
        return str(self.qualifier) + " " + self.space_object1.name() + " is adjacent to " + \
                self.space_object2.one() + " " + self.space_object2.name() + "."
    
    def text(self, board):
        num_object1 = board.num_objects()[self.space_object1]
        num_object2 = board.num_objects()[self.space_object2]
        return self.qualifier.for_object(self.space_object1, num_object1) + " adjacent to " + \
                self.space_object2.any_of(num_object2) + "."
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.qualifier == other.qualifier:
                if self.qualifier is RuleQualifier.NONE or self.qualifier is RuleQualifier.AT_LEAST_ONE:
                    # Mutual rules - i.e. space objects can be swapped
                    return self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2 or \
                            self.space_object1 == other.space_object2 and self.space_object2 == other.space_object1
                else:
                    # One way rules - i.e. space objects cannot be swapped
                    return self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2
            else:
                return False
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def is_satisfied(self, board):
        adjacent_idxs = [i for i in range(len(board)) if board[i] is self.space_object1
                            and (board[i-1] is self.space_object2 or board[i+1] is self.space_object2)]
        
        if self.qualifier is RuleQualifier.NONE:
            return len(adjacent_idxs) == 0
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return len(adjacent_idxs) > 0
        else:
            return len(adjacent_idxs) == board.num_objects()[self.space_object1]
    
    def is_immediately_limiting(self):
        return False

    def disallowed_sectors(self):
        return []
    
    def _fill_board_none(self, board, num_objects):
        if not self.is_satisfied(board):
            # There are already two adjacent in this board, cannot meet rule
            return []
        
        num_obj1 = num_objects[self.space_object1]
        num_obj2 = num_objects[self.space_object2]
        
        for obj in board:
            if obj is self.space_object1:
                num_obj1 -= 1
            elif obj is self.space_object2:
                num_obj2 -= 1
        
        board_perms = fill_no_touch({self.space_object1: num_obj1, self.space_object2: num_obj2}, board)
        return [Board(board_objects) for board_objects in board_perms]
    
    
    def _fill_board_every(self, board, num_objects, num_objects_left, start_i=0):
        # num_objects: how many should be on the board starting from start_i
        # num_objects_left: how many still need to be placed
        num_obj1 = num_objects[self.space_object1]
        num_obj2 = num_objects[self.space_object2]
        
        num_obj1_left = num_objects_left[self.space_object1]
        num_obj2_left = num_objects_left[self.space_object2]
                
        new_num_objects = num_objects.copy()
        new_num_objects_left = num_objects_left.copy()

        if num_obj1 == 0:
            return [ board ]
        
        new_boards = []
        for i in range(start_i, len(board)):
            obj = board[i]
            is_obj1 = obj is self.space_object1
            # Attempt to fill each position with an object1 if possible
            if obj is None or is_obj1:
                options = 0
                if is_obj1 or num_obj1_left > 0:
                    if board[i-1] is self.space_object2 or board[i+1] is self.space_object2:
                        options += 1
                        # If there is already an obj2 next to it, fill with obj1 and proceed
                        board_copy = board.copy()
                        board_copy[i] = self.space_object1
                        new_num_objects[self.space_object1] = num_obj1 - 1
                        new_num_objects[self.space_object2] = num_obj2
                        new_num_objects_left[self.space_object1] = num_obj1_left - (not is_obj1)
                        new_num_objects_left[self.space_object2] = num_obj2
                        new_boards.extend(self._fill_board_every(board_copy, new_num_objects, new_num_objects_left, i+1))
                    elif num_obj2_left > 0:
                        # Otherwise there must be obj2 left to use
                        if board[i-1] is None and (i-2 < 0 or board[i-2] is not self.space_object1):
                            # Do not put an obj2 on the left if there is a obj1
                            # already to the left of that, to avoid duplicate boards
                            # Only follow this restriction if we are looking at a space object that we placed 
                            # under this algorithm, not one that existed before: i.e. it's ok if said object 
                            # is around the end of the board (to the back)
                            options += 1
                            board_copy = board.copy()
                            board_copy[i] = self.space_object1
                            board_copy[i-1] = self.space_object2
                            new_num_objects[self.space_object1] = num_obj1 - 1
                            new_num_objects[self.space_object2] = num_obj2 - 1
                            new_num_objects_left[self.space_object1] = num_obj1_left - (not is_obj1)
                            new_num_objects_left[self.space_object2] = num_obj2_left - 1
                            new_boards.extend(self._fill_board_every(board_copy, new_num_objects, new_num_objects_left, i+1))
                    
                        if board[i+1] is None and (i+2 < len(board) or board[i+2] is not self.space_object1):
                            # Do not put an obj2 on the right if there is a obj1
                            # to the right of that, to avoid duplicate boards
                            # Only follow this restriction if we are looking at a space object that we placed 
                            # under this algorithm, not one that existed before: i.e. it's ok as long it's 
                            # not around the end of the board (to the front)
                            options += 1
                            board_copy = board.copy()
                            board_copy[i] = self.space_object1
                            board_copy[i+1] = self.space_object2
                            new_num_objects[self.space_object1] = num_obj1 - 1
                            new_num_objects[self.space_object2] = num_obj2 - 1
                            new_num_objects_left[self.space_object1] = num_obj1_left - (not is_obj1)
                            new_num_objects_left[self.space_object2] = num_obj2_left - 1
                            new_boards.extend(self._fill_board_every(board_copy, new_num_objects, new_num_objects_left, i+2))

                if is_obj1 and options == 0:
                    # Unable to place an obj2 next to an existing obj1
                    return []
            
        return new_boards
    
    def fill_board(self, board, num_objects):
        if self.qualifier is RuleQualifier.NONE:
            return self._fill_board_none(board, num_objects)
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            # Not yet supported
            return None
        else:
            num_objects_left = num_objects.copy()
            for obj in board:
                if obj is self.space_object1 or obj is self.space_object2:
                    num_objects_left[obj] -= 1
                
            return self._fill_board_every(board, num_objects, num_objects_left)
            
    def affects(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object1, self.space_object2 ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object1 ]
    
    def completes(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object1, self.space_object2 ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object1 ]
    
    def adds(self):
        return [ self.space_object1, self.space_object2 ]
    
    @classmethod
    def generate_rule(cls, board, constraints, space_object1, space_object2):
        # Some are already constrained, don't generate these rules
        if any(isinstance(constraint, cls) and constraint == cls(space_object1, space_object2, constraint.qualifier)
              for constraint in constraints):
            return None

        num_adjacent = 0
        
        # Count how many object1s are adjacent to object2s 
        for i, obj in enumerate(board):
            if obj is space_object1:
                if board[i-1] is space_object2 or board[i+1] is space_object2:
                    num_adjacent += 1
        
        num_object1 = board.num_objects()[space_object1]
        num_object2 = board.num_objects()[space_object2]
        
        # Create rule options
        if num_adjacent == 0:
            # None were adjacent
            qualifier_options = [RuleQualifier.NONE]
        elif num_adjacent < num_object1:
            # Some were adjacent
            qualifier_options = [RuleQualifier.AT_LEAST_ONE]
        else:
            # Every one was adjacent - also means at least one was 
            qualifier_options = [RuleQualifier.AT_LEAST_ONE, RuleQualifier.EVERY]
        
        # At least one just means every
        if num_object1 == 1:
            qualifier_options = [option for option in qualifier_options \
                                if option is not RuleQualifier.AT_LEAST_ONE]
        
        # Finding one object2 finds all object1s
        if num_object1 >= 2 * num_object2:
            qualifier_options = [option for option in qualifier_options \
                                if option is not RuleQualifier.EVERY]
            
        if len(qualifier_options) == 0:
            return None
        
        qualifier = random.choice(qualifier_options)
        return AdjacentRule(space_object1, space_object2, qualifier)
    
    @classmethod
    def eliminate_sectors(cls, space_object1, space_object2, data, board, constraints):  
        """
        Create a rule that will eliminate possible positions of space_object1, where 
        space_object1 and data.elimination_object are ambiguous on survey/target
        
        Only the sectors in data.need_eliminated are ambiguous, and the sectors in 
        data.already_eliminated have been eliminated by other rules. To be viable,
        this rule must eliminate at least data.minimum sectors, and if possible 
        should eliminate data.goal sectors.
        """
        # Some are already constrained, don't generate these rules
        if any(isinstance(constraint, cls) and constraint == cls(space_object1, space_object2, constraint.qualifier)
              for constraint in constraints):
            return None
        
        obj1_num_adjacent = 0
        el_adjacent = set()
        
        num_obj1 = board.num_objects()[space_object1]
        num_obj2 = board.num_objects()[space_object2]
        num_el = len(data.need_eliminated)
        
        # If the eliminated object is space object2, then space object1 "looks like" space object 2
        adjacent_objs = [space_object2]
        if data.elimination_object is space_object2:
            adjacent_objs.append(space_object1)
        
        # Count how many are adjacent
        for i, obj in enumerate(board):
            # An "object 2" is adjacent to this sector
            if board[i-1] in adjacent_objs or board[i+1] in adjacent_objs:
                if obj is space_object1:
                    # Count an object 1 being adjacent
                    obj1_num_adjacent += 1
                elif obj is data.elimination_object and i in data.need_eliminated:
                    # Add to list of sectors where the eliminated object is adjacent
                    el_adjacent.add(i)
                            
        # Only using "not adjacent" rules to avoid too powerful rules
        # There must be no object 1's ajacent to an 'object 2' 
        if obj1_num_adjacent == 0 and len(el_adjacent) > 0:
            eliminated = el_adjacent - data.already_eliminated
            # Must eliminate data.minimum new sectors
            if len(eliminated) >= data.minimum:
                rule = AdjacentRule(space_object1, space_object2, RuleQualifier.NONE)
                return eliminated, rule
        
        return None, None
    
    def code(self):
        return "A" + str(self.space_object1) + str(self.space_object2) + self.qualifier.code()
    
    @classmethod
    def parse(cls, s):
        space_object1 = SpaceObject.parse(s[1])
        space_object2 = SpaceObject.parse(s[2])
        qualifier = RuleQualifier.parse(s[3])
        return cls(space_object1, space_object2, qualifier)
    
    def to_json(self, board):
        return {
            "ruleType": "ADJACENT",
            "spaceObject1": self.space_object1.to_json(),
            "spaceObject2": self.space_object2.to_json(),
            "qualifier": self.qualifier.to_json(),
            "categoryName": self.category_name(),
            "text": self.text(board)
        }
    
    
class OppositeRule(RelationRule):
    """
    A rule stating that two objects are or aren't opposite to one another
    """
    def __init__(self, space_object1, space_object2, qualifier):
        self.space_object1 = space_object1
        self.space_object2 = space_object2
        self.qualifier = qualifier
        
    def __repr__(self):
        return "<" + self.qualifier.name + " " + repr(self.space_object1) + " opposite " \
                + repr(self.space_object2) + ">"
    
    def __str__(self):
        return str(self.qualifier) + " " + self.space_object1.name() + " is directly opposite " + \
                self.space_object2.one() + " " + self.space_object2.name() + "."
    
    def text(self, board):
        num_object1 = board.num_objects()[self.space_object1]
        num_object2 = board.num_objects()[self.space_object2]
        return self.qualifier.for_object(self.space_object1, num_object1) + " directly opposite " + \
                self.space_object2.any_of(num_object2) + "." 
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.qualifier == other.qualifier:
                if self.qualifier is RuleQualifier.NONE or self.qualifier is RuleQualifier.AT_LEAST_ONE:
                    # Mutual rules - i.e. space objects can be swapped
                    return self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2 or \
                            self.space_object1 == other.space_object2 and self.space_object2 == other.space_object1
                else:
                    # One way rules - i.e. space objects cannot be swapped
                    return self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2
            else:
                return False
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def is_satisfied(self, board):
        half = len(board) // 2
        opposite_idxs = [i for i in range(len(board)) if board[i] is self.space_object1 
                            and board[i+half] is self.space_object2]
        
        if self.qualifier is RuleQualifier.NONE:
            return len(opposite_idxs) == 0
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return len(opposite_idxs) > 0
        else:
            return len(opposite_idxs) == board.num_objects()[self.space_object1]
    
    def is_immediately_limiting(self):
        return False

    def disallowed_sectors(self):
        return []
    
    def _fill_board_none(self, board, num_objects):
        if not self.is_satisfied(board):
            # There are already two opposite in this board, cannot meet rule
            return []
        
        num_obj1 = num_objects[self.space_object1]
        num_obj2 = num_objects[self.space_object2]
        num_none = 0
        
        for obj in board:
            if obj is self.space_object1:
                num_obj1 -= 1
            elif obj is self.space_object2:
                num_obj2 -= 1
            elif obj is None:
                num_none += 1
        
        num_none -= (num_obj1 + num_obj2)
        
        new_boards = []
        
        perms = permutations_multi({self.space_object1: num_obj1, self.space_object2: num_obj2, None: num_none})
        for p in perms:
            board_copy = board.copy()
            j = 0
            for i in range(len(board_copy)):
                if board_copy[i] is None:
                    board_copy[i] = p[j]
                    j += 1
            if self.is_satisfied(board_copy):
                new_boards.append(board_copy)
        
        return new_boards
    
    
    def _fill_board_every(self, board, num_objects, num_objects_left, start_i=0):
        # num_objects: how many should be on the board starting from start_i
        # num_objects_left: how many still need to be placed
        num_obj1 = num_objects[self.space_object1]
        
        num_obj1_left = num_objects_left[self.space_object1]
        num_obj2_left = num_objects_left[self.space_object2]
                
        new_num_objects = num_objects.copy()
        new_num_objects_left = num_objects_left.copy()

        if num_obj1 == 0:
            return [ board ]
        
        half = len(board) // 2
        
        new_boards = []
        for i in range(start_i, len(board)):
            obj = board[i]
            is_obj1 = obj is self.space_object1
            if obj is None or is_obj1:
                already_opp = (board[i + half] is self.space_object2)
                board_copy = board.copy()
                board_copy[i + half] = self.space_object2
                board_copy[i] = self.space_object1

                if (already_opp or num_obj2_left > 0) and (is_obj1 or num_obj1_left > 0):
                    new_num_objects[self.space_object1] = num_obj1 - 1
                    new_num_objects_left[self.space_object1] = num_obj1_left - (not is_obj1)
                    new_num_objects_left[self.space_object2] = num_obj2_left - (not already_opp)
                    new_boards.extend(self._fill_board_every(board_copy, new_num_objects, new_num_objects_left, i+1))
                    
        return new_boards
 
    def fill_board(self, board, num_objects):
        if self.qualifier is RuleQualifier.NONE:
            return self._fill_board_none(board, num_objects)
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            # Not yet supported
            return None
        else:
            num_objects_left = num_objects.copy()
            for obj in board:
                if obj is self.space_object1 or obj is self.space_object2:
                    num_objects_left[obj] -= 1
                
            return self._fill_board_every(board, num_objects, num_objects_left)
            
    def affects(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object1, self.space_object2 ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object1 ]
    
    def completes(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object1, self.space_object2 ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object1 ]
    
    def adds(self):
        return [ self.space_object1, self.space_object2 ]
    
    @classmethod
    def generate_rule(cls, board, constraints, space_object1, space_object2):
        # Some are already constrained, don't generate these rules
        if any(isinstance(constraint, cls) and constraint == cls(space_object1, space_object2, constraint.qualifier)
              for constraint in constraints):
            return None
        
        # Board must have an even number of sectors for objects to be opposite each other
        if len(board) % 2 != 0:
            return None
        
        num_opposite = 0
        half = int(len(board) / 2)
        
        # Calculate how many object1's are opposite object2's 
        for i, obj in enumerate(board):
            if obj is space_object1:
                if board[i+half] is space_object2:
                    num_opposite += 1
        
        num_object1 = board.num_objects()[space_object1]
        num_object2 = board.num_objects()[space_object2]
        
        # List possible rules
        if num_opposite == 0:
            # No object1's are opposite object2
            qualifier_options = [RuleQualifier.NONE]
        elif num_opposite < num_object1:
            # Some object1's are opposite object2
            qualifier_options = [RuleQualifier.AT_LEAST_ONE]
        else:
            # Every object1 is opposite an object2, which also means at least one is
            qualifier_options = [RuleQualifier.AT_LEAST_ONE, RuleQualifier.EVERY]
                    
        if num_object1 == num_object2:
            # This would completely determine one object given the other, too powerful
            qualifier_options = [option for option in qualifier_options \
                                if option is not RuleQualifier.EVERY]

        if num_object1 == 1:
            # At least one is the same as every, so drop at least one
            qualifier_options = [option for option in qualifier_options \
                                    if option is not RuleQualifier.AT_LEAST_ONE]
                    
        if len(qualifier_options) == 0:
            return None
        
        # Choose a random rule of the options
        qualifier = random.choice(qualifier_options)
        return OppositeRule(space_object1, space_object2, qualifier)
    
    @classmethod
    def eliminate_sectors(cls, space_object1, space_object2, data, board, constraints):
        # Some are already constrained, don't generate these rules
        if any(isinstance(constraint, cls) and constraint == cls(space_object1, space_object2, constraint.qualifier)
              for constraint in constraints):
            return None
        
        # Board must have an even number of sectors for objects to be opposite each other
        if len(board) % 2 != 0:
            return None, None
        
        half = int(len(board) / 2)

        obj1_num_opposite = 0
        el_opposite = set()
        
        num_obj1 = board.num_objects()[space_object1]
        num_obj2 = board.num_objects()[space_object2]
        num_el = len(data.need_eliminated)
        
        # If space_object2 is the object we are trying to eliminate, it is ambiguous
        # with space_object1 and we should check for objects being opposite it as well
        opposite_objs = [space_object2]
        if data.elimination_object is space_object2:
            opposite_objs.append(space_object1)
        
        for i, obj in enumerate(board):
            # Object opposite this sector "looks like" object 2
            if board[i + half] in opposite_objs:
                if obj is space_object1:
                    # Add to count of space object 1 being opposite "object 2"
                    obj1_num_opposite += 1
                elif obj is space_object2 and i in data.need_eliminated:
                    # Add sector to the list of ambiguous sectors also opposite "object 2"
                    el_opposite.add(i)
        
        # Only allowing "not opposite" rules, since "is directly opposite" rules would be too powerful
        # This means that no object1s can appear to be opposite an object2 for this rule to be viable
        if obj1_num_opposite == 0 and len(el_opposite) > 0:
            eliminated = el_opposite - data.already_eliminated
            # There must be at least data.minimum sectors that aren't already eliminated which
            # ARE opposite an "object 2" for enough sectors to be eliminated by this rule
            if len(eliminated) >= data.minimum:
                rule = OppositeRule(space_object1, space_object2, RuleQualifier.NONE)
                return eliminated, rule
        
        return None, None
    
    def code(self):
        return "O" + str(self.space_object1) + str(self.space_object2) + self.qualifier.code()

    @classmethod
    def parse(cls, s):
        space_object1 = SpaceObject.parse(s[1])
        space_object2 = SpaceObject.parse(s[2])
        qualifier = RuleQualifier.parse(s[3])
        return cls(space_object1, space_object2, qualifier)
    
    def to_json(self, board):
        return {
            "ruleType": "OPPOSITE",
            "spaceObject1": self.space_object1.to_json(),
            "spaceObject2": self.space_object2.to_json(),
            "qualifier": self.qualifier.to_json(),
            "categoryName": self.category_name(),
            "text": self.text(board)
        }
    
class WithinRule(RelationRule):
    """
    A rule stating that two objects are or aren't within a certain number of sectors from each other
    """
    def __init__(self, space_object1, space_object2, qualifier, num_sectors):
        self.space_object1 = space_object1
        self.space_object2 = space_object2
        self.qualifier = qualifier
        self.num_sectors = num_sectors
        
    def __repr__(self):
        return "<" + self.qualifier.name + " " + repr(self.space_object1) + " within " + str(self.num_sectors) + \
                " sectors of " + repr(self.space_object2) + ">"
    
    def __str__(self):
        return str(self.qualifier) + " " + self.space_object1.name() + " is within " + str(self.num_sectors) + \
                " sectors of " + self.space_object2.one() + " " + self.space_object2.name() + "."
    
    def text(self, board):
        num_object1 = board.num_objects()[self.space_object1]
        num_object2 = board.num_objects()[self.space_object2]
        return self.qualifier.for_object(self.space_object1, num_object1) + " within " + \
                str(self.num_sectors) + " sectors of " + self.space_object2.any_of(num_object2) + "."
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.qualifier == other.qualifier and self.num_sectors == other.num_sectors:
                if self.qualifier is RuleQualifier.NONE or self.qualifier is RuleQualifier.AT_LEAST_ONE:
                    # Mutual rules - i.e. space objects can be swapped
                    return self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2 or \
                            self.space_object1 == other.space_object2 and self.space_object2 == other.space_object1
                else:
                    # One way rules - i.e. space objects cannot be swapped
                    return self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2
            else:
                return False
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def covers(self, other):
        if isinstance(other, self.__class__):
            if self.qualifier == other.qualifier:
                if self.qualifier is RuleQualifier.NONE:
                    # Mutual rules - i.e. space objects can be swapped
                    return self.num_sectors >= other.num_sectors and \
                            (self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2 or \
                            self.space_object1 == other.space_object2 and self.space_object2 == other.space_object1)
                elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
                    # Mutual rules - i.e. space objects can be swapped
                    return self.num_sectors <= other.num_sectors and \
                            (self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2 or \
                            self.space_object1 == other.space_object2 and self.space_object2 == other.space_object1)
                else:
                    # One way rules - i.e. space objects cannot be swapped
                    return self.num_sectors <= other.num_sectors and \
                            self.space_object1 == other.space_object1 and self.space_object2 == other.space_object2
            else:
                return False
        else:
            return False
        
    def _is_satisfied_none(self, board):
        prev = None
        countdown = 0
        is_valid = True
        for i in range(-self.num_sectors, len(board)):
            obj = board[i]
            if obj is self.space_object1 or obj is self.space_object2:
                if countdown != 0 and obj != prev:
                    is_valid = False
                    break
                prev = obj
                countdown = self.num_sectors
            else:
                countdown = max(0, countdown - 1)
                
        return is_valid
    
    def _num_within(self, board):
        prev = None, None
        countdown = 0
        within_indices = set()
        for i in range(-self.num_sectors, len(board)):
            if board[i] is self.space_object1:
                if countdown > 0 and prev[0] is self.space_object2:
                    within_indices.add(i % len(board))
                prev = board[i], i
                countdown = self.num_sectors
            elif board[i] is self.space_object2:
                if countdown > 0 and prev[1] is not None:
                    within_indices.add(prev[1] % len(board))
                prev = board[i], i
                countdown = self.num_sectors
            else:
                countdown = max(0, countdown - 1)
        return len(within_indices)
    
    def is_satisfied(self, board):
        if self.qualifier is RuleQualifier.NONE:
            return self._is_satisfied_none(board)
        else:
            num_within = self._num_within(board)
            if self.qualifier is RuleQualifier.AT_LEAST_ONE:
                return num_within > 0
            else:
                return num_within == board.num_objects()[self.space_object1]
    
    def is_immediately_limiting(self):
        return False

    def disallowed_sectors(self):
        return []
    
    def _fill_board_none(self, board, num_objects):
        if not self.is_satisfied(board):
            # There are already some within this range, cannot meet rule
            return []
                
        num_obj1 = num_objects[self.space_object1]
        num_obj2 = num_objects[self.space_object2]
        
        if self.space_object1 in board.num_objects():
            num_obj1 -= board.num_objects()[self.space_object1]
        
        if self.space_object2 in board.num_objects():
            num_obj2 -= board.num_objects()[self.space_object2]
                
        return [Board(b) for b in fill_no_within({self.space_object1: num_obj1, self.space_object2: num_obj2}, \
                                                 board, self.num_sectors)]
   
    def _fill_board_every(self, board, num_obj1, num_objects_left, start_i=0):
        # num_obj1: how many should be on the board starting from start_i
        # num_objects_left: how many still need to be placed
        num_obj1_left = num_objects_left[self.space_object1]
        num_obj2_left = num_objects_left[self.space_object2]
                
        new_num_objects_left = num_objects_left.copy()

        if num_obj1 == 0:
            return [ board ]
        
        board_size = len(board)
                
        new_boards = []
        for i in range(start_i, board_size):
            obj = board[i]
            is_obj1 = obj is self.space_object1
            # Attempt to fill each position with an object1 is possible
            if obj is None or is_obj1:
                options = 0
                if is_obj1 or num_obj1_left > 0:
                    if self.space_object2 in board[i-self.num_sectors:i+self.num_sectors+1]:
                        # If there is already an obj2 in range, fill with obj1 and proceed
                        options += 1
                        board_copy = board.copy()
                        board_copy[i] = self.space_object1
                        new_num_objects_left[self.space_object1] = num_obj1_left - (not is_obj1)
                        new_num_objects_left[self.space_object2] = num_obj2_left
                        new_boards.extend(self._fill_board_every(board_copy, num_obj1 - 1, new_num_objects_left, i+1))
                    elif num_obj2_left > 0:
                        # Otherwise there must be obj2 left to use
                        for j in range(i-self.num_sectors, i):
                            if board[j] is None:
                                
                                if not any(k >= 0 and board[k] is self.space_object1 for k in range(max(0, j-self.num_sectors), j)):
                                    options += 1
                                    board_copy = board.copy() 
                                    board_copy[i] = self.space_object1
                                    board_copy[j] = self.space_object2
                                    new_num_objects_left[self.space_object1] = num_obj1_left - (not is_obj1)
                                    new_num_objects_left[self.space_object2] = num_obj2_left - 1
                                    new_boards.extend(self._fill_board_every(board_copy, num_obj1 - 1, new_num_objects_left, i+1))

                        max_sector = min(i+self.num_sectors+1, len(board)+(i-self.num_sectors))
                        for j in range(i+1, max_sector):
                            if board[j] is None:
                                if not any(k < len(board) and board[k] is self.space_object1 for k in range(j+1, min(j+self.num_sectors+1, board_size))):
                                    options += 1
                                    board_copy = board.copy() 
                                    board_copy[i] = self.space_object1
                                    board_copy[j] = self.space_object2
                                    new_num_objects_left[self.space_object1] = num_obj1_left - (not is_obj1)
                                    new_num_objects_left[self.space_object2] = num_obj2_left - 1
                                    new_boards.extend(self._fill_board_every(board_copy, num_obj1 - 1, new_num_objects_left, i+1))

                    if is_obj1 and options == 0:
                        # Unable to place an obj2 next to an existing obj1
                        return []
                
        return new_boards
 
    def fill_board(self, board, num_objects):
        if self.qualifier is RuleQualifier.NONE:
            return self._fill_board_none(board, num_objects)
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            # Not yet supported
            return None
        else:
            num_objects_left = num_objects.copy()
            for obj in board:
                if obj is self.space_object1 or obj is self.space_object2:
                    num_objects_left[obj] -= 1
                
            return self._fill_board_every(board, num_objects[self.space_object1], num_objects_left)
            
    def affects(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object1, self.space_object2 ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object1 ]
    
    def completes(self):
        if self.qualifier is RuleQualifier.NONE:
            return [ self.space_object1, self.space_object2 ]
        elif self.qualifier is RuleQualifier.AT_LEAST_ONE:
            return []
        else:
            return [ self.space_object1 ]
    
    def adds(self):
        return [ self.space_object1, self.space_object2 ]
    
    @staticmethod
    def _circle_dist(i, j, size):
        """
        The distance between i and j on a circle of size size - i.e. modular distance
        """
        dist = abs(i - j)
        return min(dist, size - dist)
    
    @staticmethod
    def _max_min_sectors_away(space_object1, space_object2, board):
        """
        Calculate the minimum and maximum number of sectors any space_object1 is from space_object2
        """
        board_size = len(board)
        obj1_positions = [i for i, obj in enumerate(board) if obj is space_object1]
        obj2_positions = [i for i, obj in enumerate(board) if obj is space_object2]
        
        maximum_sectors = 0
        minimum_sectors = board_size
        for i in obj1_positions:
            # How far away this obj1 is from the nearest obj2
            sectors_away = min(WithinRule._circle_dist(i, j, board_size) for j in obj2_positions)
            if sectors_away > maximum_sectors:
                maximum_sectors = sectors_away
            if sectors_away < minimum_sectors:
                minimum_sectors = sectors_away
        
        return minimum_sectors, maximum_sectors
    
    @staticmethod
    def _max_between(space_object, board):
        max_run = 0
        current_run = 0
        for obj in board:
            if obj == space_object:
                if current_run > max_run:
                    max_run = current_run
                current_run = 0
            else:
                current_run += 1
                
        for obj in board:
            if obj == space_object:
                if current_run > max_run:
                    max_run = current_run
                break
            else:
                current_run += 1
                
        return max_run
    
    @classmethod
    def generate_rule(cls, board, constraints, space_object1, space_object2):
        min_none = 2
        max_every = len(board)
        
        # Some objects are already constrained, must constrain them even further or generate no rule
        for constraint in constraints:
            if isinstance(constraint, cls):
                if constraint.qualifier is RuleQualifier.NONE and \
                { space_object1, space_object2 } == { constraint.space_object1, constraint.space_object2 }:
                    if constraint.num_sectors + 1 > min_none:
                        min_none = constraint.num_sectors + 1
                elif constraint.qualifier is RuleQualifier.EVERY and \
                (space_object1, space_object2) == (constraint.space_object1, constraint.space_object2):
                    if constraint.num_sectors - 1 < max_every:
                        max_every = constraint.num_sectors - 1
        
        num_object1 = board.num_objects()[space_object1]
        num_object2 = board.num_objects()[space_object2]
        
        # There must be more of object 2 (or at least the same amount) than object 1
        if num_object1 > num_object2:
            return None
        
        max_n = int(len(board)/3 - 1)
        max_every = min(max_every, max_n)
        
        min_sectors, max_sectors = cls._max_min_sectors_away(space_object1, space_object2, board)
        
        options = []
        
        if min_sectors > min_none:
            # Create a random number of sectors that no object1 is within object2
            # This must be < min_sectors, because object1 is within that many sectors of object2.
            num_not_within = random.randrange(min_none, min_sectors)
            options.append((RuleQualifier.NONE, num_not_within))
        
        if max_sectors <= max_every:
            max_between_obj2 = cls._max_between(space_object2, board)
            max_for_eliminating = (max_between_obj2 - 1) // 2
            
            max_rule = min(max_for_eliminating, max_every)
            min_rule = max(2, max_sectors)
                    
            if min_rule <= max_rule:
                # Create a random number of sectors that every object1 is within object2
                # This must be at least max_sectors, to cover every possible object1
                num_within = random.randrange(min_rule, max_rule+1)
                options.append((RuleQualifier.EVERY, num_within))
            
        if len(options) == 0:
            return None
        
        # Choose a random rule
        qualifier, num_sectors = random.choice(options)
        return WithinRule(space_object1, space_object2, qualifier, num_sectors)
    
    @classmethod
    def eliminate_sectors(cls, space_object1, space_object2, data, board, constraints):
        """
        Create a rule that will eliminate possible positions of space_object1, where 
        space_object1 and data.elimination_object are ambiguous on survey/target
        
        Only the sectors in data.need_eliminated are ambiguous, and the sectors in 
        data.already_eliminated have been eliminated by other rules. To be viable,
        this rule must eliminate at least data.minimum sectors, and if possible 
        should eliminate data.goal sectors.
        """
        min_none = 2
        max_every = len(board)
        
        # Some objects are already constrained, must constrain them even further or generate no rule
        for constraint in constraints:
            if isinstance(constraint, cls):
                if constraint.qualifier is RuleQualifier.NONE and \
                { space_object1, space_object2 } == { constraint.space_object1, constraint.space_object2 }:
                    if constraint.num_sectors + 1 > min_none:
                        min_none = constraint.num_sectors + 1
                elif constraint.qualifier is RuleQualifier.EVERY and \
                (space_object1, space_object2) == (constraint.space_object1, constraint.space_object2):
                    if constraint.num_sectors - 1 < max_every:
                        max_every = constraint.num_sectors - 1
        
        max_n = int(len(board)/3 - 1)
        max_every = min(max_every, max_n)
        
        board_size = len(board)
        obj1_positions = [i for i, obj in enumerate(board) if obj is space_object1]
        el_positions = data.need_eliminated
        obj2_positions = [i for i, obj in enumerate(board) if obj is space_object2]
        
        # Object 2 appears same as object 1
        if data.elimination_object is space_object2:
            obj2_positions += obj1_positions
        
        # Get the maximum and minimum positions that object 1 is away from an "object 2"
        max_obj1 = 0
        min_obj1 = board_size
        for i in obj1_positions:
            sectors_away = min(WithinRule._circle_dist(i, j, board_size) for j in obj2_positions if j != i)
            if sectors_away > max_obj1:
                max_obj1 = sectors_away
            if sectors_away < min_obj1:
                min_obj1 = sectors_away
        
        # Get how many sectors each eliminated object is from an "object 2"
        # Organize them into an array, with each index containing the indices for elimination objects that are that
        # number of sectors from an "object 2"
        max_el = 0
        min_el = board_size
        el_sectors_away = set()
        el_sectors_away = [[]]
        for i in el_positions:
            sectors_away = min(WithinRule._circle_dist(i, j, board_size) for j in obj2_positions if j != i)
            if sectors_away > len(el_sectors_away) - 1:
                el_sectors_away.extend([[] for j in range(sectors_away-len(el_sectors_away)+1)])
            el_sectors_away[sectors_away].append(i)
            if sectors_away > max_el:
                max_el = sectors_away
            if sectors_away < min_el:
                min_el = sectors_away
                
        options = []
        for sectors_away, matching_el_indices in enumerate(el_sectors_away):
            if sectors_away < min_none or sectors_away > max_every:
                continue
            if sectors_away >= min_obj1:
                # An "every obj1 within n sectors rule" would eliminate the el_objs further than that
                eliminated = set(i for idx_list in el_sectors_away[sectors_away+1:] for i in idx_list)
                if len(eliminated) > 0:
                    eliminated -= data.already_eliminated
                    options.append((sectors_away, eliminated, RuleQualifier.EVERY))
            if sectors_away < max_obj1:
                # A "no obj1 within n sectors rule" would eliminate the el_objs that are within that range
                eliminated = set(i for idx_list in el_sectors_away[:sectors_away+1] for i in idx_list)
                if len(eliminated) > 0:
                    eliminated -= data.already_eliminated
                    options.append((sectors_away, eliminated, RuleQualifier.NONE))

        if len(options) == 0:
            return None, None
                
        max_num_eliminated = max(len(eliminated) for sectors, eliminated, qualifier in options)
        
        # Only consider rules eliminating the goal value if it at least one does
        if max_num_eliminated >= data.goal:
            options = [option for option in options if len(option[1]) >= data.goal]
           
        # In any case, rules must eliminate the minimum number of sectors
        options = [option for option in options if len(option[1]) >= data.minimum]

        if len(options) == 0:
            return None, None
        
        # Generate a random rule from the choices
        rand_rule_opts = random.choice(options)
        
        num_object1 = board.num_objects()[space_object1]
        num_object2 = board.num_objects()[space_object2]
        rand_rule = WithinRule(space_object1, space_object2, rand_rule_opts[2], rand_rule_opts[0])
        
        return rand_rule_opts[1], rand_rule

    def code(self):
        return "W" + str(self.space_object1) + str(self.space_object2) + self.qualifier.code() + str(self.num_sectors)
    
    @classmethod
    def parse(cls, s):
        space_object1 = SpaceObject.parse(s[1])
        space_object2 = SpaceObject.parse(s[2])
        qualifier = RuleQualifier.parse(s[3])
        num_sectors = int(s[4])
        return cls(space_object1, space_object2, qualifier, num_sectors)
    
    def to_json(self, board):
        return {
            "ruleType": "WITHIN",
            "spaceObject1": self.space_object1.to_json(),
            "spaceObject2": self.space_object2.to_json(),
            "numSectors": self.num_sectors,
            "qualifier": self.qualifier.to_json(),
            "categoryName": self.category_name(),
            "text": self.text(board)
        }