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
from functools import partial
import random

MOVEMENT_SIZE = 4

class Player:
    def __init__(self, position, aim, color, key_left, key_right, is_ai=False):
        self.position = position
        #self.aim = vector(4 if color == 'red' else -4, 0)
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

    def set_aim(self, aim_vect):
        desired_vect = get_cardinal_unit_direction_vector(aim_vect)
        if self.get_aim() != desired_vect and self.get_aim() * -1 != desired_vect:
            self.aim = aim_vect

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
        next_position.x = (next_position.x + 200) % 400 - 200
        next_position.y = (next_position.y + 200) % 400 - 200
        self.position = next_position
        self.body.add(self.position.copy())

    def get_projected_movements(self, num_movements):
        set_projected = set()
        for number in range(1, num_movements):
            set_projected.add(self.position + (number * self.aim))
        return set_projected


    def add_to_body(self, head_val):
        self.body.add(head_val)

    def is_far_from_opponent(self, opponent_player, threshold: int):
        return get_closest_enemy_pixel_distance(opponent_player, self) > threshold * MOVEMENT_SIZE

#### START of Behavior Tree
class Node:
    """Base class for all nodes."""
    def run(self):
        raise NotImplementedError("Subclass must implement abstract method")

class Selector(Node):
    """Returns success if any child succeeds."""
    def __init__(self, children=None):
        self.children = children or []

    def run(self):
        for child in self.children:
            if child.run():
                return True
        return False

class Sequence(Node):
    """Returns success if all children succeed."""
    def __init__(self, children=None):
        self.children = children or []

    def run(self):
        for child in self.children:
            if not child.run():
                return False
        return True

class Action(Node):
    """Represents an action node."""
    def __init__(self, action):
        self.action = action

    def run(self):
        return self.action()

class Condition(Node):
    """Represents a condition check."""
    def __init__(self, condition):
        self.condition = condition

    def run(self):
        return self.condition()

# Returns True if within a certain range of enemy pixel.
def hover_near_closest_enemy_pixel(player:Player, opponent_player:Player):
    direction_vect_closest_enemy_pixel = get_closest_enemy_pixel_direction_vect(player, opponent_player)
    ## -3, -4 => 0, -1
    ## -5, 2 => -1, 0
    ## 7, -5 => 1, 0
    ## 9, 15 => 0, 1
    desired_direction_unit_vect = get_cardinal_unit_direction_vector(direction_vect_closest_enemy_pixel)
    print(desired_direction_unit_vect)
    player.set_aim(desired_direction_unit_vect)
    return True

# Example usage:
def is_enemy_visible():
    # Example condition function
    return True

def attack():
    # Example action function
    print("Attacking the enemy!")
    return True

def search_for_enemy():
    # Example action function
    print("Searching for the enemy.")
    return True

def get_closest_enemy_pixel_position(player: Player, opponent_player: Player):
    player_pos = player.get_position()
    opponent_body = opponent_player.get_body()
    closest_pixel = None
    enemy_min_distance = float('inf')
    for pixel_pos in opponent_body:
        pixel_dist = manhattan_distance(player_pos, pixel_pos)
        if pixel_dist < enemy_min_distance:
            enemy_min_distance = pixel_dist
            closest_pixel = pixel_pos
    return closest_pixel

def get_closest_enemy_pixel_distance(player: Player, opponent_player: Player):
    return manhattan_distance(player.get_position(), get_closest_enemy_pixel_position(player, opponent_player))

def direction_vector(pixel1, pixel2):
    x1, y1 = pixel1
    x2, y2 = pixel2

    dx = x2 - x1
    dy = y2 - y1

    return vector(dx, dy)

def get_closest_enemy_pixel_direction_vect(player: Player, opponent_player: Player):
    return direction_vector(player.get_position(), get_closest_enemy_pixel_position(player, opponent_player))

def get_cardinal_unit_direction_vector(input_direction_vector):
    result_x = 0
    result_y = 0
    if (abs(input_direction_vector.x) > abs(input_direction_vector.y)):
        result_x = ((input_direction_vector.x) / abs(input_direction_vector.x))
        result_y = 0
    else:
        result_x = 0
        result_y = ((input_direction_vector.y) / abs(input_direction_vector.y))
    return vector(result_x * MOVEMENT_SIZE, result_y * MOVEMENT_SIZE)

#### END of Behavior Tree



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

def true_with_probability(probability: float):
    # Generate a random float between 0.0 and 1.0
    probability_value = random.random()
    # Return True if the generated number is less than 0.2
    return probability_value < probability

def draw(center_turtle):
    """Advance players and draw game."""
    #p1xy.move(p1aim)
    p1.move()
    p1head = p1.get_position().copy()

    #p2xy.move(p2aim)
    p2.move()
    p2head = p2.get_position().copy()

    p1_failure = not inside(p1head) or p1head in p2.get_body()
    p2_failure = not inside(p2head) or p2head in p1.get_body()
    if p1_failure and p2_failure:
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

    #p1body.add(p1head)
    p1.add_to_body(p1head)
    #p2body.add(p2head)
    p2.add_to_body(p2head)

    square(p1.get_position().x, p1.get_position().y, 3, 'red')
    square(p2.get_position().x, p2.get_position().y, 3, 'blue')
    turtle.update()

    # DECISION TREE LOGIC HERE
    # background color changes indicate what behavior the AI should be performing
    if p2.is_ai:
        head_manhattan_distance = manhattan_distance(p2.get_position(), p1.get_position())
        # Checks if any of the projected movements of player 2 and any of the pixels in player 1 are the same.
        peril_movements = p2.get_projected_movements(20) & p1.get_body()
        # Allows for setting the background color to help debug.
        turtle.colormode(255)
        # If the head of p2 is close to the head of p1.
        if head_manhattan_distance < (10 * MOVEMENT_SIZE):
            # Placeholder for the most evasive behavior.
            turtle.bgcolor(255, 200, 200)
        # If a collision is projected.
        elif len(peril_movements) > 0:
            # Placeholder code for mid-tier (slightly) evasive behavior.
            turtle.bgcolor(255, 200, 100)
        else:
            turtle.bgcolor('white')

        # AGGRESSIVE BEHAVIOR TREE
        # Constructing the behavior tree

        #root = Selector([
        #    Sequence([
        #        Condition(is_enemy_visible),
        #        Action(attack)
        #    ]),
        #    Action(search_for_enemy)
        #])

        root = Selector([
            Sequence([
                Condition(partial(p2.is_far_from_opponent, p1, 5)),
                Condition(partial(true_with_probability, 0.2)),
                Action(partial(hover_near_closest_enemy_pixel, p2, p1))
            ])
        ])

        root.run()


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

