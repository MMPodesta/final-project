import random
import pygame
from sys import exit
from random import choice
import numpy as np
import pickle


class Player(pygame.sprite.Sprite):
    def __init__(self, neural_network):
        super().__init__()
        # walking frames
        player_walk_1 = pygame.image.load("../assets/player_walk_1.png").convert_alpha()
        player_walk_2 = pygame.image.load("../assets/player_walk_2.png").convert_alpha()
        self.player_walk = [player_walk_1, player_walk_2]
        self.player_index = 0

        # Ducking frames
        player_duck_1 = pygame.image.load("../assets/duck1.png").convert_alpha()
        player_duck_2 = pygame.image.load("../assets/duck2.png").convert_alpha()
        player_duck_3 = pygame.image.load("../assets/duck3.png").convert_alpha()
        self.player_duck = [player_duck_1, player_duck_2, player_duck_3]
        self.is_ducking = False
        self.duck_index = 0

        # jump frame
        self.player_jump = pygame.image.load("../assets/jump.png").convert_alpha()
        self.gravity = 0

        # set player position
        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(random.randint(20, 150), 300))

        # NN arguments
        self.neural_network = neural_network

    def start_ducking(self):
        self.is_ducking = True
        self.duck_index = 0
        self.rect.height = self.player_duck[2].get_height()  # Adjust the hit box height

    def stop_ducking(self):
        self.is_ducking = False
        self.rect.height = self.player_walk[0].get_height()  # Reset the hit box height

    def AI_programmatic_jump(self):
        # Only allow jumping if the player is on the ground and not ducking
        if self.rect.bottom >= 300 and not self.is_ducking:
            self.gravity = -20

    def AI_programmatic_duck(self):
        if not self.is_ducking:
            self.start_ducking()

    def stop_AI_ducking(self):
        if self.is_ducking:
            self.stop_ducking()

    def apply_gravity(self):
        # Make player quickly fall back to the floor
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def animation_state(self):
        if self.is_ducking:
            self.duck()  # Call ducking animation

        elif self.rect.bottom < 300:
            self.image = self.player_jump

        else:
            self.walk()  # Call walking animation

    def walk(self):
        self.player_index += 0.1
        if self.player_index >= len(self.player_walk):
            self.player_index = 0
        self.image = self.player_walk[int(self.player_index)]

    def duck(self):
        # Hold the last frame of ducking while 's' is pressed
        if self.duck_index < len(self.player_duck) - 1:
            self.duck_index += 0.1
        self.image = self.player_duck[int(self.duck_index)]

    def update(self):
        self.apply_gravity()
        self.animation_state()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obstacle_type):
        super().__init__()
        self.obstacle_type = obstacle_type

        if self.obstacle_type == "fly":
            fly_1 = pygame.image.load("../assets/Fly1.png").convert_alpha()
            fly_2 = pygame.image.load("../assets/Fly2.png").convert_alpha()
            self.frames = [fly_1, fly_2]
            self.y_pos = 150

        elif self.obstacle_type == "snail":
            snail_1 = pygame.image.load("../assets/snail1.png").convert_alpha()
            snail_2 = pygame.image.load("../assets/snail2.png").convert_alpha()
            self.frames = [snail_1, snail_2]
            self.y_pos = 300

        elif self.obstacle_type == "water":
            water_1 = pygame.image.load("../assets/water1.png").convert_alpha()
            water_2 = pygame.image.load("../assets/water2.png").convert_alpha()
            water_3 = pygame.image.load("../assets/water3.png").convert_alpha()
            water_4 = pygame.image.load("../assets/water4.png").convert_alpha()
            water_5 = pygame.image.load("../assets/water5.png").convert_alpha()
            water_6 = pygame.image.load("../assets/water6.png").convert_alpha()
            water_7 = pygame.image.load("../assets/water7.png").convert_alpha()
            water_8 = pygame.image.load("../assets/water8.png").convert_alpha()
            water_9 = pygame.image.load("../assets/water9.png").convert_alpha()

            self.frames = [water_1, water_2, water_3, water_4, water_5, water_6, water_7, water_8, water_9]
            self.y_pos = 250

        elif self.obstacle_type == "coin":
            coin_1 = pygame.image.load("../assets/Gold1.png").convert_alpha()
            coin_2 = pygame.image.load("../assets/Gold2.png").convert_alpha()
            coin_3 = pygame.image.load("../assets/Gold3.png").convert_alpha()
            coin_4 = pygame.image.load("../assets/Gold4.png").convert_alpha()
            self.frames = [coin_1, coin_2, coin_3, coin_4]
            self.y_pos = choice([150, 250, 300])
            self.collected_by = set()  # Track players who have collected this coin

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(random.randint(900, 1100), self.y_pos))

    def animation_state(self):
        self.animation_index += 0.2
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= 6  # move towards player on the left side of screen
        self.destroy()

    def destroy(self):
        # Destroy object when out of view
        if self.rect.x <= -250:
            self.kill()


