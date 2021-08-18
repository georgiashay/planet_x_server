def _permutations_multi(lst):
    if len(lst) == 0:
        # No permutations for empty list 
        return
    elif len(lst) == 1:
        # One permutation for list of one element
        yield lst
    else:
        for i in range(len(lst)):
            # Only generate permutations on the first instance of each value
            if i == 0 or lst[i] != lst[i-1]:
                rest = lst[:i] + lst[i+1:]
                # Choose this value to be the last value
                for p in _permutations_multi(rest):
                    yield [lst[i]] + p

def permutations_multi_old(counts):
    # Construct sorted list of values in counts
    lst = []
    for val in counts:
        for i in range(counts[val]):
            lst.append(val)
    # Return the permutations
    yield from _permutations_multi(lst)
    
def memo_counts(f):
    memo = {}
    
    def helper(counts):
        key = tuple(counts.items())
        if key not in memo:
            memo[key] = list(f(counts))
        return memo[key]
    
    return helper

@memo_counts
def permutations_multi(counts):
    obj_choices = False
    for obj in counts:
        if counts[obj] > 0:
            obj_choices = True
            
            # Reduce count by 1 and generate more permutations
            counts[obj] -= 1
            # Place this value at the end of the list
            for p in permutations_multi(counts):
                yield [obj] + p
            
            counts[obj] += 1
            
    # All objects have a count of 0
    if not obj_choices:
        yield []          
        
def sum_counts(d):
    s = 0
    for k in d:
        s += d[k]
    return s
                            
def _fill_no_touch(prev, counts, holes, no_touch_objs, t=0):
    if len(counts.keys()) == 0:
        if all(holes):
            # If valid so far and all holes left, fill in Nones for holes
            if len(holes) == 0 or \
            (holes[0][0] == prev or holes[0][0] not in no_touch_objs or prev not in no_touch_objs):
                yield [None]*len(holes)
        return
    else:
        # If we're at a hole and valid
        if holes[0] and (holes[0][0] == prev or holes[0][0] not in no_touch_objs or prev not in no_touch_objs):
            # Add a hole and continue
            for p in _fill_no_touch(holes[0][-1], counts, holes[1:], no_touch_objs, t+1):
                yield [None] + p
        else:
            # Loop through each object and check if we're allowed to put it next
            first_objs = list(counts.keys())
            for obj in first_objs:
                if obj == prev or prev not in no_touch_objs or obj not in no_touch_objs:
                    counts[obj] -= 1
                    if counts[obj] == 0:
                        del counts[obj]
                
                    # Place object next and continue
                    for p in _fill_no_touch(obj, counts, holes[1:], no_touch_objs, t+1):
                        yield [obj] + p
            
                    if obj in counts:
                        counts[obj] += 1
                    else:
                        counts[obj] = 1

def fill_no_touch(counts, board):
    # Create list of holes
    # holes = False if not a hole, [first_obj, last_obj] if it's a run of existing objects (i.e. hole)
    holes = []
    in_hole = False
    for obj in board:
        if obj is None:
            holes.append(False)
            in_hole = False
        elif in_hole:
            if holes[-1][-1] in counts and obj in counts and obj != holes[-1][-1]:
                return
            else:
                holes[-1] += (obj,)
        else:
            in_hole = True
            holes.append((obj,))
      
    num_holes = len([val for val in holes if val != False])
    # Number of empties to add
    empty = len([obj for obj in board if obj is None]) - sum_counts(counts)
    # Number of total gaps possible to have
    gaps = num_holes + empty
    
    if len(counts.keys()) > gaps:
        return []
    else:                     
        put_counts = counts.copy()
        if empty > 0:
            put_counts[None] = empty
        for obj in list(put_counts.keys()):
            if put_counts[obj] == 0:
                del put_counts[obj]
        # Fill without touching
        for p in _fill_no_touch(None, put_counts, holes, counts.keys()):
            first_val = p[0] if holes[0] == False else holes[0][0]
            last_val = p[-1] if holes[-1] == False else holes[-1][-1]

            # Make sure first & last value (which wraparound) are allowed
            if first_val == last_val or first_val not in counts or last_val not in counts:
                board_copy = board.copy()
                # Construct board by filling in values
                j = 0
                for i in range(len(board_copy)):
                    if board[i] is None:
                        board_copy[i] = p[j]
                        j += 1
                    elif board[i-1] is None or i == 0:
                        j += 1
                yield board_copy
                
