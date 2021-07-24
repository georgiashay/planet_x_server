from planetx_game.game import *

help_string = "Usage: python reencode.py [input game file] [output game file]"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(help_string)
    elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print(help_string)
    else:
        try:
            input_filename = sys.argv[1]
            output_filename = sys.argv[2]
        except Exception as e:
            print(e)
            print(help_string)
        else:
            input_file = open(input_filename, "r")
            output_file = open(output_filename, "w")
            
            more_games = True
            current_game = 0
            
            while more_games:
                current_game += 1
                print("Reencoding game " + str(current_game))
                game_str = input_file.readline().rstrip("\r\n")
                if len(game_str) == 0:
                    more_games = False
                    break
                else:
                    game = Game.parse(game_str)
                    output_file.write(game.code() + "\n")
                    
            input_file.close()
            output_file.close()