def display_score():
    global collected_coins
    # Current score
    current_score = int(pygame.time.get_ticks() / 1000) - start_time
    total_score = current_score + (collected_coins * 5)  # Combine time-based score with coin collection score
    score_surface = test_font.render(f'Score: {total_score}', False, (64, 64, 64))
    score_rectangle = score_surface.get_rect(center=(400, 50))
    screen.blit(score_surface, score_rectangle)

    return total_score


def collision_sprite(player):
    global collected_coins

    # During this frame, get all obstacles which this player collided with
    collided_sprites = pygame.sprite.spritecollide(player.sprite, obstacle_group, False)

    for obstacle in collided_sprites:
        if obstacle.obstacle_type == "coin":
            if player not in obstacle.collected_by:
                obstacle.collected_by.add(player)  # Assure player only collects reward once
                collected_coins += 1
                print("coin collected")

        # obstacle is an enemy
        else:
            # Delete this player
            player.sprite.kill()
            players_list.remove(player)


def relu(x):
    # Introduce Non-Linearity, makes it able to learn complex real world patterns
    # Should be applied to each hidden layer as well as the output.
    return np.maximum(0, x)


def sigmoid(x):
    # Sigmoid activation function
    # Squish output between 0 and 1
    return 1 / (1 + np.exp(-x))


class NeuralNetwork:
    def __init__(self):
        # Generate random numbers from -1 to 1 in a matrix
        self.input_weights = 2 * np.random.random((6, 4)) - 1  # 6 input to 4 hidden neurons
        self.output_weights = 2 * np.random.random((5, 2)) - 1  # (4 hidden neurons + 1 bias) = 5, to 2 outputs

    def forward(self, inputs):
        # Multiply input by 6 input weights and store all 4 results in 4 neurons in the hidden layer
        self.hidden_layer = relu(np.dot(inputs, self.input_weights))

        # Store 1 extra value in hidden layer as number 1(bias)
        self.hidden_layer = np.append(self.hidden_layer, 1)

        # Multiply all (4 neuron values + bias) by 5 output weights
        # Then sum all 5 values into a single output result, and apply sigmoid
        output_layer = sigmoid(np.dot(self.hidden_layer, self.output_weights))

        return output_layer


def load_neural_network(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)


# Initialize the neural network
pygame.init()
screen = pygame.display.set_mode((800, 400))  # width and height
pygame.display.set_caption("Random Mutations - Custom AI Demo")
clock = pygame.time.Clock()
test_font = pygame.font.Font("../assets/Pixeltype.ttf", 50)
game_active = False
max_distance_x = 1000
start_time = 0
score = 0
collected_coins = 0
previous_score = 0
best_score = 0
generation = 1
threshold = 0.5

# Start list of players (Only add the single best player)
players_list = []

# Load the best neural network file
best_neural_network = load_neural_network('best_neural_network.pkl')

# Set up the player
best_player = Player(best_neural_network)
players_list.append(pygame.sprite.GroupSingle(best_player))

# obstacle group
obstacle_group = pygame.sprite.Group()

# Background
sky_surface = pygame.image.load("../assets/Sky.png").convert()
ground_surface = pygame.image.load("../assets/ground.png").convert()

# Intro screen
player_stand = pygame.image.load("../assets/player_stand.png").convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 2)
player_stand_rectangle = player_stand.get_rect(center=(400, 200))

