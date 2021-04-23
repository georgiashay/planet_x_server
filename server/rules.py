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
                            and board[i-1] is self.space_object2 or board[i+1] is self.space_object2]
        
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
        if any(isinstance(constraint, cls) and constraint == cls(space_object1, space_object2, cls.qualifier)):
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
    def eliminate_sectors(cls, space_object1, space_object2, data, board):  
        """
        Create a rule that will eliminate possible positions of space_object1, where 
        space_object1 and data.elimination_object are ambiguous on survey/target
        
        Only the sectors in data.need_eliminated are ambiguous, and the sectors in 
        data.already_eliminated have been eliminated by other rules. To be viable,
        this rule must eliminate at least data.minimum sectors, and if possible 
        should eliminate data.goal sectors.
        """
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
        if any(isinstance(constraint, cls) and constraint == cls(space_object1, space_object2, cls.qualifier)):
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
    def eliminate_sectors(cls, space_object1, space_object2, data, board):
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