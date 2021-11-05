from lib.block_walkable import get_block_walkable


class Node:
    def __init__(self, x, y, z, g, parent):
        self.x = x
        self.y = y
        self.z = z
        self.g = g
        self.h = 0
        self.parent = parent
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z
    
    def get_neighbors(self):
        neighbors = []
        for offsets in [
            { "x": -1, "y": 0, "z": 0 },
            { "x": 1, "y": 0, "z": 0 },
            { "x": 0, "y": -1, "z": 0 },
            { "x": 0, "y": 1, "z": 0 },
            { "x": 0, "y": 0, "z": -1 },
            { "x": 0, "y": 0, "z": 1 },
        ]:
            if get_block_walkable(self.x + offsets["x"], self.y + offsets["y"], self.z + offsets["z"]):
                neighbors.append(Node(self.x + offsets["x"], self.y + offsets["y"], self.z + offsets["z"], self.g + 1, self))
        return neighbors
    
    def get_path(self):
        path = []
        current = self
        while current is not None:
            path.append(f"{current.x},{current.y},{current.z}")
            current = current.parent
        return ';'.join(path)
    
    def calculate_h(self, goal):
        self.h = abs(self.x - goal.x) + abs(self.y - goal.y) + abs(self.z - goal.z)
"""
    A function that uses A* to find the shortest path between two points.
"""
def pathfind(cx, cy, cz, tx, ty, tz):
    start = Node(cx, cy, cz, 0, None)
    end = Node(tx, ty, tz, 0, None)
    open_list = [start]
    closed_list = []
    while len(open_list) > 0:
        current = open_list[0]
        for node in open_list:
            if node.g + node.h < current.g + current.h:
                current = node
        open_list.remove(current)
        closed_list.append(current)
        if current == end:
            return current.get_path()
        for neighbor in current.get_neighbors():
            if neighbor in closed_list:
                continue
            neighbor.g = current.g + 1
            neighbor.calculate_h(end)
            if neighbor not in open_list:
                open_list.append(neighbor)