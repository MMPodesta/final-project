import random
import pygame
from sys import exit
from random import choice
import numpy as np


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_walk_1 = pygame.image.load("assets/player_walk_1.png").convert_alpha()
        player_walk_2 = pygame.image.load("assets/player_walk_2.png").convert_alpha()
        self.player_walk = [player_walk_1, player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load("assets/jump.png").convert_alpha()

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(80, 300))
        self.gravity = 0

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
            self.gravity = -20

    def AI_programmatic_jump(self):
        if self.rect.bottom >= 300:  # Check if the player is on the ground
            self.gravity = -20  # Adjust this value as needed

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def animation_state(self):
        if self.rect.bottom < 300:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obstacle_type):
        super().__init__()

        if obstacle_type == "fly":
            fly_1 = pygame.image.load("assets/Fly1.png").convert_alpha()
            fly_2 = pygame.image.load("assets/Fly2.png").convert_alpha()
            self.frames = [fly_1, fly_2]
            y_pos = 300
        else:
            snail_1 = pygame.image.load("assets/snail1.png").convert_alpha()
            snail_2 = pygame.image.load("assets/snail2.png").convert_alpha()
            self.frames = [snail_1, snail_2]
            y_pos = 300

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(random.randint(900, 1100), y_pos))

    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= 6
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()


def display_score():
    # Current
    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    score_surface = test_font.render(f'Score: {current_time}', False, (64, 64, 64))
    score_rectangle = score_surface.get_rect(center=(400, 50))
    screen.blit(score_surface, score_rectangle)

    # Previous
    previous_score_surface = test_font.render(f'Last Score: {previous_score}', False, (64, 64, 64))
    previous_score_rectangle = previous_score_surface.get_rect(midleft=(50, 50))
    screen.blit(previous_score_surface, previous_score_rectangle)

    # Best
    best_score_surface = test_font.render(f'Best Score: {best_score}', False, (64, 64, 64))
    best_score_rectangle = best_score_surface.get_rect(midleft=(50, 100))
    screen.blit(best_score_surface, best_score_rectangle)

    return current_time


def collision_sprite():
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        obstacle_group.empty()
        return False
    else:
        return True


def relu(x):
    # Introduce Non-Linearity, makes it able to learn complex real world patterns
    # Should be applied to each hidden layer as well as the output.
    return np.maximum(0, x)


class NeuralNetwork:
    def __init__(self):
        # Generate random numbers from -1 to 1
        self.input_weights = 2 * np.random.random((1, 4)) - 1  # 1 input to 4 hidden neurons
        print(self.input_weights)

        self.output_weights = 2 * np.random.random((5, 1)) - 1  # (4 hidden neurons + 1 bias) = 5 to 1 output
        print(self.output_weights)

    def forward(self, inputs):
        # Multiply input by 4 input weights and store all 4 results in 4 neurons in the hidden layer
        self.hidden_layer = relu(np.dot(inputs, self.input_weights))
        print("hidden layer:", self.hidden_layer)

        # Store 1 extra value in hidden layer as number 1(bias)
        self.hidden_layer = np.append(self.hidden_layer, 1)
        print("hidden layer with bias:", self.hidden_layer)

        # Multiply all (4 neuron values + bias) by 5 output weights
        # Then sum all 5 values into a single output result
        output_layer = relu(np.dot(self.hidden_layer, self.output_weights))
        print("output layer:", output_layer)
        return output_layer


# Example of using the network
# Initialize the neural network
nn = NeuralNetwork()

pygame.init()
screen = pygame.display.set_mode((800, 400))  # width and height
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()
test_font = pygame.font.Font("assets/Pixeltype.ttf", 50)
game_active = False
start_time = 0
score = 0
previous_score = 0
best_score = 0

# Groups
player = pygame.sprite.GroupSingle()
player.add(Player())
obstacle_group = pygame.sprite.Group()

# Background
sky_surface = pygame.image.load("assets/Sky.png").convert()
ground_surface = pygame.image.load("assets/ground.png").convert()

# Intro screen
player_stand = pygame.image.load("assets/player_stand.png").convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 2)
player_stand_rectangle = player_stand.get_rect(center=(400, 200))

game_name = test_font.render("Pixel Runner", False, (111, 196, 169))
game_name_rectangle = game_name.get_rect(center=(400, 80))

game_message = test_font.render("Press space to run", False, (111, 196, 169))
game_message_rectangle = game_message.get_rect(center=(400, 330))

# Timer
obstacle_timer = pygame.USEREVENT + 1  # avoid conflict with reserved by '+1'
pygame.time.set_timer(obstacle_timer, 1500)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_active:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(["fly", "fly", "snail", "snail", "snail"])))

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
        player.draw(screen)
        player.update()

        # Obstacles
        obstacle_group.draw(screen)
        obstacle_group.update()

        # collision
        game_active = collision_sprite()

        # AI
        # Calculate horizontal distance to the closest obstacle for every frame
        closest_obstacle_distance = min(
            [abs(obstacle.rect.x - player.sprite.rect.x) for obstacle in obstacle_group.sprites()], default=0)

        print(closest_obstacle_distance)

        # horizontal distance to obstacle
        inputs = np.array([closest_obstacle_distance]).reshape(1, -1)

        # Getting the decision from the network (whether to jump or not)
        decision = nn.forward(inputs)

        if decision > 20:
            player.sprite.AI_programmatic_jump()

        print("Decision:", decision)

    else:
        screen.fill((94, 129, 162))
        screen.blit(player_stand, player_stand_rectangle)

        player_gravity = 0
        previous_score = score
        if score > best_score:
            best_score = score

        score_message = test_font.render(f'Your score: {score}', False, (111, 196, 169))
        score_message_rectangle = score_message.get_rect(center=(400, 330))
        screen.blit(game_name, game_name_rectangle)

        if score == 0:
            screen.blit(game_message, game_message_rectangle)
        else:
            screen.blit(score_message, score_message_rectangle)

    pygame.display.update()
    clock.tick(60)  # loop should not run faster than 60x/second
