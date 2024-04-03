"""Tron, classic arcade game.

Exercises

1. Make the tron players faster/slower.
2. Stop a tron player from running into itself.
3. Allow the tron player to go around the edge of the screen.
4. How would you create a computer player?
"""
import math
import turtle
from freegames import square, vector
import tkinter.simpledialog as simpledialog
import math
import random

from queue import PriorityQueue
import numpy as np

MOVEMENT_SIZE = 4

class Player:
    def __init__(self, position, aim, color, key_left, key_right, is_ai=False):
        self.position = position
        self.aim = vector(4 if color == 'red' else -4, 0)
        self.aim = aim
        self.body = set()
        self.color = color
        self.key_left = key_left
        self.key_right = key_right
        self.is_ai = is_ai

    def get_position(self):
        return self.position

    def get_aim(self):
        return self.aim

    def rotate_left(self):
        self.aim.rotate(90)

    def rotate_right(self):
        self.aim.rotate(-90)

    def get_key_right(self):
        return self.key_right

    def get_key_left(self):
        return self.key_left

    def get_body(self):
        return self.body

    def move(self):
        # Updated for edge wrapping
        next_position = self.position + self.aim
        # print(self.position)
        # print(self.aim)
        # print(next_position)
        # print()
        # print()
        next_position.x = (next_position.x + 200) % 400 - 200
        next_position.y = (next_position.y + 200) % 400 - 200
        self.position = next_position
        # self.body.add(self.position.copy())

    def get_projected_movements(self, num_movements):
        set_projected = set()
        for number in range(1, num_movements):
            set_projected.add(self.position + (number * self.aim))
        return set_projected


    def add_to_body(self, head_val):
        self.body.add(head_val)

def ask_to_play_ai():
    """Asks the player if they are ready to play."""
    # This uses the underlying Tkinter root window to ask for user input.
    answer = simpledialog.askstring("AI/Human?", "Do you want to play an AI or a Human? (AI/Human)")
    return answer.lower() == 'ai'

def inside(head):
    """Return True if head inside screen."""
    return -200 < head.x < 200 and -200 < head.y < 200

def write_text(text, x_loc, y_loc, align, font_size=12, text_turtle=None):
    # Instruction turtle
    if(text_turtle == None):
        text_turtle = turtle.Turtle()
        text_turtle.hideturtle()
    text_turtle.penup()
    text_turtle.goto(x_loc, y_loc)
    text_turtle.write(text, align=align, font=("Arial", font_size, "normal"))

def draw_border():
    """Draws a thicker black border around the game window."""
    border_turtle = turtle.Turtle()
    border_turtle.hideturtle()
    border_turtle.penup()
    border_turtle.color('black')
    border_turtle.goto(-205, -205)  # Slightly larger than the inside boundary
    border_turtle.pendown()
    border_turtle.pensize(10)  # Increased pen size for a thicker border
    for _ in range(4):
        border_turtle.forward(410)  # Matches the adjusted coordinates
        border_turtle.left(90)
    border_turtle.penup()

def euclidean_distance(point1, point2):
    """Calculate the Euclidean distance between two 2D points."""
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance

def manhattan_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    distance = abs(x2 - x1) + abs(y2 - y1)
    return distance

# Based off Tron code from Pascal van Kooten
def choose_direction(old, new):
    if old.x < new.x:
        return "RIGHT"
    if old.y < new.y:
        return "UP"
    if old.x > new.x:
        return "LEFT"
    return "DOWN"

# Returns an array that has possible neighboring positions that the AI player can  move into
def get_neighbors(position):
    neighbors = []

    right_position = position + vector(4, 0)
    left_position = position + vector(-4, 0)
    up_position = position + vector(0, 4)
    down_position = position + vector(0, -4)
    if inside(right_position) and right_position not in p1.get_body() and right_position not in p2.get_body():
        neighbors.append(right_position)
    if inside(left_position) and left_position not in p1.get_body() and left_position not in p2.get_body():
        neighbors.append(left_position)
    if inside(up_position) and up_position not in p1.get_body() and up_position not in p2.get_body():
        neighbors.append(up_position)
    if inside(down_position) and down_position not in p1.get_body() and down_position not in p2.get_body():
        neighbors.append(down_position)
    return neighbors

