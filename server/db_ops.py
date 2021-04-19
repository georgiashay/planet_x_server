import json
import os

import mysql.connector

from .board import *
from .board_type import * 
from .game import *

dirname = os.path.dirname(__file__)
credsfile = os.path.join(dirname, "creds.json")

with open(credsfile, "r") as f:
    creds = json.load(f)

def get_connection():
    """
    Gets a mysql database connection to perform operations with
    """
    cxn = mysql.connector.connect(user=creds["username"], password=creds["password"],
                                 host=creds["hostname"], database=creds["database"])
    return cxn

def add_game(game, game_code):
    """
    Adds a game to the database
    
    game: The Game to add
    game_code: The string game code for the game
    """
    # Extract parameters of the board and encode them
    board_size = len(game.board)
    board_objects = str(game.board)
    research = game.research.code()
    conference = game.conference.code()
    starting_information = game.starting_info.code()
    
    # Perform mysql command to insert it into the database
    cxn = get_connection()
    cursor = cxn.cursor()
    
    add_game_query = ("INSERT INTO games "
                       "(game_code, board_size, board_objects, research, conference, starting_information) "
                       "VALUES (%s, %s, %s, %s, %s, %s);")
    game_data = (game_code, board_size, board_objects, research, conference, starting_information)
    
    cursor.execute(add_game_query, game_data)
    cxn.commit()
    
    cursor.close()
    cxn.close()
    
def clear_games():
    """
    Remove all games from the database
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    cursor.execute("TRUNCATE TABLE games")
    cxn.commit()
    
    cursor.close()
    cxn.close()
    
def add_games(games, game_codes):
    """
    Add a set of games to the database
    """
    values = []
    
    # Collect the parameters of each game for the mysql columns
    for game_code, game in zip(game_codes, games):
        board_size = len(game.board)
        board_objects = str(game.board)
        research = game.research.code()
        conference = game.conference.code()
        starting_information = game.starting_info.code()
        
        values.append((game_code, board_size, board_objects, research, conference, starting_information))
    
    # Insert all games into the database
    add_game_query = ("INSERT INTO games "
                       "(game_code, board_size, board_objects, research, conference, starting_information) "
                       "VALUES (%s, %s, %s, %s, %s, %s);")
        
    cxn = get_connection()
    cursor = cxn.cursor()
    
    cursor.executemany(add_game_query, values)
    cxn.commit()
    
    cursor.close()
    cxn.close()
    
def add_games_by_str(games, game_codes):
    """
    Add games to the database by their encoded strings
    
    games: A list of encoded game strings
    game_codes: A list of game codes for the games
    """
    values = []
    
    # Split the game into parameters by splitting encoded string on & symbol
    for game_code, game_str in zip(game_codes, games):
        components = game_str.split("&")
        values.append((game_code, int(components[0]), components[1], components[2], components[3], components[4]))
    
    # Insert all the games into the database
    add_game_query = ("INSERT INTO games "
                       "(game_code, board_size, board_objects, research, conference, starting_information) "
                       "VALUES (%s, %s, %s, %s, %s, %s);")
        
    cxn = get_connection()
    cursor = cxn.cursor()
    
    cursor.executemany(add_game_query, values)
    cxn.commit()
    
    cursor.close()
    cxn.close()

def pick_game():
    """
    Pick a random game from the database
    
    Returns a tuple of the game code and the Game itself
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
        
#     random_game_query = ("SELECT * "
#                           "FROM games JOIN "
#                               "(SELECT CEIL(RAND() * "
#                                   "(SELECT MAX(id) "
#                                       "FROM games)) AS id"
#                                   ") AS r2 "
#                                   "USING (id);")
    
    # Select a random id and get the game for that id
    random_game_query = ("SELECT * "
                             "FROM games AS r1 JOIN "
                                 "(SELECT CEIL(RAND() * "
                                     "(SELECT MAX(id) "
                                         "FROM games)) AS id) "
                                 "AS r2 "
                             "WHERE r1.id >= r2.id "
                             "ORDER BY r1.id ASC "
                             "LIMIT 1;")
    
    cursor.execute(random_game_query)    
    
    gid, game_code, board_size, board_objects, research, conference, starting_information, _ = cursor.fetchone()
    game = Game(Board.parse(board_objects), StartingInformation.parse(starting_information), 
                Research.parse(research), Conference.parse(conference))
    
    cursor.close()
    cxn.close()
 
    return game_code, game

def get_game(game_code):
    """
    Gets the game for a given game code game_code.
    """
    cxn = get_connection()
    cursor = cxn.cursor()

                      
    game_query = ("SELECT * from games " 
                 "WHERE game_code = %s")
    
    cursor.execute(game_query, (game_code,))
    
    result = cursor.fetchone()
    
    if result is None:
        return None
    
    gid, game_code, board_size, board_objects, research, conference, starting_information = result
    game = Game(Board.parse(board_objects), StartingInformation.parse(starting_information), 
                Research.parse(research), Conference.parse(conference))
    
    cursor.close()
    cxn.close()
 
    return game