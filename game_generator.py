from game import *
import db_ops

class GameGenerator:
    @classmethod
    def generate_games(cls, board_type, input_filename, output_filename, chunk_size=float('inf'), parallel=None):
        with open(input_filename) as f:
            for i, line in enumerate(f):
                pass
            num_boards = i+1
                        
        board_file = open(input_filename, "r")        
        game_file = open(output_filename, "w")
        
        boards = []
        more_boards = True
        
        current_board = 0
        last_update = 0
        chunk = 0
        while more_boards:
            if len(boards) == 0:
                while len(boards) < chunk_size:
                    board_str = board_file.readline().rstrip("\r\n")
                    if len(board_str) == 0:
                        more_boards = False
                        break
                    else:
                        boards.append(Board.parse(board_str))
            
            for board in boards:
                game = Game.generate_from_board(board, board_type)
                if game is not None:
                    game_file.write(game.code() + "\n")
                    
                current_board += 1
                current_percentage = round((current_board + 1)*100/num_boards, 2)
                if current_percentage > last_update:
                    print(str(current_percentage) + "% complete " + str(current_board+1) + "/" + str(num_boards))
                    last_update = current_percentage
            
            boards = []
        
        board_file.close()
        game_file.close()
        
    @staticmethod
    def _game_code(i, length):
        code = ""
        while i > 0:
            n = (i % 9) + 1
            i = int(i/9)
            l = i % 25
            if l < 14:
                c = chr(l + 65)
            else:
                c = chr(l + 66)
            i = int(i/25)
            code = c + str(n) + code
        if len(code) < length:
            code = "A1" * ((length - len(code))//2) + code
        return code
    
    @staticmethod
    def _generate_game_codes(total_games):
        code_length = 0
        n = total_games
        while n > 0:
            code_length += 2
            n = int(n/(25 * 9))
        
        nums = random.sample(range((25*9)**(code_length//2)), total_games)
        codes = [GameGenerator._game_code(num, code_length) for num in nums]
        return codes
        
    @classmethod
    def add_to_database(cls, input_filename, chunk_size=float('inf')):
        num_games = 0
        with open(input_filename, "r") as f:
            for i, line in enumerate(f):
                pass
            num_games = i + 1
            
        game_codes = GameGenerator._generate_game_codes(num_games)
        print("Generated " + str(len(game_codes)) + " codes")

        game_file = open(input_filename, "r")
        game_strs = game_file.readlines()
        game_strs = [game_str.rstrip("\r\n") for game_str in game_strs]
        
        if chunk_size == float('inf'):
            chunk_size = num_games
            
        num_chunks = math.ceil(num_games/chunk_size)
        
        for i in range(0, len(game_strs), chunk_size):
            print("Chunk " + str(i//chunk_size) + "/" + str(num_chunks))
            some_strs = game_strs[i:i+chunk_size]
            some_codes = game_codes[i:i+chunk_size]
        
            db_ops.add_games_by_str(some_strs, some_codes)