def Dijkstra(board, position, occupied):
    # Set up a priority queue to use in Dijkstra
    queue = PriorityQueue()

    # print("position: " + str(position))

    # Get how x and y lengths of the 2D array that represents the board
    # Both x_max and y_max should be 100
    x_max, y_max = board.shape

    print(x_max)
    print(y_max)

    # Create a new 2D array that has the same shape as the board and mark every location with 0s
    # 0 means that we have not visited there yet
    visited = np.zeros(board.shape)
    # print(visited)

    # For each position that is occupied, mark it with 1
    # 1 means that we visited that location
    for vector in occupied:
        # If the occupied position is not the current position
        if vector != position: 
            # Add it to the visited position
            x_position = int(vector.x / 4) + 50
            y_position = int(vector.y / 4) + 50
            board[(x_position, y_position)] = -1

    # Put in the priority queue the distance and position pair where we begin the Dijkstra's algorithm
    queue.put((0, (int(position.x / 4) + 50 , int(position.y / 4) + 50)))

    # While the priority queue is not empty
    while not queue.empty():

        # Get the distance and position pair from the queue
        distance, xy = queue.get()

        # If we already visited that position, we move onto the next position
        if visited[xy]:
            continue
        # If we haven't visited that position yet, we mark it with 1 to show that it has been visited
        visited[xy] = 1

        # We record how many steps it takes to get to that position
        board[xy] = distance

        # Get the x value and y value of that position
        x,y = xy

        # For each neighboring position,
        for x1, y1 in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):

            # If the neighboring position's x value and y value are within the board and we have not visited there yet,
            if 0 <= x1 < x_max and 0 <= y1 < y_max and board[x1, y1] >= 0 and visited[x1, y1] == 0:

                # If the new distance is less than the distance that is already recorded for the neighboring position
                if distance + 1 < board[x1, y1]:

                    # Update the distance for that neighboring position
                    board[x1, y1] = distance + 1
                    # print("board[" + str(x1) + ", " + str(y1) + "] = " + str(board[x1, y1]))

                    # Put into the priority queue the neighboring position
                    queue.put((distance + 1, (x1, y1)))
    # print(board)
    return board

def create_new_board(p1board, p2board):
    new_board = np.zeros(p1board.shape)
    x, y = p1board.shape
    for i in range(x):
        for j in range(y):
            if p1board[i, j] != -1 and p2board[i, j] != -1:
                if p1board[i, j] <= p2board[i, j]:
                    new_board[i, j] = 1
                elif p1board[i, j] > p2board[i, j]:
                    new_board[i, j] = 2
    # print(new_board)
    return new_board

def count_num_positions(new_board):
    x, y = new_board.shape
    print("x: " + str(x))
    print("y: " + str(y))
    p1_count = 0
    p2_count = 0
    for i in range(x):
        for j in range(y):
            if new_board[i, j] == 1:
                p1_count = p1_count + 1
            if new_board[i, j] == 2:
                p2_count = p2_count + 1
    print("p1_count: " + str(p1_count))
    print("p2_count: " + str(p2_count))
    return [p1_count, p2_count]

def calculate_score(position_count):
    p1_count, p2_count = position_count
    # return p2_count * 1000
    return p2_count * 10000000 + p1_count * -100000

def calculate_sum_shortest_distance(player_num, player_board, new_board):
    x, y = player_board.shape
    sum_shortest_distance = 0
    for i in range(x):
        for j in range(y):
            if new_board[i, j] == player_num:
                sum_shortest_distance += player_board[i, j]
    return sum_shortest_distance

def turn_or_not(direction, aim):

    # When we are already moving right:

    # If we are moving right and we want to go up, turn left
    if aim == vector(4, 0) and direction == "UP":
        return 90
    # If we are moving right and we want to go down, turn right
    if aim == vector(4, 0) and direction == "DOWN":
        return -90
    # If we are moving right and we want to go right, do not turn
    if aim == vector(4, 0) and direction == "RIGHT":
        return 0
    
    # Cannot move in the opposite direction, but have it just in case
    if aim == vector(4, 0) and direction == "LEFT":
        return 0
    
    # When we are already moving left:
    
    # If we are moving left and we want to go up, turn right
    if aim == vector(-4, 0) and direction == "UP":
        return -90
    # If we are moving left and we want to go down, turn left
    if aim == vector(-4, 0) and direction == "DOWN":
        return 90
    # If we are moving left and we want to go left, do not turn
    if aim == vector(-4, 0) and direction == "LEFT":
        return 0
    
    # Cannot move in the opposite direction, but have it just in case
    if aim == vector(-4, 0) and direction == "RIGHT":
        return 0
    
    # When we are already moving up:

    # If we are moving up and we want to go up, do not turn
    if aim == vector(0, 4) and direction == "UP":
        return 0
    # If we are moving up and we want to go left, turn left
    if aim == vector(0, 4) and direction == "LEFT":
        return 90
    # If we are moving up and we want to go right, turn right
    if aim == vector(0, 4) and direction == "RIGHT":
        return -90
    
    # Cannot go in the opposite direction, but have it just in case
    if aim == vector(0, 4) and direction == "DOWN":
        return 0
    
    # When we are already moving down:
    
    # If we are moving down and we want to go down, do not turn
    if aim == vector(0, -4) and direction == "DOWN":
        return 0
    # If we are moving down and we want to go left, turn right
    if aim == vector(0, -4) and direction == "LEFT":
        return -90
    # If we are moving down and we want to go right, turn left
    if aim == vector(0, -4) and direction == "RIGHT":
        return 90
    
    # Cannot go in the opposite direction, but have it just in case
    if aim == vector(0, -4) and direction == "UP":
        return 0
    
