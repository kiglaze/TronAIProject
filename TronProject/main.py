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
from enum import Enum

MOVEMENT_SIZE = 4

class Behavior(Enum):
    AGGRESSIVE = 1
    EVASIVE = 2
    RANDOM = 3

class AIType(Enum):
    HUMAN = 0
    TYPE_A = 1
    TYPE_B = 2

class Player:
    def __init__(self, position, aim, color, key_left, key_right, is_ai=False):
        self.position = position
        #self.aim = vector(4 if color == 'red' else -4, 0)
        self.aim = aim
        self.body = set()
        self.color = color
        self.key_left = key_left
        self.key_right = key_right
        self.behavior = Behavior.RANDOM
        self.is_ai = is_ai

    def set_behavior(self, behavior_enum: Behavior, turtle_obj=None):
        self.behavior = behavior_enum
        if turtle_obj is not None:
            if behavior_enum == Behavior.EVASIVE:
                turtle_obj.bgcolor('pink')
            elif behavior_enum == Behavior.AGGRESSIVE:
                turtle_obj.bgcolor('lightgreen')
            elif behavior_enum == Behavior.RANDOM:
                turtle_obj.bgcolor('yellow')

    def get_behavior(self) -> Behavior:
        return self.behavior

    def get_position(self):
        return self.position

    def get_aim(self):
        return self.aim

    def set_aim(self, aim_vect):
        desired_vect = self.get_cardinal_unit_direction_vector(aim_vect)
        is_desired_val = (((abs(aim_vect.x) == MOVEMENT_SIZE or abs(aim_vect.y) == MOVEMENT_SIZE)
                          and not (abs(aim_vect.x) == MOVEMENT_SIZE and abs(aim_vect.y) == MOVEMENT_SIZE))
                          and (aim_vect.x == 0 or aim_vect.y == 0) and not (aim_vect.x == 0 and aim_vect.y == 0))

        if is_desired_val and self.get_aim() != desired_vect and self.get_aim() * -1 != desired_vect:
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

    def get_body_com(self):
        body_pixel_count = len(self.get_body())
        body_x_sum = 0
        body_y_sum = 0
        for pixel in self.get_body():
            body_x_sum += pixel.x
            body_y_sum += pixel.y
        body_x_avg = body_x_sum / body_pixel_count
        body_y_avg = body_y_sum / body_pixel_count
        return vector(body_x_avg, body_y_avg)

    def get_cardinal_dir_vect_opponent_com(self, opponent_player):
        direction_vect = self.direction_vector(self.get_position(), opponent_player.get_body_com())
        return self.get_cardinal_unit_direction_vector(direction_vect)

    def is_facing_opponent_com(self, opponent_player):
        return self.get_aim() == self.get_cardinal_dir_vect_opponent_com(opponent_player)

    def is_far_from_opponent(self, opponent_player, threshold: int):
        return self.get_closest_enemy_pixel_distance(opponent_player) > threshold * MOVEMENT_SIZE

    def direction_vector(self, pixel1, pixel2):
        x1, y1 = pixel1
        x2, y2 = pixel2

        dx = x2 - x1
        dy = y2 - y1

        return vector(dx, dy)

    def manhattan_distance(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        distance = abs(x2 - x1) + abs(y2 - y1)
        return distance

    def is_head_within_dist_opponent_head(self, opponent_player, threshold_moves: int):
        head_manhattan_distance = manhattan_distance(self.get_position(), opponent_player.get_position())
        return head_manhattan_distance < (threshold_moves * MOVEMENT_SIZE)

    def is_crash_into_opponent_anticipated(self, opponent_player, threshold_moves: int):
        peril_movements = self.get_projected_movements(threshold_moves) & opponent_player.get_body()
        return len(peril_movements) > 0

    def get_closest_enemy_pixel_direction_vect(self, opponent_player):
        result = direction_vector(self.get_position(), self.get_closest_enemy_pixel_position(opponent_player))
        if result.x == 0 and result.y == 0:
            print(result)
        return result

    def get_closest_enemy_pixel_position(self, opponent_player):
        opponent_body = opponent_player.get_body()
        player_pos = self.get_position()
        closest_pixel = None
        enemy_min_distance = float('inf')
        for pixel_pos in opponent_body:
            pixel_dist = manhattan_distance(player_pos, pixel_pos)
            if pixel_dist < enemy_min_distance:
                enemy_min_distance = pixel_dist
                closest_pixel = pixel_pos
        return closest_pixel

    def get_closest_opponent_projected_pixel(self, opponent_player, projected_pixels_count: int):
        opponent_projected_movements = opponent_player.get_projected_movements(projected_pixels_count)
        player_pos = self.get_position()
        closest_pixel = None
        enemy_min_distance = float('inf')
        for pixel_pos in opponent_projected_movements:
            pixel_dist = manhattan_distance(player_pos, pixel_pos)
            if pixel_dist < enemy_min_distance:
                enemy_min_distance = pixel_dist
                closest_pixel = pixel_pos
        return closest_pixel

    def get_closest_projected_enemy_pixel_dir_vect(self, opponent_player, projected_pixels_count: int):
        return direction_vector(player.get_position(), self.get_closest_opponent_projected_pixel(opponent_player, projected_pixels_count))

    # Returns True if within a certain range of enemy pixel.
    def face_closest_enemy_pixel(self, opponent_player):
        direction_vect_closest_enemy_pixel = self.get_closest_enemy_pixel_direction_vect(opponent_player)
        ## -3, -4 => 0, -1
        ## -5, 2 => -1, 0
        ## 7, -5 => 1, 0
        ## 9, 15 => 0, 1
        if direction_vect_closest_enemy_pixel.x == 0 and direction_vect_closest_enemy_pixel.y == 0:
            return False
        else:
            desired_direction_unit_vect = self.get_cardinal_unit_direction_vector(direction_vect_closest_enemy_pixel)
            player.set_aim(desired_direction_unit_vect)
            print(desired_direction_unit_vect)
            return True

    def get_random_turn_direction(self, exclude_direction_vectors=None):
        current_direction = self.get_aim()
        from_direction = -1 * self.get_aim()
        exclude_direction_vectors_all = [current_direction, from_direction]
        if exclude_direction_vectors is not None:
            for exclude_direction_vector in exclude_direction_vectors:
                exclude_direction_vectors_all.append(exclude_direction_vector)
        all_possible_directions = [vector(0, -MOVEMENT_SIZE), vector(0, MOVEMENT_SIZE), vector(-MOVEMENT_SIZE, 0), vector(MOVEMENT_SIZE, 0)]
        for exclude_direction in exclude_direction_vectors_all:
            if exclude_direction in all_possible_directions:
                all_possible_directions.remove(exclude_direction)
        if len(all_possible_directions) == 0:
            return None
        else:
            return random.choice(all_possible_directions)
    def face_away_from_closest_enemy_pixel(self, opponent_player):
        direction_vect_closest_enemy_pixel = self.get_closest_enemy_pixel_direction_vect(opponent_player)
        ## -3, -4 => 0, -1
        ## -5, 2 => -1, 0
        ## 7, -5 => 1, 0
        ## 9, 15 => 0, 1
        if direction_vect_closest_enemy_pixel.x == 0 and direction_vect_closest_enemy_pixel.y == 0:
            return False
        else:
            desired_direction_unit_vect = self.get_cardinal_unit_direction_vector(direction_vect_closest_enemy_pixel)
            random_turn_direction_vect = self.get_random_turn_direction([desired_direction_unit_vect])
            player.set_aim(random_turn_direction_vect)
            print(desired_direction_unit_vect)
            return True

    def is_facing_closest_opponent_pixel(self, opponent_player):
        direction_vect_closest_enemy_pixel = self.get_closest_enemy_pixel_direction_vect(opponent_player)
        if direction_vect_closest_enemy_pixel.x == 0 and direction_vect_closest_enemy_pixel.y == 0:
            return False
        else:
            desired_direction_unit_vect = self.get_cardinal_unit_direction_vector(direction_vect_closest_enemy_pixel)
            return self.get_aim() == desired_direction_unit_vect

    def is_closer_to_projected_pixel(self, opponent_player, projected_pixels_count: int):
        target_pixel = self.get_closest_opponent_projected_pixel(opponent_player, projected_pixels_count)
        player_distance = self.manhattan_distance(self.get_position(), target_pixel)
        opponent_distance = self.manhattan_distance(opponent_player.get_position(), target_pixel)
        return player_distance < opponent_distance

    def face_closest_projected_enemy_pixel(self, opponent_player, projected_pixels_count: int):
        direction_vect_closest_projected_enemy_pixel = self.get_closest_projected_enemy_pixel_dir_vect(opponent_player, projected_pixels_count)
        desired_direction_unit_vect = self.get_cardinal_unit_direction_vector(direction_vect_closest_projected_enemy_pixel)
        print(desired_direction_unit_vect)
        if desired_direction_unit_vect.x == 0 and desired_direction_unit_vect.y == 0:
            return False
        else:
            player.set_aim(desired_direction_unit_vect)
            return True

    def get_cardinal_unit_direction_vector(self, input_direction_vector):
        result_x = 0
        result_y = 0
        if abs(input_direction_vector.x) > abs(input_direction_vector.y):
            result_x = int((input_direction_vector.x / abs(input_direction_vector.x))) if input_direction_vector.x != 0 else 0
            result_y = 0
        else:
            result_x = 0
            result_y = int((input_direction_vector.y / abs(input_direction_vector.y))) if input_direction_vector.y != 0 else 0
        if result_x == 0 and result_y == 0:
            print(result_x, result_y)
        return vector(result_x * MOVEMENT_SIZE, result_y * MOVEMENT_SIZE)

    def get_closest_enemy_pixel_distance(self, opponent_player):
        return manhattan_distance(player.get_position(), player.get_closest_enemy_pixel_position(opponent_player))

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

# For DECISION TREES ONLY
class DecisionNode:
    """A node in the decision tree that makes a decision to which node to proceed next."""
    def __init__(self, decision_function, true_node, false_node):
        self.decision_function = decision_function
        self.true_node = true_node
        self.false_node = false_node

    def run(self):
        if self.decision_function():
            return self.true_node.run()
        else:
            return self.false_node.run()

class Condition(Node):
    """Represents a condition check."""
    def __init__(self, condition):
        self.condition = condition

    def run(self):
        return self.condition()

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

def direction_vector(pixel1, pixel2):
    x1, y1 = pixel1
    x2, y2 = pixel2

    dx = x2 - x1
    dy = y2 - y1

    return vector(dx, dy)

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
    return probability_value <= probability

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
    active_ai = AIType.TYPE_A
    if p2.is_ai:
        if active_ai == AIType.TYPE_A:
            # Construct the decision tree, type A
            decision_tree = DecisionNode(
                decision_function=partial(p2.is_head_within_dist_opponent_head, p1, 10),
                true_node=Action(partial(p2.set_behavior, Behavior.EVASIVE, turtle)),
                false_node=DecisionNode(decision_function=partial(p2.is_crash_into_opponent_anticipated,p1, 20),
                                        true_node=Action(partial(p2.set_behavior, Behavior.EVASIVE, turtle)),
                                        false_node=DecisionNode(
                                            decision_function=partial(p2.is_facing_opponent_com, p1),
                                            true_node=Action(partial(p2.set_behavior, Behavior.RANDOM, turtle)),
                                            false_node=Action(partial(p2.set_behavior, Behavior.AGGRESSIVE, turtle))
                                        )
                )
            )
            # Execute the decision tree
            outcome = decision_tree.run()
        elif active_ai == AIType.TYPE_B:
            # Construct the decision tree, type B
            #decision_tree = DecisionNode()
            # Execute the decision tree
            #outcome = decision_tree.run()



        # AGGRESSIVE BEHAVIOR TREE
        # Constructing the behavior tree
        #p2.set_behavior(Behavior.AGGRESSIVE)
        #p2.set_behavior(Behavior.EVASIVE)

        #root = Selector([
        #    Sequence([
        #        Condition(is_enemy_visible),
        #        Action(attack)
        #    ]),
        #    Action(search_for_enemy)
        #])

        if p2.get_behavior() == Behavior.AGGRESSIVE:
            root = Selector([
                Sequence([
                    Condition(partial(p2.is_closer_to_projected_pixel, p1, 40 * MOVEMENT_SIZE)),
                    Action(partial(p2.face_closest_projected_enemy_pixel, p1, 40 * MOVEMENT_SIZE))
                ]),
                Sequence([
                    Condition(partial(p2.is_far_from_opponent, p1, 25)),
                    Condition(partial(true_with_probability, 0.70)),
                    Action(partial(p2.face_closest_enemy_pixel, p1))
                ])
            ])

            root.run()
        elif p2.get_behavior() == Behavior.EVASIVE:
            root = Selector([
                Sequence([
                    # Need to avoid collision.
                    Condition(partial(p2.is_facing_closest_opponent_pixel, p1)),
                    Condition(partial(true_with_probability, 0.70)),
                    Action(partial(p2.face_away_from_closest_enemy_pixel, p1))
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

