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
    main_unit = None
    main_tiles = None
    
    def handle(self):
        
        
        game = Game()
        counter = 0
        
        while True:
            
            data = self.rfile.readline().decode() # reads until '\n' encountered
            json_data = json.loads(str(data))
            unit_array = json_data["unit_updates"]
            tiles = json_data["tile_updates"]
            if not self.main_unit:
                self.main_unit = unit_array
                self.main_tiles = tiles
            game.gameStart(json_data)
            
            
          
            
            
           
            
           
            

            # uncomment the following line to see pretty-printed data
            # print(json.dumps(json_data, indent=4, sort_keys=True))
            response = game.get_random_move(unit_array, tiles, self.main_unit, self.main_tiles).encode()
            self.wfile.write(response)



    
class Game:
    
    
    def __init__(self):
        self.units = set() # set of unique unit ids
        self.directions = ['N', 'S', 'E', 'W']
        self.counter = 0
        self.basex = 0
        self.basey = 0
        self.game_map = 0

    def get_random_move(self, unit_array, tiles, main_units, main_tiles):
        units = set([unit["id"] for unit in unit_array if unit['type'] != 'base'])
        self.units |= units # add any additional ids we encounter
        
        for value in main_units:
            for val in unit_array:
                if value["id"] == val["id"]:  
                    value["id"] = val
                    value["x"] = self.basex + value["x"]
                    value["y"] = self.basey + value["x"]
        for val in main_tiles:
            self.game_map[self.basex + val["x"]][self.basey + val["y"]] = val
            
                    
        
        
                    
            
                    
                    
                    
        unit = random.choice(tuple(self.units))
        direction = random.choice(self.directions)
        move = 'MOVE'
        command = {"commands": [{"command": move, "unit": unit, "dir": direction}]}
        response = json.dumps(command, separators=(',',':')) + '\n'
        return response
        
                
            
    def gameStart(self, json_data):
        if (json_data["turn"] == 0):
            game_info = json_data["game_info"]
            # create memory map
            self.constructMemoryMap(game_info["map_width"], game_info["map_height"])
            
            # set base x and y coordinates
            self.basex = math.floor(game_info["map_width"]/2)
            self.basey = math.floor(game_info["map_height"]/2)

            

            # self.updateNewTiles(json_data)

            
    # game map is game_map[row][column]
    def constructMemoryMap(self, map_width, map_height):
        game_map = []
        for i in range(map_height * 2 + 1):
            game_map.append([])
            for j in range(map_width * 2 + 1):
                game_map[i].append([])

        self.game_map = game_map
        
        
        
    # def updateNewTiles(self, json_data):
    #     for tile in json_data["tile_updates"]:
    #         # assgin tile in memory map
    #         if self.game_map[self.basex + tile["x"]][self.basey + tile["y"]] != None:
    #             self.game_map[self.basex + tile["x"]][self.basey + tile["y"]] |= tile
    #         else:
    #             self.game_map[self.basex + tile["x"]][self.basey + tile["y"]] = tile
  
    
    
    

if __name__ == "__main__":
    port = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1]) else 9090
    host = '0.0.0.0'
    # myNet = NetworkHandler()

    server = ss.TCPServer((host, port), NetworkHandler)
    print("listening on {}:{}".format(host, port))
    server.serve_forever()

#  {'unit_updates': [{'id': 8, 'player_id': 0, 'x': -1, 'y': -6, 'status': 'moving', 'type': 'worker', 'health': 10, 'can_attack': True, 'range': 2, 'speed': 5, 'resource': 0, 'attack_damage': 2, 'attack_cooldown_duration': 30, 'attack_cooldown': 0, 'attack_type': 'melee'}, {'id': 11, 'player_id': 0, 'x': 4, 'y': 3, 'status': 'moving', 'type': 'worker', 'health': 10, 'can_attack': True, 'range': 2, 'speed': 5, 'resource': 0, 'attack_damage': 2, 'attack_cooldown_duration': 30, 'attack_cooldown': 0, 'attack_type': 'melee'}], 'tile_updates': [], 'player': 0, 'turn': 374, 'time': 225020}


# [{'visible': True, 'x': -2, 'y': -2, 'blocked': True, 'resources': None, 'units': []}, {'visible': True, 'x': -2, 'y': -1, 'blocked': True, 'resources': None, 'units': []}, {'visible': True, 'x': -2, 'y': 0, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': -2, 'y': 1, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': -2, 'y': 2, 'blocked': True, 'resources': None, 'units': []}, {'visible': True, 'x': -1, 'y': -2, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': -1, 'y': -1, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': -1, 'y': 0, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': -1, 'y': 1, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': -1, 'y': 2, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': 0, 'y': -2, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': 0, 'y': -1, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': 0, 'y': 0, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': 0, 'y': 1, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': 0, 'y': 2, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': 1, 'y': -2, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': 1, 'y': -1, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': 1, 'y': 0, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': 1, 'y': 1, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': 1, 'y': 2, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': 2, 'y': -2, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': 2, 'y': -1, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': 2, 'y': 0, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': 2, 'y': 1, 'blocked': False, 'resources': None, 'units': []}, {'visible': True, 'x': 2, 'y': 2, 'blocked': False, 'resources': None, 'units': []}]