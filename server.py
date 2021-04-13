import http.server
# import http.server, ssl
import re

from board import *
from board_type import *
from game import *
import db_ops

def retrieve_game(game_code):
    game = db_ops.get_game(game_code)
    return {
        "game_code": game_code,
        "game": game.to_json()
    }

def create_game():
    game_code, game = db_ops.pick_game()
    return {
        "game_code": game_code,
        "game": game.to_json()
    }

class PlanetXHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/creategame':
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(json.dumps(create_game()).encode("utf8")) 
        elif None != re.search('/joingame/*', self.path):
            game_code = self.path.split('/')[-1]
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(json.dumps(retrieve_game(game_code)).encode("utf8")) 

server_address = ('localhost', 4443)
httpd = http.server.HTTPServer(server_address, PlanetXHttpRequestHandler)
# httpd.socket = ssl.wrap_socket(httpd.socket,
#                                server_side=True,
#                                certfile='server.crt',
#                                keyfile='server.key',
#                                ssl_version=ssl.PROTOCOL_TLS)


httpd.serve_forever()