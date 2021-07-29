import argparse

from planetx_game.game import *

parser = argparse.ArgumentParser(description="Reencode a set of games.")
parser.add_argument("-i", "--input", type=str, help="The input file containing one game per line", required=True)
parser.add_argument("-o", "--out", type=str, help="The output filename", required=True)

if __name__ == "__main__":
    args = parser.parse_args(sys.argv[1:])    
    
    input_file = open(args.input, "r")
    output_file = open(args.out, "w")

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
