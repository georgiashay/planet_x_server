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
    
def _fill_no_touch(lst, is_hole):
    if len(lst) == 0:
        if all(is_hole):
            yield [None]*len(is_hole)
        return
    else:
        if is_hole[0]:
            for p in _fill_no_touch(lst, is_hole[1:]):
                yield [None] + p
        else:
            for i in range(len(lst)):
                if i == 0 or lst[i] != lst[i-1]:
                    rest = lst[:i] + lst[i+1:]
                    for p in _fill_no_touch(rest, is_hole[1:]):
                        if len(p) == 0 or p[0] == lst[i] or p[0] is None or lst[i] is None:
                            yield [lst[i]] + p

def fill_no_touch(counts, board):
    is_hole = [obj is not None and board[i-1] is None for i, obj in enumerate(board)]
    is_hole_collapsed = [hole_val for i, hole_val in enumerate(is_hole) if hole_val or board[i] is None]
    holes = sum(is_hole)
    empty = len([obj for obj in board if obj is None]) - sum_counts(counts)
    gaps = holes + empty
    
    if len(counts.keys()) > gaps:
        return []
    else:
        lst = []
        for val in counts:
            for i in range(counts[val]):
                lst.append(val)
        for i in range(empty):
            lst.append(None)
                    
        for p in _fill_no_touch(lst, is_hole_collapsed):
            if p[0] == p[-1] or p[0] is None or p[-1] is None or p[0] not in counts or p[-1] not in counts:
                board_copy = board.copy()
                j = 0
                for i in range(len(board_copy)):
                    if board[i] is None:
                        board_copy[i] = p[j]
                        j += 1
                    elif board[i-1] is None:
                        j += 1
                yield board_copy