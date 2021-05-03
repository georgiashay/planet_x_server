from planetx_game.game import *
import planetx_game.db_ops as db_ops

class GameGenerator:
    @classmethod
    def generate_games(cls, board_type, input_filename, output_filename, chunk_size=float('inf')):
        """
        Generate games from a board file
        
        board_type: A BoardType describing the number of sectors, constraints, and number of rules for the game
        input_filename: The file name for the file with a list of boards, encoded with initials for each sector's
            object and separated by newlines
        output_filename: The file name to put the produced games in, with each game encoded and separated by a 
            newline
        chunk_size: The number of boards to pull into memory from the file at any given time
        """
        # Count number of boards in the file
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
            # Bring in next chunk of boards into memory
            if len(boards) == 0:
                while len(boards) < chunk_size:
                    board_str = board_file.readline().rstrip("\r\n")
                    if len(board_str) == 0:
                        more_boards = False
                        break
                    else:
                        boards.append(Board.parse(board_str))
            
            # Create a game for each board
            for board in boards:
                game = Game.generate_from_board(board, board_type)
                # If a game is generated, add it to the file
                # Some games cannot be generated, or were not generated based on the 
                # random choices made
                if game is not None:
                    game_file.write(game.code() + "\n")
                    
                # Calculate percentage for log
                current_board += 1
                current_percentage = round((current_board + 1)*100/num_boards, 2)
                if current_percentage > last_update:
                    print(str(current_percentage) + "% complete " + str(current_board+1) + "/" + str(num_boards))
                    last_update = current_percentage
            
            boards = []
        
        board_file.close()
        game_file.close()
        
    @staticmethod
    def _code_to_int(code):
        """
        Get the integer corresponding to a game code of the form
        <letter><number><letter><number>. The letters cannot be O/I, and the 
        numbers are 2-9. The 0th game code is A2A2...A2 for any given length.
        
        code: The game code 
        """
        i = 0
        
        while len(code) > 0:
            i *= (8 * 24)
            
            letter = ord(code[0]) - 65
            digit = int(code[1])
            
            i += (digit - 2)
            
            if letter < 8:
                i += letter * 8
            elif letter < 14:
                i += (letter - 1) * 8
            else:
                i += (letter - 2) * 8
                
            code = code[2:]
        
        return i
        
    @staticmethod
    def _game_code(i, length):
        """
        Construct the ith game code of length length. Game codes are in the format
        <letter><number><letter><number>... The letters cannot be O/I, and the numbers 
        are 2-9. The 0th game code is A2A2...A2 for any given length.
        
        length: The number of characters for the game code. Must be even.
        i: The number of the game code to construct
        """
        code = ""
        # Construct code, taking each letter-number pair one by one
        while i > 0:
            # Extract number by taking modulo
            n = (i % 8) + 2
            i = int(i/8)
            # Extract letter index by taking modulo
            l = i % 24

            # Turn letter index into a letter, skipping O and I
            if l < 8:
                c = chr(l + 65)
            elif l < 13:
                c = chr(l + 66)
            else:
                c = chr(l + 67)
            i = int(i/24)
            # Prepend letter-number pair to code
            code = c + str(n) + code
        # Pad with A2's 
        if len(code) < length:
            code = "A2" * ((length - len(code))//2) + code
        return code 
    
    @staticmethod
    def _generate_game_codes(total_games, code_length):
        """
        Generate a random set of game codes for a given number of games
        """
        existing_codes = db_ops.get_game_codes()
        existing_ints = {GameGenerator._code_to_int(code) for code in existing_codes if len(code) == code_length}
        max_code = (24*8)**(code_length//2)
        available_ints = set(range(max_code)) - existing_ints

        # Take a random sample of integers up to the maximum possible for that code length
        nums = random.sample(available_ints, total_games)
        # Get game code for each integer 
        codes = [GameGenerator._game_code(num, code_length) for num in nums]
        return codes
        
    @classmethod
    def add_to_database(cls, input_filename, code_length, chunk_size=float('inf')):
        """
        Add games in game file to database. Assumes that no games exist in the database to 
        start.
        
        input_filename: File containing encoded games, one per line
        chunk_size: The number of games to add to the database at once
        """
        # Count the number of games in the file
        num_games = 0
        with open(input_filename, "r") as f:
            for i, line in enumerate(f):
                pass
            num_games = i + 1
            
        # Create a unique game code for each game
        game_codes = GameGenerator._generate_game_codes(num_games, code_length)
        print("Generated " + str(len(game_codes)) + " codes")

        # Read all game strings
        game_file = open(input_filename, "r")
        game_strs = game_file.readlines()
        game_strs = [game_str.rstrip("\r\n") for game_str in game_strs]
        
        if chunk_size == float('inf'):
            chunk_size = num_games
            
        num_chunks = math.ceil(num_games/chunk_size)
        
        # Add games to database, chunk by chunk
        for i in range(0, len(game_strs), chunk_size):
            print("Chunk " + str(i//chunk_size) + "/" + str(num_chunks))
            some_strs = game_strs[i:i+chunk_size]
            some_codes = game_codes[i:i+chunk_size]
        
            db_ops.add_games_by_str(some_strs, some_codes)
            
        