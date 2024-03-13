"""Tron, classic arcade game.

Exercises

1. Make the tron players faster/slower.
2. Stop a tron player from running into itself.
3. Allow the tron player to go around the edge of the screen.
4. How would you create a computer player?
"""
import math
from turtle import *
from freegames import square, vector
import tkinter.simpledialog as simpledialog

def ask_to_play_ai():
    """Asks the player if they are ready to play."""
    # This uses the underlying Tkinter root window to ask for user input.
    answer = simpledialog.askstring("AI/Human?", "Do you want to play an AI or a Human? (AI/Human)")
    return answer.lower() == 'ai'

def inside(head):
    """Return True if head inside screen."""
    return -200 < head.x < 200 and -200 < head.y < 200

def write_text(text, x_loc, y_loc, align):
    # Instruction turtle
    instruct_turtle = Turtle()
    instruct_turtle.hideturtle()
    instruct_turtle.penup()
    instruct_turtle.goto(x_loc, y_loc)
    instruct_turtle.write(text, align=align, font=("Arial", 12, "normal"))

def draw_border():
    """Draws a thicker black border around the game window."""
    border_turtle = Turtle()
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

def draw():
    """Advance players and draw game."""
    p1xy.move(p1aim)
    p1head = p1xy.copy()

    p2xy.move(p2aim)
    p2head = p2xy.copy()

    if not inside(p1head) or p1head in p2body:
        print('Player blue wins!')
        write_text("Game Over!\nBlue wins.", 0, 0, "center")
        return

    if not inside(p2head) or p2head in p1body:
        print('Player red wins!')
        write_text("Game Over!\nRed wins.", 0, 0, "center")
        return

    # Can be used to power the AI's rotation.
    global p2aim_rotate_val
    if p2aim_rotate_val != 0:
        p2aim.rotate(p2aim_rotate_val)
        p2aim_rotate_val = 0
    # ###

    p1body.add(p1head)
    p2body.add(p2head)

    square(p1xy.x, p1xy.y, 3, 'red')
    square(p2xy.x, p2xy.y, 3, 'blue')
    update()
    ontimer(draw, 100)

if __name__ == '__main__':
    p2aim_rotate_val = 0
    p1xy = vector(-100, 0)
    p1aim = vector(4, 0)
    p1body = set()

    p2xy = vector(100, 0)
    p2aim = vector(-4, 0)
    p2body = set()

    setup(450, 600, 0, 0)
    hideturtle()
    tracer(False)
    listen()
    onkey(lambda: p1aim.rotate(90), 'a')
    onkey(lambda: p1aim.rotate(-90), 'd')
    if ask_to_play_ai() == False:
        onkey(lambda: p2aim.rotate(90), 'j')
        onkey(lambda: p2aim.rotate(-90), 'l')

    draw_border()
    write_text("TRON", 0, 240, "center")
    write_text("Red Player: \nLeft: 'a'\nRight: 'd'", -150, -270, "left")
    write_text("Blue Player (If Human): \nLeft: 'j'\nRight: 'l'", 150, -270, "right")


    draw()

    done()

