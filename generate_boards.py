import sys 

from server.board_type import *
from server.board import *

help_string = "Usage: python generate_boards.py [number of sectors] [core number 0...n-1] [number of cores n] [# boards per chunk] [output file name]"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(help_string)
    elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print(help_string)
    else:
        try:
            num_sectors = int(sys.argv[1])
            board_type = sector_types[num_sectors]
            core_num = int(sys.argv[2])
            num_cores = int(sys.argv[3])
            parallel = (core_num, num_cores)
            chunk_size = int(sys.argv[4])
            filename = sys.argv[5]
            
            board_type.generate_boards_to_file(filename, parallel=parallel, chunk_size=chunk_size)
        except Exception as e:
            print(e)
            print(help_string)

