from game_generator import GameGenerator
from board_type import sector_types

help_string = "Usage: python generate_games.py [number of sectors] [input file name ] [output file name] [# boards per chunk]"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(help_string)
    elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print(help_string)
    else:
        try:
            num_sectors = int(sys.argv[1])
            board_type = sector_types[num_sectors]
            input_filename = sys.argv[2]
            output_filename = sys.argv[3]
            chunk_size = int(sys.argv[4])
            
            GameGenerator.generate_games(board_type, input_filename, output_filename, chunk_size=chunk_size)
        except Exception as e:
            print(e)
            print(help_string)

