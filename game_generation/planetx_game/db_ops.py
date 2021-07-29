import json
import os

import mysql.connector
import mysql.connector.pooling

from .board import *
from .board_type import * 
from .game import *
from .session import *

dirname = os.path.dirname(__file__)
credsfile = os.path.join(dirname, "creds.json")

with open(credsfile, "r") as f:
    creds = json.load(f)
    
dbconfig = {
    "password": creds["password"],
    "database": creds["database"],
    "user": creds["username"],
    "host": creds["hostname"]
}

cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name = "mypool", pool_size = 3, **dbconfig)

def get_connection():
    """
    Gets a mysql database connection to perform operations with
    """
    return cnxpool.get_connection()

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


def query(query):
    cxn = get_connection()
    cursor = cxn.cursor()
     
    cursor.execute(query)  
    
    rows = cursor.fetchall()
    
    cursor.close()
    cxn.close()
    
    return rows
    
def pick_game(num_sectors):
    """
    Pick a random game from the database
    
    Returns a tuple of the game code and the Game itself
    """
    cxn = get_connection()
    cursor = cxn.cursor()

    cursor.execute("SET @maxID := (SELECT MAX(id) FROM games WHERE board_size = %s);", (num_sectors,))
    cursor.execute("SET @minID := (SELECT MIN(id) FROM games WHERE board_size = %s);", (num_sectors,))
    
    # Select a random id and get the game for that id
    random_game_query = ("SELECT * "
                             "FROM games AS r1 JOIN "
                                 "(SELECT CEIL(RAND() * "
                                     "(@maxID - @minID) + @minID)  AS id) "
                                 "AS r2 "
                             "WHERE r1.id >= r2.id AND board_size = %s "
                             "ORDER BY r1.id ASC "
                             "LIMIT 1;")
    
    cursor.execute(random_game_query, (num_sectors,))    
    
    gid, game_code, board_size, board_objects, research, conference, starting_information, _ = cursor.fetchone()
    game = Game(Board.parse(board_objects), StartingInformation.parse(starting_information), 
                Research.parse(research), Conference.parse(conference))
    
    cursor.close()
    cxn.close()
 
    return gid, game_code, game

def get_game_by_id(gid):
    """
    Gets the game for a given id
    """
    cxn = get_connection()
    cursor = cxn.cursor()

                      
    game_query = ("SELECT * from games " 
                 "WHERE id = %s")
    
    cursor.execute(game_query, (gid,))
    
    result = cursor.fetchone()
    
    if result is None:
        return None
    
    gid, game_code, board_size, board_objects, research, conference, starting_information = result
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
 
    return gid, game

def get_game_codes():
    """
    Returns a list of all game codes that currently exist
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    game_code_query = "SELECT game_code FROM games"
    
    cursor.execute(game_code_query)    
    
    game_codes = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    cxn.close()
    
    return game_codes

def get_session_codes():
    """
    Returns a list of all session codes that currently exist
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    session_code_query = "SELECT session_code FROM sessions"
    
    cursor.execute(session_code_query)
    
    session_codes = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    cxn.close()
    
    return session_codes

def create_session(session_code, num_sectors, gid):
    """
    Creates a session with a particular session code and game id
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    session_query = "INSERT INTO sessions (session_code, game_size, game_id) VALUES (%s, %s, %s);"
    
    cursor.execute(session_query, (session_code, num_sectors, gid))
    cxn.commit()
    
    session_id = cursor.lastrowid

    cursor.close()
    cxn.close()
    
    return session_id

def get_session_by_code(session_code):
    """
    Gets the session with a given session code
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    session_query = "SELECT * FROM sessions WHERE session_code = %s"
    
    cursor.execute(session_query, (session_code,))
    
    session_id, session_code, game_size, game_id, first_rot, \
    current_sector, action_type, action_player = cursor.fetchone()
    
    cursor.close()
    cxn.close()
    
    return session_id, session_code, game_size, game_id, bool(first_rot), current_sector, action_type, action_player

