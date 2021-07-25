import sys 
import argparse

from planetx_game.board_type import *
from planetx_game.board import *

parser = argparse.ArgumentParser(description="Generate Planet X boards of a specific size.")
parser.add_argument("sectors", type=int, help="The number of sectors on the boards to generate")
parser.add_argument("-p", "--parallel", nargs=2, type=int, default=(0, 1), help="The core number followed by the total number of cores (default: 0 1)", required=False)
parser.add_argument("-c", "--chunk-size", default=float('inf'), type=int, help="The number of boards to load into memory at one time", required=False)
parser.add_argument("-o", "--out", type=str, help="The output filename", required=True)

if __name__ == "__main__":
    args = parser.parse_args(sys.argv[1:])
    try:
        board_type = sector_types[args.sectors]
        board_type.generate_boards_to_file(args.out, parallel=args.parallel, chunk_size=args.chunk_size)
    except Exception as e:
        print(e)

