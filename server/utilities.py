def _permutations_multi(lst):
    if len(lst) == 0:
        return
    elif len(lst) == 1:
        yield lst
    else:
        for i in range(len(lst)):
            if i == 0 or lst[i] != lst[i-1]:
                rest = lst[:i] + lst[i+1:]
                for p in _permutations_multi(rest):
                    yield [lst[i]] + p

def permutations_multi(counts):
    lst = []
    for val in counts:
        for i in range(counts[val]):
            lst.append(val)
    yield from _permutations_multi(lst)
    
def sum_counts(d):
    s = 0
    for k in d:
        s += d[k]
    return s
                            
def _fill_no_touch(prev, counts, holes, no_touch_objs, t=0):
    if len(counts.keys()) == 0:
        if all(holes):
            if len(holes) == 0 or \
            (holes[0][0] == prev or holes[0][0] not in no_touch_objs or prev not in no_touch_objs):
                yield [None]*len(holes)
        return
    else:
        if holes[0] and (holes[0][0] == prev or holes[0][0] not in no_touch_objs or prev not in no_touch_objs):
            for p in _fill_no_touch(holes[0][-1], counts, holes[1:], no_touch_objs, t+1):
                yield [None] + p
        else:
            first_objs = list(counts.keys())
            for obj in first_objs:
                if obj == prev or prev not in no_touch_objs or obj not in no_touch_objs:
                    counts[obj] -= 1
                    if counts[obj] == 0:
                        del counts[obj]
                
                    for p in _fill_no_touch(obj, counts, holes[1:], no_touch_objs, t+1):
                        yield [obj] + p
            
                    if obj in counts:
                        counts[obj] += 1
                    else:
                        counts[obj] = 1

def fill_no_touch(counts, board):
    holes = []
    in_hole = False
    for obj in board:
        if obj is None:
            holes.append(False)
            in_hole = False
        elif in_hole:
            holes[-1] += (obj,)
        else:
            in_hole = True
            holes.append((obj,))
                        
    num_holes = len([val for val in holes if val != False])
    empty = len([obj for obj in board if obj is None]) - sum_counts(counts)
    gaps = num_holes + empty
    
    if len(counts.keys()) > gaps:
        return []
    else:                     
        put_counts = counts.copy()
        if empty > 0:
            put_counts[None] = empty
        for p in _fill_no_touch(None, put_counts, holes, counts.keys()):
            if p[0] == p[-1] or p[0] not in counts or p[-1] not in counts:
                if holes[-1] == False or holes[0] != False or p[0] == holes[-1][-1] \
                or p[0] not in counts or holes[-1][-1] not in counts:
                    board_copy = board.copy()
                    j = 0
                    for i in range(len(board_copy)):
                        if board[i] is None:
                            board_copy[i] = p[j]
                            j += 1
                        elif board[i-1] is None:
                            j += 1
                    yield board_copy
                    
def _fill_no_within(prev, countdown, counts, no_within_objs, board, n, i):
    if (i == len(board)):
        yield []
        return
    
    if board[i] != None:
        if board[i] in no_within_objs:
            if board[i] != prev and countdown != 0:
                return
            new_prev = board[i]
            new_countdown = n
        else:
            new_prev = prev
            new_countdown = countdown - 1
            
        for p in _fill_no_within(new_prev, new_countdown, counts, no_within_objs, board, n, i+1):
            yield [board[i]] + p
        return
        
    obj_choices = list(counts.keys())
    for obj in obj_choices:
        restricted_obj = obj in no_within_objs
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
                
            for p in _fill_no_within(new_prev, new_countdown, counts, no_within_objs, board, n, i+1):
                yield [obj] + p
            
            if obj in counts:
                counts[obj] += 1
            else:
                counts[obj] = 1

def fill_no_within(counts, board, n):
    num_none = len([obj for obj in board if obj is None]) - sum_counts(counts)
    for p in _fill_no_within(None, 0, {**counts, None: num_none}, counts.keys(), board, n, 0):
        first_i = next(i for i, obj in enumerate(p) if obj in counts)
        last_i = next(i for i in range(len(p) - 1, -1, -1) if p[i] in counts and p[i] != p[first_i])
        diff = first_i + (len(p) - last_i)
        if diff > n:
            yield p
            
def _fill_no_self_touch(prev, holes, obj, num_obj, num_none, t=0):
    if num_obj == 0 and num_none == 0:
        if all(holes):
            if len(holes) == 0 or \
            (holes[0][0] != prev or holes[0][0] != obj or prev != obj):
                yield [None]*len(holes)
        return
    else:
        if holes[0] and (holes[0][0] != prev or holes[0][0] != obj or prev != obj):
            for p in _fill_no_self_touch(holes[0][-1], holes[1:], obj, num_obj, num_none, t+1):
                yield [None] + p
        else:
            if num_obj > 0 and obj != prev:
                for p in _fill_no_self_touch(obj, holes[1:], obj, num_obj - 1, num_none, t+1):
                    yield [obj] + p
            if num_none > 0:
                for p in _fill_no_self_touch(None, holes[1:], obj, num_obj, num_none - 1, t+1):
                    yield [None] + p

def fill_no_self_touch(obj, num_obj, board):
    holes = []
    in_hole = False
    for o in board:
        if o is None:
            holes.append(False)
            in_hole = False
        elif in_hole:
            holes[-1] += (o,)
        else:
            in_hole = True
            holes.append((o,))
                        
    num_holes = len([val for val in holes if val != False])
    empty = len([o for o in board if o is None]) - num_obj
    gaps = num_holes + empty
    
    if num_obj > gaps:
        return []
    else:                     
        for p in _fill_no_self_touch(None, holes, obj, num_obj, empty):
            if p[0] != p[-1] or p[0] != obj or p[-1] != obj:
                if holes[-1] == False or holes[0] != False or p[0] != holes[-1][-1] \
                or p[0] != obj or holes[-1][-1] != obj:
                    board_copy = board.copy()
                    j = 0
                    for i in range(len(board_copy)):
                        if board[i] is None:
                            board_copy[i] = p[j]
                            j += 1
                        elif board[i-1] is None:
                            j += 1
                    yield board_copy