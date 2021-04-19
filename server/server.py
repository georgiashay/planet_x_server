import http.server
# import http.server, ssl
import re

from .board import *
from .board_type import *
from .game import *
import .db_ops

def retrieve_game(game_code):
    """
    Get a json game from a game code
    """
    game = db_ops.get_game(game_code)
    if game is not None:
        return {
            "gameCode": game_code,
            "game": game.to_json()
        }
    else:
        return {
            "gameCode": None,
            "game": None
        }

def create_game():
    """
    Choose a random game
    """
    game_code, game = db_ops.pick_game()
    return {
        "gameCode": game_code,
        "game": game.to_json()
    }

class PlanetXHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/creategame":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(create_game()).encode("utf8")) 
        elif None != re.search("/joingame/*", self.path):
            game_code = self.path.split("/")[-1]
            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(retrieve_game(game_code)).encode("utf8")) 

server_address = ('0.0.0.0', 8000)
httpd = http.server.HTTPServer(server_address, PlanetXHttpRequestHandler)
# httpd.socket = ssl.wrap_socket(httpd.socket,
#                                server_side=True,
#                                certfile='server.crt',
#                                keyfile='server.key',
#                                ssl_version=ssl.PROTOCOL_TLS)


httpd.serve_forever()