def get_session_by_id(session_id):
    """
    Gets the session with a given session code
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    session_query = "SELECT * FROM sessions WHERE id = %s"
    
    cursor.execute(session_query, (session_id,))
    
    session_id, session_code, game_size, game_id, first_rot, \
    current_sector, action_type, action_player = cursor.fetchone()
    
    cursor.close()
    cxn.close()
    
    return session_id, session_code, game_size, game_id, bool(first_rot), current_sector, action_type, action_player

def get_theories_for_session(session_id):
    """
    Gets the theories for a session with a particular session ID
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    theory_query = "SELECT * FROM theories WHERE session_id = %s"
    
    cursor.execute(theory_query, (session_id,))
    
    rows = cursor.fetchall()
    theories = [Theory(SpaceObject.parse(row[3]), row[4], row[2], row[5]) for row in rows]
    
    cursor.close()
    cxn.close()
    
    return theories

def get_theories_for_player_session(player_id):
    """
    Gets the theories for a player's session given the player's ID
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    session_query = "SELECT session_id FROM players where id = %s"
    cursor.execute(session_query, (player_id,))
    
    session_id = cursor.fetchone()[0]
    
    theory_query = "SELECT object, sector, player_id, progress FROM theories WHERE session_id = %s;"

    cursor.execute(theory_query, (session_id,))
    
    rows = cursor.fetchall()
    theories = [Theory(SpaceObject.parse(row[0]), row[1], row[2], row[3]) for row in rows]
    
    cursor.close()
    cxn.close()
    
    return session_id, theories
    
    
def get_players_for_session(session_id):
    """
    Gets the players for a session with a particular session ID
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    player_query = "SELECT * FROM players WHERE session_id = %s"
    
    cursor.execute(player_query, (session_id,))
    
    rows = cursor.fetchall()
    players = [Player(row[0], row[2], row[3], row[4], row[5]) for row in rows]
    
    cursor.close()
    cxn.close()
    
    return players

def get_players_for_session_code(session_code):
    """
    Gets the players for a session with a particular session ID
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    player_query = ("SELECT sessions.id, players.id, players.num, players.name, players.sector, players.arrival "
                    "FROM players, sessions WHERE players.session_id = sessions.id AND sessions.session_code = %s")
    
    cursor.execute(player_query, (session_code,))
    
    rows = cursor.fetchall()
    players = [Player(row[1], row[2], row[3], row[4], row[5]) for row in rows]
    
    cursor.close()
    cxn.close()
    
    return rows[0][0], players
    
def new_player(session_code, name, creator):
    """
    Creates a new player for a session with a particular code
    """
    cxn = get_connection()
    cursor = cxn.cursor()

    new_player_query = "CALL NewPlayer(%s, %s, @SessionID, @PlayerNum, @PlayerID)"
    cursor.execute(new_player_query, (session_code, name,))
    cursor.execute("SELECT @SessionID, @PlayerNum, @PlayerID")
    
    session_id, player_num, player_id = cursor.fetchone()
    
    if creator:
        action_query = "INSERT INTO actions(action_type, player_id, resolved) VALUES('START_GAME', %s, FALSE);"
        cursor.execute(action_query, (player_id,))
    
    cxn.commit()
    
    cursor.close()
    cxn.close()
    
    return session_id, player_num, player_id
    
def move_player(player_id, sector, arrival):
    """
    Moves player with id player_id to sector sector in arrival order arrival
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    player_query = "UPDATE players SET sector = %s, arrival = %s WHERE id = %s;"
    
    cursor.execute(player_query, (sector, arrival, player_id))
    cxn.commit()
    
    cursor.close()
    cxn.close()   
    
def create_theory(session_id, player_id, space_object, sector):
    """
    Creates a new theory
    """
    cxn = get_connection()
    cursor = cxn.cursor()

    theory_query = "INSERT INTO theories (session_id, player_id, object, sector, progress) VALUES (%s, %s, %s, %s, %s);"
    cursor.execute(theory_query, (session_id, player_id, space_object, sector, 0))
    
    cxn.commit()
    
    cursor.close()
    cxn.close()
    
