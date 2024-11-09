#!/usr/bin/python

import sys
import json
import random
import math

if (sys.version_info > (3, 0)):
    print("Python 3.X detected")
    import socketserver as ss
else:
    print("Python 2.X detected")
    import SocketServer as ss


class NetworkHandler(ss.StreamRequestHandler):
    def handle(self):
        game = Game()
        counter = 0
        while counter < 5:
            data = self.rfile.readline().decode() # reads until '\n' encountered
            json_data = json.loads(str(data))
            # uncomment the following line to see pretty-printed data
            print(json.dumps(json_data, indent=4, sort_keys=True))
            
            #Read map
            #Identify resources, enemies, and shortest paths
            # --Create unitarray
            # [{'id': 6, 'player_id': 0, 'x': 1, 'y': 0, 'status': 'moving', 'type': 'worker', 'health': 10, 'can_attack': True, 'range': 2, 'speed': 5, 'resource': 0, 'attack_damage': 2, 'attack_cooldown_duration': 30, 'attack_cooldown': 0, 'attack_type': 'melee'}, {'id': 10, 'player_id': 0, 'x': -1, 'y': -1, 'status': 'moving', 'type': 'worker', 'health': 10, 'can_attack': True, 'range': 2, 'speed': 5, 'resource': 0, 'attack_damage': 2, 'attack_cooldown_duration': 30, 'attack_cooldown': 0, 'attack_type': 'melee'}]
            # game_info = json_data["game_info"]
            
            unit_array = json_data["unit_updates"]
            tiles = json_data["tile_updates"]
            
            counter += 1
            print("1-----------")
            print(unit_array)
            print("2-----------")
            print(tiles)
            print("3-----------")
            # print(game_info["unit_info"])
            
            
            #Looping over unit objects
            # for i in unit_array:
               
           
            
            #Send instructions(The protocol is newline delimited. Make sure your JSON has all but its last newline stripped. The starter kit SDKs should handle this for you.): Move towards resources and away from enemies
            #If enemy encountered attack
            #Bring resources back to base
            #Estimate resource balance-- if money is a lot, employ more wokrers
            
            response = game.get_random_move(unit_array, tiles).encode
            self.wfile.write(response)



class Game:
    def __init__(self):
        self.units = set() # set of unique unit ids
        self.tiles = set()
        self.directions = ['N', 'S', 'E', 'W']

        # Game Info
        self.game_duration = 0
        self.turn_duration = 0
        self.unit_info
        self.game_map = []

        # Base object
        self.base = {}
        
 

    def get_random_move(self, unit_array, tiles_array):
       
        units = set([unit['id'] for unit in unit_array if unit['type'] != 'base'])
        self.units |= units # add any additional ids we encounter
      #   tiles = set([unit['id'] for unit in json_data['unit_updates'] if unit['type'] != 'base'])
           
        
      #   for unit in units:
           

        unit = random.choice(tuple(self.units))
        direction = random.choice(self.directions)
        move = 'MOVE'
        command = {"commands": [{"command": move, "unit": unit, "dir": direction}]}
        response = json.dumps(command, separators=(',',':')) + '\n'
        return response
     
    def gameStart(self, json_data):
        if (json_data["turn"] == 0):
            # create memory map
            self.constructMemoryMap(json_data["map_width"], json_data["map_height"])
            
            # set base x and y coordinates
            self.basex = math.floor(json_data["map_width"]/2)
            self.basey = math.floor(json_data["map_height"]/2)

            
            
            
    # game map is game_map[row][column]
    def constructMemoryMap(self, map_width, map_height):
        game_map = []
        for i in range(map_height * 2 + 1):
            game_map.append([])
            for j in range(map_width * 2 + 1):
                game_map[i].append([])

        self.game_map = game_map
        
   
  

if __name__ == "__main__":
    port = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1]) else 9090
    host = '0.0.0.0'

    server = ss.TCPServer((host, port), NetworkHandler)
    print("listening on {}:{}".format(host, port))
    server.serve_forever()


#  {'unit_updates': [{'id': 8, 'player_id': 0, 'x': -1, 'y': -6, 'status': 'moving', 'type': 'worker', 'health': 10, 'can_attack': True, 'range': 2, 'speed': 5, 'resource': 0, 'attack_damage': 2, 'attack_cooldown_duration': 30, 'attack_cooldown': 0, 'attack_type': 'melee'}, {'id': 11, 'player_id': 0, 'x': 4, 'y': 3, 'status': 'moving', 'type': 'worker', 'health': 10, 'can_attack': True, 'range': 2, 'speed': 5, 'resource': 0, 'attack_damage': 2, 'attack_cooldown_duration': 30, 'attack_cooldown': 0, 'attack_type': 'melee'}], 'tile_updates': [], 'player': 0, 'turn': 374, 'time': 225020}