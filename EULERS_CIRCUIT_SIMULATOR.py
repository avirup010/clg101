import raylibpy as rl
import math
from collections import deque

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
MAX_NODES = 10
NODE_RADIUS = 25
EDGE_THICKNESS = 2
HOVER_THICKNESS = 3

# Colors
BACKGROUND_COLOR = (22, 22, 29, 255)  # Dark blue-gray
NODE_COLOR = (45, 112, 193, 255)  # Steel blue
NODE_HOVER_COLOR = (64, 159, 255, 255)  # Bright blue
NODE_SELECTED_COLOR = (76, 175, 80, 255)  # Green
EDGE_COLOR = (149, 157, 165, 255)  # Light gray
PATH_COLOR = (255, 85, 85, 255)  # Coral red
TEXT_COLOR = (236, 239, 244, 255)  # Off-white
HINT_COLOR = (149, 157, 165, 128)  # Semi-transparent gray

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hover = False

class Edge:
    def __init__(self, u, v):
        self.u = u
        self.v = v

class EulerPathFinder:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.adj = [[0] * MAX_NODES for _ in range(MAX_NODES)]
        self.selected_node = None
        self.highlighted_path = []
        self.hover_node = None
        self.status = ""
        self.show_hint = True
        
    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def add_node(self, x, y):
        if len(self.nodes) < MAX_NODES:
            self.nodes.append(Node(x, y))
            self.show_hint = False

    def delete_node(self, index):
        # Remove the node
        self.nodes.pop(index)
        
        # Remove all edges connected to this node
        self.edges = [edge for edge in self.edges 
                     if edge.u != index and edge.v != index]
        
        # Update edge indices for nodes after the deleted node
        for edge in self.edges:
            if edge.u > index:
                edge.u -= 1
            if edge.v > index:
                edge.v -= 1
        
        # Update adjacency matrix
        self.adj = [[0] * MAX_NODES for _ in range(MAX_NODES)]
        for edge in self.edges:
            self.adj[edge.u][edge.v] = self.adj[edge.v][edge.u] = 1
        
        # Reset selection and path
        self.selected_node = None
        self.highlighted_path = []
        
        # Update status
        if self.edges:
            self.check_eulerian()
        else:
            self.status = ""

    def add_edge(self, u, v):
        if u != v and u < len(self.nodes) and v < len(self.nodes) and self.adj[u][v] == 0:
            self.edges.append(Edge(u, v))
            self.adj[u][v] = self.adj[v][u] = 1

    def check_eulerian(self):
        odd_degree_nodes = [i for i in range(len(self.nodes)) if sum(self.adj[i]) % 2 == 1]
        if len(odd_degree_nodes) == 0:
            self.highlighted_path = self.find_eulerian_path(0)
            self.status = "Euler Circuit Found!"
        elif len(odd_degree_nodes) == 2:
            self.highlighted_path = self.find_eulerian_path(odd_degree_nodes[0])
            self.status = "Euler Path Found!"
        else:
            self.highlighted_path = []
            self.status = "No Euler Path/Circuit Exists"

    def find_eulerian_path(self, start):
        temp_adj = [row[:] for row in self.adj]
        path = []
        stack = [start]
        
        while stack:
            u = stack[-1]
            found = False
            for v in range(len(self.nodes)):
                if temp_adj[u][v] > 0:
                    stack.append(v)
                    temp_adj[u][v] -= 1
                    temp_adj[v][u] -= 1
                    found = True
                    break
            if not found:
                path.append(stack.pop())
        
        return path[::-1]

    def draw_edge(self, start, end, color, thickness):
        rl.draw_line_ex(
            rl.Vector2(start.x, start.y),
            rl.Vector2(end.x, end.y),
            thickness,
            color
        )

    def draw_node(self, node, index, color):
        # Draw node shadow
        rl.draw_circle(
            int(node.x), 
            int(node.y + 2), 
            NODE_RADIUS, 
            (0, 0, 0, 64)
        )
        
        # Draw main node circle
        rl.draw_circle(int(node.x), int(node.y), NODE_RADIUS, color)
        
        # Draw node border
        rl.draw_circle_lines(int(node.x), int(node.y), NODE_RADIUS, TEXT_COLOR)
        
        # Draw node index
        text = str(index)
        font_size = 20
        text_width = rl.measure_text(text, font_size)
        rl.draw_text(
            text,
            int(node.x - text_width/2),
            int(node.y - font_size/2),
            font_size,
            TEXT_COLOR
        )

    def draw(self):
        rl.clear_background(BACKGROUND_COLOR)
        
        # Draw controls help
        controls_text = "Left click: Add nodes and create edges | Right click: Delete nodes"
        font_size = 20
        text_width = rl.measure_text(controls_text, font_size)
        rl.draw_text(
            controls_text,
            SCREEN_WIDTH - text_width - 20,
            SCREEN_HEIGHT - font_size - 20,
            font_size,
            HINT_COLOR
        )
        
        # Draw hint text if needed
        if self.show_hint:
            hint_text = "Click anywhere to add nodes"
            font_size = 24
            text_width = rl.measure_text(hint_text, font_size)
            rl.draw_text(
                hint_text,
                SCREEN_WIDTH//2 - text_width//2,
                SCREEN_HEIGHT//2 - font_size//2,
                font_size,
                HINT_COLOR
            )
            return

        # Draw edges
        for edge in self.edges:
            self.draw_edge(
                self.nodes[edge.u],
                self.nodes[edge.v],
                EDGE_COLOR,
                EDGE_THICKNESS
            )

        # Draw highlighted path
        if self.highlighted_path:
            for i in range(len(self.highlighted_path) - 1):
                u, v = self.highlighted_path[i], self.highlighted_path[i + 1]
                self.draw_edge(
                    self.nodes[u],
                    self.nodes[v],
                    PATH_COLOR,
                    EDGE_THICKNESS + 1
                )

        # Draw nodes
        for i, node in enumerate(self.nodes):
            color = NODE_COLOR
            if i == self.selected_node:
                color = NODE_SELECTED_COLOR
            elif node.hover:
                color = NODE_HOVER_COLOR
            self.draw_node(node, i, color)

        # Draw status text with background
        if self.status:
            padding = 20
            font_size = 24
            text_width = rl.measure_text(self.status, font_size)
            
            # Draw semi-transparent background
            rl.draw_rectangle(
                10,
                10,
                text_width + padding * 2,
                font_size + padding,
                (0, 0, 0, 128)
            )
            
            # Draw status text
            rl.draw_text(
                self.status,
                20,
                20,
                font_size,
                TEXT_COLOR
            )

    def update(self):
        mx, my = rl.get_mouse_x(), rl.get_mouse_y()
        
        # Update node hover states
        self.hover_node = None
        for i, node in enumerate(self.nodes):
            node.hover = self.distance(mx, my, node.x, node.y) <= NODE_RADIUS
            if node.hover:
                self.hover_node = i

        # Handle mouse clicks
        if rl.is_mouse_button_pressed(rl.MOUSE_RIGHT_BUTTON):
            if self.hover_node is not None:
                self.delete_node(self.hover_node)
        
        elif rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
            if self.hover_node is None:
                self.add_node(mx, my)
            else:
                if self.selected_node is None:
                    self.selected_node = self.hover_node
                else:
                    self.add_edge(self.selected_node, self.hover_node)
                    self.selected_node = None
                    self.check_eulerian()

def main():
    rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Modern Euler Path Finder")
    rl.set_target_fps(60)
    
    app = EulerPathFinder()
    
    while not rl.window_should_close():
        app.update()
        
        rl.begin_drawing()
        app.draw()
        rl.end_drawing()
    
    rl.close_window()

if __name__ == "__main__":
    main()
