import sys
import argparse

from game_generator import GameGenerator

parser = argparse.ArgumentParser(description="Uploadd Planet X games to the database.")
parser.add_argument("-i", "--input", type=str, help="The input file containing one board per line", required=True)
parser.add_argument("-l", "--code-length", type=int, help="The length of the game codes", required=True)
parser.add_argument("-c", "--chunk-size", default=float('inf'), type=int, help="The number of boards to upload at one time", required=False)

if __name__ == "__main__":
    args = parser.parse_args(sys.argv[1:])    
    print(args)
    
    try:
        GameGenerator.add_to_database(args.input, args.code_length, chunk_size=args.chunk_size)
    except Exception as e:
        print(e)