def add_one_no_touch(obj1, obj2, num_obj1, board, start_i=0):
    # No more object left to add, current board is fine
    if num_obj1 == 0:
        yield board
        return 
    
    for i in range(start_i, len(board)):
        # Add object at position i if allowed
        if board[i] is None and board[i-1] != obj2 and board[i+1] != obj2:
            board_copy = board.copy()
            board_copy[i] = obj1
            # Continue adding objects after i
            yield from add_one_no_touch(obj1, obj2, num_obj1 - 1, board_copy, i+1)

def add_two_no_touch(obj1, obj2, num_obj1, num_obj2, board):
    # Add the object 1's 
    with_obj1 = add_one_no_touch(obj1, obj2, num_obj1, board)
    for b in with_obj1:
        # Add the object 2's
        yield from add_one_no_touch(obj2, obj1, num_obj2, b)
        
def add_one_no_self_touch(obj, num_obj, board, start_i=0):
    # No more object left to add, current board is fine
    if num_obj == 0:
        yield board
        return 
    
    for i in range(start_i, len(board)):
        # Add object at position i if allowed
        if board[i] is None and board[i-1] != obj and board[i+1] != obj:
            board_copy = board.copy()
            board_copy[i] = obj
            # Continue adding objects after i
            yield from add_one_no_self_touch(obj, num_obj - 1, board_copy, i+2)
                    
def _fill_no_within(prev, countdown, counts, no_within_objs, board, n, i):
    if (i == len(board)):
        yield []
        return
    
    if board[i] != None:
        if board[i] in no_within_objs:
            if board[i] != prev and countdown != 0:
                # Already violates rule
                return
            # Restart countdown, encountered an object in the set again
            new_prev = board[i]
            new_countdown = n
        else:
            # Moved further from an object, decrease countdown
            new_prev = prev
            new_countdown = max(0, countdown - 1)
        # Fill in board where possible starting after this index
        for p in _fill_no_within(new_prev, new_countdown, counts, no_within_objs, board, n, i+1):
            yield [board[i]] + p
        return
        
    obj_choices = list(counts.keys())
    for obj in obj_choices:
        restricted_obj = obj in no_within_objs
        # Check if object is allowed to be placed here
        if obj == prev or not restricted_obj or countdown == 0:
            counts[obj] -= 1
            if counts[obj] == 0:
                del counts[obj]
                
            if restricted_obj:
                new_countdown = n
                new_prev = obj
            else:
                new_countdown = max(0, countdown - 1)
                new_prev = prev
                
            # Fill in board starting after the index adding this object
            for p in _fill_no_within(new_prev, new_countdown, counts, no_within_objs, board, n, i+1):
                yield [obj] + p
            
            if obj in counts:
                counts[obj] += 1
            else:
                counts[obj] = 1

def fill_no_within(counts, board, n):
    num_none = len([obj for obj in board if obj is None]) - sum_counts(counts)
    for p in _fill_no_within(None, 0, {**counts, None: num_none}, counts.keys(), board, n, 0):
        # Ensure the objects aren't too close to each other due to wraparound
        try:
            first_i = next(i for i, obj in enumerate(p) if obj in counts)
            last_i = next(i for i in range(len(p) - 1, -1, -1) if p[i] in counts and p[i] != p[first_i])
            diff = first_i + (len(p) - last_i)
            if diff > n:
                yield p
        except StopIteration:
            # Not >= 2 objects in counts in the board
            yield p
            
