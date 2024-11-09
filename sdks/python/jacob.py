#!/usr/bin/python

import sys
import json
import random
import math

# Python program for A* Search Algorithm
import math
import heapq

if (sys.version_info > (3, 0)):
    print("Python 3.X detected")
    import socketserver as ss
else:
    print("Python 2.X detected")
    import SocketServer as ss


class NetworkHandler(ss.StreamRequestHandler):
    def handle(self):
        game = Game()

        while True:
            data = self.rfile.readline().decode() # reads until '\n' encountered
            json_data = json.loads(str(data))
            # uncomment the following line to see pretty-printed data
            print(json.dumps(json_data, indent=4, sort_keys=True))
            game.gameStart(json_data) # Initialize the game
            response = game.returnResponse(json_data).encode()
            self.wfile.write(response)
            print("test")



class Game:
    def __init__(self):
        self.units = {} # set of unique unit ids
        self.directions = ['N', 'S', 'E', 'W']
        self.game_map = [[]]
        self.map_width = 0
        self.map_height = 0

        # Game Info
        self.game_duration = 0
        self.turn_duration = 0

        # Base coordinates
        self.basex = 0
        self.basey = 0

    def get_random_move(self, json_data):
        units = set([unit['id'] for unit in json_data['unit_updates'] if unit['type'] != 'base'])
        self.units |= units # add any additional ids we encounter

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

            # Get game and turn duration
            self.game_duration = game_info["game_duration"]
            self.turn_duration = game_info["turn_duration"]

            self.updateNewTiles(json_data)
            self.assignUnitIds(json_data)

    # assigns unit ids
    def assignUnitIds(self, json_data):
        units = {}

        for unit in json_data['unit_updates']:
            if unit['type'] != 'base':
                units[unit['id']] = unit
        
        # units = set([unit['id'] for unit in json_data['unit_updates'] if unit['type'] != 'base'])
        self.units |= units # add any additional ids we encounter

    def updateNewTiles(self, json_data):
        for tile in json_data["tile_updates"]:
            # assgin tile in memory map
            if self.game_map[self.basex + tile["x"]][self.basey + tile["y"]] != None:
                self.game_map[self.basex + tile["x"]][self.basey + tile["y"]] |= tile
            else:
                self.game_map[self.basex + tile["x"]][self.basey + tile["y"]] = tile
            

    # need to return dictionary of command {"command": move, "unit": unit, "dir": direction}
    def assignWorkerCommand(self, unit):
        tilesNextToUnit = self.getTilesNextTo(unit["x"], unit["y"])

        for tile in tilesNextToUnit:
            # Check for melee
            if tile["units"] != None:
                return {"command": "MELEE", "unit": unit, "target": tile["units"][0]}
        

        for tile in tilesNextToUnit:
            # Check for gather
            if tile["resources"] != None:
                setDirection = (tile["x"] - unit["x"], tile["y"] - unit["y"])
                if setDirection == (1, 0):
                    direction = 'E'
                if setDirection == (0, 1):
                    direction = 'S'
                if setDirection == (-1, 0):
                    direction = 'W'
                if setDirection == (0, -1):
                    direction = 'N'

                return {"command": "GATHER", "unit": unit["id"], "dir": direction}

        return self.move(unit, [unit["x"] + 1, unit["y" + 1]])
    

    def assignScoutCommand(self, unit):
        command = ''

        return {"command": command, "unit": unit}

    def assignTankCommand(self, unit):
        command = ''

        return {"command": command, "unit": unit}

    def move(self, unit, destination):
        direction = ''

        path = self.a_star_search(self.game_map, [self.units[unit]["x"], self.units[unit]["y"]], destination)

        if path[0] == (1, 0):
            direction = 'N'
        elif path[0] == (0, 1):
            direction = 'E'
        elif path[0] == (-1, 0):
            direction = 'S'
        elif path[0] == (0, -1):
            direction = 'W'

        return {"command": 'MOVE', "unit": unit, "dir": direction}

    def returnResponse(self, json_data):
        self.assignUnitIds(json_data)
        self.updateNewTiles(json_data)
        command = {"commands": []}

        """
        for unit in self.units:
            if unit["type"] == 'worker':
                command["commands"].append(self.assignWorkerCommand(unit))
            elif unit["type"] == 'scout':
                command["commands"].append(self.assignScoutCommand(unit))
            elif unit["type"] == 'tank':
                command["commands"].append(self.assignTankCommand(unit))
        """
        
        for unit in self.units:
            command["commands"].append(self.move(unit, [unit["x"] + 1, unit["y"]]))

        response = json.dumps(command, separators=(',',':')) + '\n'
        return response
    
    def getTilesNextTo(self, xpos, ypos):
        tiles = []

        tiles.append(self.game_map[xpos + 1][ypos])
        tiles.append(self.game_map[xpos - 1][ypos])
        tiles.append(self.game_map[xpos][ypos + 1])
        tiles.append(self.game_map[xpos][ypos - 1])

        return tiles

    # game map is game_map[row][column]
    def constructMemoryMap(self, map_width, map_height):
        game_map = []
        for i in range(map_height * 2 + 1):
            game_map.append([])
            for j in range(map_width * 2 + 1):
                game_map[i].append(None)

        self.game_map = game_map
        self.map_width = map_width * 2 + 1
        self.map_height = map_height * 2 + 1



    """
    A* Pathfinding
    """
    # Check if a cell is valid (within the grid)
    def is_valid(self, row, col):
        return (row >= 0) and (row < self.map_width) and (col >= 0) and (col < self.map_height) and self.game_map[row][col] != None

    # Check if a cell is unblocked
    def is_unblocked(self, grid, row, col):
        return not grid[row][col]["blocked"]

    # Check if a cell is the destination
    def is_destination(self, row, col, dest):
        return row == dest[0] and col == dest[1]

    # Calculate the heuristic value of a cell (Euclidean distance to destination)
    def calculate_h_value(self, row, col, dest):
        return ((row - dest[0]) ** 2 + (col - dest[1]) ** 2) ** 0.5

    # Trace the path from source to destination
    def trace_path(self, cell_details, dest):
        path = []
        row = dest[0]
        col = dest[1]

        # Trace the path from destination to source using parent cells
        while not (cell_details[row][col].parent_i == row and cell_details[row][col].parent_j == col):
            path.append((row, col))
            temp_row = cell_details[row][col].parent_i
            temp_col = cell_details[row][col].parent_j
            row = temp_row
            col = temp_col

        # Add the source cell to the path
        path.append((row, col))
        # Reverse the path to get the path from source to destination
        return path.reverse()

    # Implement the A* search algorithm
    def a_star_search(self, grid, src, dest):
        # Check if the source and destination are valid
        if not self.is_valid(src[0], src[1]) or not self.is_valid(dest[0], dest[1]):
            print("Source or destination is invalid")
            return

        # Check if the source and destination are unblocked
        if not self.is_unblocked(grid, src[0], src[1]) or not self.is_unblocked(grid, dest[0], dest[1]):
            print("Source or the destination is blocked")
            return

        # Check if we are already at the destination
        if self.is_destination(src[0], src[1], dest):
            print("We are already at the destination")
            return

        # Initialize the closed list (visited cells)
        closed_list = [[False for _ in range(self.COL)] for _ in range(self.ROW)]
        # Initialize the details of each cell
        cell_details = [[Cell() for _ in range(self.COL)] for _ in range(self.ROW)]

        # Initialize the start cell details
        i = src[0]
        j = src[1]
        cell_details[i][j].f = 0
        cell_details[i][j].g = 0
        cell_details[i][j].h = 0
        cell_details[i][j].parent_i = i
        cell_details[i][j].parent_j = j

        # Initialize the open list (cells to be visited) with the start cell
        open_list = []
        heapq.heappush(open_list, (0.0, i, j))

        # Initialize the flag for whether destination is found
        found_dest = False

        # Main loop of A* search algorithm
        while len(open_list) > 0:
            # Pop the cell with the smallest f value from the open list
            p = heapq.heappop(open_list)

            # Mark the cell as visited
            i = p[1]
            j = p[2]
            closed_list[i][j] = True

            # For each direction, check the successors
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                        (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dir in directions:
                new_i = i + dir[0]
                new_j = j + dir[1]

                # If the successor is valid, unblocked, and not visited
                if self.is_valid(new_i, new_j) and self.is_unblocked(grid, new_i, new_j) and not closed_list[new_i][new_j]:
                    # If the successor is the destination
                    if self.is_destination(new_i, new_j, dest):
                        # Set the parent of the destination cell
                        cell_details[new_i][new_j].parent_i = i
                        cell_details[new_i][new_j].parent_j = j
                        # Trace the path from source to destination
                        found_dest = True
                        return self.trace_path(cell_details, dest)
                    else:
                        # Calculate the new f, g, and h values
                        g_new = cell_details[i][j].g + 1.0
                        h_new = self.calculate_h_value(new_i, new_j, dest)
                        f_new = g_new + h_new

                        # If the cell is not in the open list or the new f value is smaller
                        if cell_details[new_i][new_j].f == float('inf') or cell_details[new_i][new_j].f > f_new:
                            # Add the cell to the open list
                            heapq.heappush(open_list, (f_new, new_i, new_j))
                            # Update the cell details
                            cell_details[new_i][new_j].f = f_new
                            cell_details[new_i][new_j].g = g_new
                            cell_details[new_i][new_j].h = h_new
                            cell_details[new_i][new_j].parent_i = i
                            cell_details[new_i][new_j].parent_j = j

        # If the destination is not found after visiting all cells
        if not found_dest:
            print("Failed to find the destination cell")



if __name__ == "__main__":
    port = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1]) else 9090
    host = '0.0.0.0'

    print("test2")
    server = ss.TCPServer((host, port), NetworkHandler)
    print("listening on {}:{}".format(host, port))
    server.serve_forever()




    
# Define the Cell class
class Cell:
    def __init__(self):
    # Parent cell's row index
        self.parent_i = 0
    # Parent cell's column index
        self.parent_j = 0
    # Total cost of the cell (g + h)
        self.f = float('inf')
    # Cost from start to this cell
        self.g = float('inf')
    # Heuristic cost from this cell to destination
        self.h = 0