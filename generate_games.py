import sys
import argparse

from game_generator import GameGenerator
from planetx_game.board_type import sector_types

parser = argparse.ArgumentParser(description="Generate Planet X games given a set of boards.")
parser.add_argument("sectors", type=int, help="The number of sectors on the boards")
parser.add_argument("-i", "--input", type=str, help="The input file containing one board per line", required=True)
parser.add_argument("-c", "--chunk-size", default=float('inf'), type=int, help="The number of boards to load into memory at one time", required=False)
parser.add_argument("-o", "--out", type=str, help="The output filename", required=True)

if __name__ == "__main__":
    args = parser.parse_args(sys.argv[1:])    
    try:
        GameGenerator.generate_games(sector_types[args.sectors], args.input, args.out, chunk_size=args.chunk_size)
    except Exception as e:
        print(e)