def _fill_no_self_touch(prev, holes, obj, num_obj, num_none, t=0):
    if num_obj == 0 and num_none == 0:
        if all(holes):
            # If there are only holes left and the hole doesn't conflict with the previous object,
            # add the holes
            if len(holes) == 0 or \
            (holes[0][0] != prev or holes[0][0] != obj or prev != obj):
                yield [None]*len(holes)
        return
    else:
        # If there is a hole it doesn't conflict with the previous object, add it
        if holes[0] and (holes[0][0] != prev or holes[0][0] != obj or prev != obj or prev is None):
            for p in _fill_no_self_touch(holes[0][-1], holes[1:], obj, num_obj, num_none, t+1):
                yield [None] + p
        else:
            # If we have objects left and the last thing wasn't this object, we can add it
            if num_obj > 0 and (obj != prev or prev is None):
                for p in _fill_no_self_touch(obj, holes[1:], obj, num_obj - 1, num_none, t+1):
                    yield [obj] + p
            # If we have empties left, we can add one
            if num_none > 0:
                for p in _fill_no_self_touch(None, holes[1:], obj, num_obj, num_none - 1, t+1):
                    yield [None] + p

def fill_no_self_touch(obj, num_obj, board):
    # Build list of holes
    # i.e. false if not a "hole" - i.e. run of objects - or [first_obj, last_obj] of run
    holes = []
    in_hole = False
    for o in board:
        if o is None:
            holes.append(False)
            in_hole = False
        elif in_hole:
            if holes[-1][-1] == obj and o == obj:
                return
            else:
                holes[-1] += (o,)
        else:
            in_hole = True
            holes.append((o,))
                        
    num_holes = len([val for val in holes if val != False])
    # Number of empties to add
    empty = len([o for o in board if o is None]) - num_obj
    # Total potential number of gaps between objs
    gaps = num_holes + empty
    
    if num_obj > gaps:
        return []
    else:
        # Fill without self-touch (array)
        for p in _fill_no_self_touch(None, holes, obj, num_obj, empty):
            # Make sure first and last aren't both obj
            if p[0] != p[-1] or p[0] != obj or p[-1] != obj:
                # Make sure holes at start/end don't make the first and last be both obj
                first = holes[0][0] if holes[0] is not False else p[0]
                last = holes[-1][-1] if holes[-1] is not False else p[-1]
                if first != last or first != obj:
                    board_copy = board.copy()
                    j = 0
                    # Fill in board based on results
                    for i in range(len(board_copy)):
                        if board[i] is None:
                            board_copy[i] = p[j]
                            j += 1
                        elif board[i-1] is None:
                            j += 1
                    yield board_copy     
    
def ordered_partitions(n, I=2, memo={}):
    if n in memo:
        return memo[(n, I)]
    elif n < I:
        memo[(n, I)] = []
        return []
    else:
        partitions = [(n,)]
        for i in range(I, n + 1):
            # Add i to partition
            for p in ordered_partitions(n-i, I):
                partitions.append((i,) + p)

        memo[(n, I)] = partitions
        return partitions

def calc_partitions(n, I=2, memo={}):
    if n in memo:
        return memo[(n, I)]
    elif n < I:
        memo[(n, I)] = []
        return []
    else:
        partitions = [(n,)]
        for i in range(I, n//2 + 1):
            # Add i to partition
            for p in calc_partitions(n-i, i):
                partitions.append((i,) + p)

        memo[(n, I)] = partitions
        return partitions
    
def cartesian_product_sets(l):
    if len(l) == 0:
        yield set()
    else:
        for val in l[0]:
            for p in cartesian_product_sets(l[1:]):
                yield p | {val}
                
def cartesian_product_sets_unique(l):
    return { tuple(sorted(choice)) for choice in cartesian_product_sets(l) }

def cartesian_product_tuples(l):
    if len(l) == 0:
        yield tuple()
    else:
        for val in l[0]:
            for p in cartesian_product_tuples(l[1:]):
                yield (val,) + p
                
def _cartesian_product_sets_no_supersets_with_dups(l):
    for p in cartesian_product_tuples(l):
        result_set = set(p)
        allowed = True
        for val in result_set:
            without_val = result_set - {val}
            # It's not minimal if it would still work with a value removed
            if all(any(x in without_val for x in l[i]) for i in range(len(l))):
                allowed = False
                break
        if allowed:
            yield result_set
    
def cartesian_product_sets_no_supersets(l):
    return { tuple(sorted(choice)) for choice in _cartesian_product_sets_no_supersets_with_dups(l) }
    
        