def draw(center_turtle):
    """Advance players and draw game."""

    if p2.is_ai:
        SIZE = 101

        p1_board = np.matrix(np.ones((SIZE,SIZE)) * np.inf)
        p2_board = np.matrix(np.ones((SIZE,SIZE)) * np.inf)

        occupied = p1.get_body().union(p2.get_body())
        # occupied = p1.get_body()

        neighbor_scores = []

        best_neighbor = []

        p1_board = Dijkstra(p1_board, p1.get_position(), occupied)
        print(p1_board)

        for neighbor in get_neighbors(p2.get_position()):
            p2_board = Dijkstra(p2_board, neighbor, occupied)
            print(p2_board)
            new_board = create_new_board(p1_board, p2_board)
            print(new_board)
            position_count = count_num_positions(new_board)
            score = calculate_score(position_count)
            # score = 0
            # score += calculate_sum_shortest_distance(2, p2_board, new_board) * -1
            score += calculate_sum_shortest_distance(2, p2_board, new_board)
            print(score)
            neighbor_scores.append((score, neighbor))
        
        # print()
        # print()
        # print()
        
        if neighbor_scores:
            best_neighbor = sorted(neighbor_scores, key=lambda x: x[0], reverse=True)[0]
            direction = choose_direction(p2.get_position(), best_neighbor[-1])
            turn_degree = turn_or_not(direction, p2.aim)
            print(turn_degree)
            
            if turn_degree == 90:
                p2.rotate_left()
                
            if turn_degree == -90:
                p2.rotate_right()
        

    #p1xy.move(p1aim)
    p1.move()
    p1head = p1.get_position().copy()
    # print(p1.body)

    #p2xy.move(p2aim)
    
    p2.move()
    p2head = p2.get_position().copy()

    p1_failure = not inside(p1head) or p1head in p2.get_body() or p1head in p1.get_body()
    p2_failure = not inside(p2head) or p2head in p1.get_body() or p2head in p2.get_body()
    if p1_failure and p2_failure or p1head == p2head:
        print('TIE!')
        write_text("Game Over!\nTIE.", 0, 0, "center", 20, center_turtle)
        return
    elif p1_failure:
        print('Player blue wins!')
        write_text("Game Over!\nBlue wins.", 0, 0, "center", 20, center_turtle)
        return
    elif p2_failure:
        print('Player red wins!')
        write_text("Game Over!\nRed wins.", 0, 0, "center", 20, center_turtle)
        return

    # p1body.add(p1head)
    p1.add_to_body(p1head)
    # p2body.add(p2head)
    p2.add_to_body(p2head)

    square(p1.get_position().x, p1.get_position().y, 3, 'red')
    square(p2.get_position().x, p2.get_position().y, 3, 'blue')
    turtle.update()

    # DECISION TREE LOGIC HERE
    # background color changes indicate what behavior the AI should be performing
    # if p2.is_ai:
    #     head_manhattan_distance = manhattan_distance(p2.get_position(), p1.get_position())
    #     # Checks if any of the projected movements of player 2 and any of the pixels in player 1 are the same.
    #     peril_movements = p2.get_projected_movements(20) & p1.get_body()
    #     # Allows for setting the background color to help debug.
    #     turtle.colormode(255)
    #     # If the head of p2 is close to the head of p1.
    #     if head_manhattan_distance < (10 * MOVEMENT_SIZE):
    #         # Placeholder for the most evasive behavior.
    #         turtle.bgcolor(255, 200, 200)
    #         random_number = random.randint(1, 5)
    #         if random_number == 1:
    #             p2.rotate_right()
    #         elif random_number == 2:
    #             p1.rotate_left()
    #     # If a collision is projected.
    #     elif len(peril_movements) > 0:
    #         # Placeholder code for mid-tier (slightly) evasive behavior.
    #         turtle.bgcolor(255, 200, 100)
    #         random_number = random.randint(1, 12)
    #         if random_number == 1:
    #             p2.rotate_right()
    #         elif random_number == 2:
    #             p1.rotate_left()
    #     else:
    #         turtle.bgcolor('white')


    turtle.ontimer(lambda: draw(center_turtle), 100)

if __name__ == '__main__':
    p1xy = vector(-100, 0)
    p1aim = vector(MOVEMENT_SIZE, 0)
    p1 = Player(p1xy, p1aim, 'red', 'a', 'd')
    #p1body = set()

    p2xy = vector(100, 0)
    p2aim = vector(-1 * MOVEMENT_SIZE, 0)
    p2 = Player(p2xy, p2aim, 'blue', 'j', 'l', is_ai=ask_to_play_ai())
    #p2body = set()

    players = [p1, p2]

    turtle.setup(450, 600, 0, 0)
    turtle.bgcolor('white')
    turtle.hideturtle()

    turtle.tracer(False)
    turtle.listen()

    for player in players:
        if not player.is_ai:
            turtle.onkey(player.rotate_left, player.key_left)
            turtle.onkey(player.rotate_right, player.key_right)

    draw_border()

    center_turtle = turtle.Turtle()
    center_turtle.hideturtle()
    write_text("TRON", 0, 240, "center")
    write_text("Red Player: \nLeft: 'a'\nRight: 'd'", -150, -270, "left")
    write_text("Blue Player (If Human): \nLeft: 'j'\nRight: 'l'", 150, -270, "right")

    draw(center_turtle)

    turtle.done()

