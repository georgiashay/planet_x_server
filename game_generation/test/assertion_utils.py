from planetx_game.board import Board

def compare_unordered_list_of_lists(result, expected):
    result_tuples = sorted([tuple([item if item is not None else "" for item in item_list]) for item_list in result])
    expected_tuples = sorted([tuple([item if item is not None else "" for item in item_list]) for item_list in expected])
    assert result_tuples == expected_tuples

def compare_unordered_list_of_boards(result, expected):
    result_sorted = sorted(result, key=lambda b: tuple([obj if obj is not None else "" for obj in b.objects]))
    expected_sorted = sorted(expected, key=lambda b: tuple([obj if obj is not None else "" for obj in b.objects]))
    assert result_sorted == expected_sorted
    
def rotate(lists):
    n = len(lists[0])
    new_lists = []
    for i in range(n):
        for l in lists:
            new_lists.append(l[n-i:n] + l[:n-i])
    return new_lists

def rotate_boards(boards):
    n = len(boards[0])
    new_boards = []
    for i in range(n):
        for b in boards:
            new_boards.append(Board(b.objects[n-i:n] + b.objects[:n-i]))
    return new_boards