from game import *

twelve_board_constraints = [CometConstraint(12), AsteroidConstraint(), PlanetXConstraint(), GasCloudConstraint() ]
eighteen_board_constraints = [CometConstraint(18), AsteroidConstraint(), DwarfPlanetConstraint(6), \
                              PlanetXConstraint(), GasCloudConstraint() ]
twentyfour_board_constraints = [ CometConstraint(24), AsteroidConstraint(), DwarfPlanetConstraint(6), \
                                BlackHoleConstraint(), PlanetXConstraint(), GasCloudConstraint() ]

twelve_board_numbers = {
    SpaceObject.PlanetX: 1,
    SpaceObject.Empty: 2,
    SpaceObject.GasCloud: 2,
    SpaceObject.DwarfPlanet: 1,
    SpaceObject.Asteroid: 4,
    SpaceObject.Comet: 2
}

eighteen_board_numbers = {
    SpaceObject.PlanetX: 1,
    SpaceObject.Empty: 5,
    SpaceObject.GasCloud: 2,
    SpaceObject.DwarfPlanet: 4,
    SpaceObject.Asteroid: 4,
    SpaceObject.Comet: 2
}

twentyfour_board_numbers = {
    SpaceObject.PlanetX: 1,
    SpaceObject.Empty: 6,
    SpaceObject.GasCloud: 3,
    SpaceObject.DwarfPlanet: 4,
    SpaceObject.Asteroid: 6,
    SpaceObject.Comet: 3,
    SpaceObject.BlackHole: 1
}

twelve_type = BoardType(twelve_board_constraints, twelve_board_numbers, 6, 1)
eighteen_type = BoardType(eighteen_board_constraints, eighteen_board_numbers, 6, 2)
twentyfour_type = BoardType(twentyfour_board_constraints, twentyfour_board_numbers, 7, 3)

sector_types = {
    12: twelve_type,
    18: eighteen_type,
    24: twentyfour_type
}

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

