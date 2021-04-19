from game_generator import GameGenerator

help_string = "Usage: python upload_games.py [input file name ] [# boards per chunk]"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(help_string)
    elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print(help_string)
    else:
        try:
            input_filename = sys.argv[1]
            chunk_size = int(sys.argv[2])
            
            GameGenerator.add_to_database(input_filename, chunk_size=chunk_size)
        except Exception as e:
            print(e)
            print(help_string)