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

def write_text(text, x_loc, y_loc, align, text_turtle=None):
    # Instruction turtle
    if(text_turtle == None):
        text_turtle = turtle.Turtle()
        text_turtle.hideturtle()
    text_turtle.penup()
    text_turtle.goto(x_loc, y_loc)
    text_turtle.write(text, align=align, font=("Arial", 12, "normal"))

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

def draw(center_turtle):
    """Advance players and draw game."""
    #p1xy.move(p1aim)
    p1.move()
    p1head = p1.get_position().copy()

    #p2xy.move(p2aim)
    p2.move()
    p2head = p2.get_position().copy()

    if not inside(p1head) or p1head in p2.get_body():
        print('Player blue wins!')
        write_text("Game Over!\nBlue wins.", 0, 0, "center", center_turtle)
        return

    if not inside(p2head) or p2head in p1.get_body():
        print('Player red wins!')
        write_text("Game Over!\nRed wins.", 0, 0, "center", center_turtle)
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
        head_euclidean_distance = euclidean_distance(p2.get_position(), p1.get_position())
        head_manhattan_distance = manhattan_distance(p2.get_position(), p1.get_position())
        if head_manhattan_distance < (10 * MOVEMENT_SIZE):
            turtle.bgcolor('lightblue')
        elif 1:
            turtle.bgcolor('lightgreen')
        else:
            turtle.bgcolor('white')


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