game_name = test_font.render("2D Runner", False, (111, 196, 169))
game_name_rectangle = game_name.get_rect(center=(400, 80))

game_message = test_font.render("Press space to run", False, (111, 196, 169))
game_message_rectangle = game_message.get_rect(center=(400, 330))

# Timer
obstacle_timer = pygame.USEREVENT + 1  # avoid conflict with reserved by '+1'
pygame.time.set_timer(obstacle_timer, 1500)  # New enemy every 1500ms

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_active:
            if event.type == obstacle_timer:
                # Trigger new obstacle
                obstacle_group.add(Obstacle(choice(["coin", "water", "fly", "fly", "fly", "snail", "snail",
                                                    "snail", "snail", "snail"])))

        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                start_time = int(pygame.time.get_ticks() / 1000)

    if game_active:
        # Background
        screen.blit(sky_surface, (0, 0))
        screen.blit(ground_surface, (0, 300))
        score = display_score()

        # Player
        for player in players_list:
            player.draw(screen)
            player.update()

        # Obstacles
        obstacle_group.draw(screen)
        obstacle_group.update()

        for player in players_list:
            # Assess any collision
            collision_sprite(player)

        # Neural Network assessment
        # Calculate horizontal distance to the closest obstacle in front of the player for every frame
        for player in players_list:
            # Extract obstacles that are ahead of the player or overlapping with the player from the right side
            obstacles_ahead = [(obstacle, obstacle.rect.right - player.sprite.rect.left) for obstacle in
                               obstacle_group.sprites() if obstacle.rect.right > player.sprite.rect.left]

            # Sort obstacles by their distance from the player (ascending order)
            obstacles_ahead.sort(key=lambda x: x[1])

            if obstacles_ahead:
                # Start categorical features
                isEnemy = 0
                isCoin = 0
                isHigh = 0
                isLow = 0
                isMid = 0

                # Closest obstacle and its distances in pixels
                closest_obstacle, closest_obstacle_distance_x = obstacles_ahead[0]

                # Normalize the distance to be between 0 and 1
                # Smaller the distance, higher the value
                normalized_distance_x = 1 - (closest_obstacle_distance_x / max_distance_x)

                # check what kind of obstacle
                if closest_obstacle.obstacle_type == "snail" or closest_obstacle.obstacle_type == "fly" or \
                        closest_obstacle.obstacle_type == "water":
                    isEnemy = 1

                elif closest_obstacle.obstacle_type == "coin":
                    isCoin = 1

                # check where is the obstacle on Y
                if closest_obstacle.y_pos == 150:
                    isHigh = 1
                elif closest_obstacle.y_pos == 250:
                    isMid = 1
                elif closest_obstacle.y_pos == 300:
                    isLow = 1

                # input to neural network
                inputs = np.array([normalized_distance_x, isEnemy, isCoin, isHigh, isMid, isLow]).reshape(1, -1)

                # Getting the decision from the network
                output = player.sprite.neural_network.forward(inputs)
                should_jump = output[0] > threshold
                should_duck = output[1] > threshold

                if should_jump:
                    player.sprite.AI_programmatic_jump()

                elif should_duck:
                    player.sprite.AI_programmatic_duck()

                # Stop ducking when neither jumping nor ducking is suggested
                if not should_jump and not should_duck:
                    player.sprite.stop_AI_ducking()

        # End game when all players are dead
        if len(players_list) == 0:
            obstacle_group.empty()
            game_active = False

    else:
        # Update score tracker
        previous_score = score
        if score > best_score:
            best_score = score

        # Reset coins
        collected_coins = 0

        if score == 0:
            # Start window
            screen.fill((94, 129, 162))
            screen.blit(player_stand, player_stand_rectangle)
            screen.blit(game_name, game_name_rectangle)
            screen.blit(game_message, game_message_rectangle)

        else:
            generation += 1

            # Add the best player back to list and reset game
            players_list.append(pygame.sprite.GroupSingle(best_player))
            game_active = True
            start_time = int(pygame.time.get_ticks() / 1000)

    pygame.display.update()
    clock.tick(60)  # loop should not run faster than 60x/second