def advance_theories(session_id):
    """
    Advances all theories for a particular session
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    theory_query = "UPDATE theories SET progress = progress + 1 WHERE progress < 4 AND session_id = %s;"
    cursor.execute(theory_query, (session_id,))
    
    cxn.commit()
    
    cursor.close()
    cxn.close()
    
def advance_player(player_id, sectors):
    """
    Advance a player sectors sectors
    """
    cxn = get_connection()
    cursor = cxn.cursor()

    new_player_query = "CALL MovePlayer(%s, %s)"
    cursor.execute(new_player_query, (player_id, sectors))
        
    cxn.commit()
    
    cursor.close()
    cxn.close()
    
def get_current_actions_for_session(session_id):
    """
    Gets a list of pending actions for a session
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    action_query = ("SELECT actions.id, actions.action_type, actions.player_id FROM actions, players "
                    "WHERE actions.resolved IS FALSE AND actions.player_id = players.id "
                    "AND players.session_id = %s")
    
    cursor.execute(action_query, (session_id,))
    
    rows = cursor.fetchall()
    actions = [Action(ActionType[row[1]], row[2], action_id=row[0]) for row in rows]
    
    cursor.close()
    cxn.close()
    
    return actions

def get_previous_turns(session_id):
    """
    Gets a list of previous turns for a session
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    turn_query = ("SELECT actions.player_id, actions.resolve_time, actions.resolve_action FROM actions, players "
                  "WHERE actions.resolved IS TRUE AND actions.action_type = 'PLAYER_TURN' "
                  "AND actions.player_id = players.id AND players.session_id = %s")
    
    cursor.execute(turn_query, (session_id,))
    
    rows = cursor.fetchall()
    turns = [Turn.parse(row[0], row[1], row[2]) for row in rows]
    
    cursor.close()
    cxn.close()
    
    return turns
    
def create_action(action_type, player_id):
    """
    Create action of type action_type for player with id player_id
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    action_query = "INSERT INTO actions(action_type, player_id, resolved) VALUES(%s, %s, %s);"
    cursor.execute(action_query, (action_type.name, player_id, False))
    
    cxn.commit()
    
    cursor.close()
    cxn.close()
    
def get_current_action(player_id):
    """
    Get the current action for a certain player, or None if there is none
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    action_query = "SELECT id, action_type, player_id FROM actions WHERE player_id = %s AND resolved IS FALSE"
    cursor.execute(action_query, (player_id,))
    
    row = cursor.fetchone()
    
    cursor.close()
    cxn.close()
    
    if row is None:
        return None
    else:
        return Action(ActionType[row[1]], row[2], action_id=row[0])
    
def resolve_action(action_id, turn):
    """
    Resolves action with a given id. Does nothing if action_id is None.
    """
    if action_id is None:
        return
    
    cxn = get_connection()
    cursor = cxn.cursor()
    
    if turn is None:
        turn_time = datetime.now()
        turn_code = ""
    else:
        turn_time = turn.turn_time
        turn_code = turn.code()
    
    action_query = "UPDATE actions SET resolved = TRUE, resolve_time = %s, resolve_action = %s WHERE id = %s;"
    cursor.execute(action_query, (turn_time, turn_code, action_id,))
    cxn.commit()
    
    cursor.close()
    cxn.close()
    
def set_current_action(session_id, action):
    """
    Sets the current action for a session
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    action_query = "UPDATE sessions SET current_action = %s, action_player = %s WHERE id = %s;"
    cursor.execute(action_query, (action.action_type.name, action.player_id, session_id,))
    cxn.commit()
    
    cursor.close()
    cxn.close()
    
def set_current_status(session_id, action, current_sector, first_rot):
    """
    Sets the current action for a session
    """
    cxn = get_connection()
    cursor = cxn.cursor()
    
    action_query = ("UPDATE sessions SET first_rotation = %s, current_sector = %s, "
                    "current_action = %s, action_player = %s WHERE id = %s;")
    
    cursor.execute(action_query, (first_rot, current_sector, action.action_type.name, action.player_id, session_id,))
    cxn.commit()
    
    cursor.close()
    cxn.close()
    