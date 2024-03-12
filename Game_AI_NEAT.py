import copy
import random
import pygame
from sys import exit
from random import choice
import neat
import os

start_time = 0
generation = 0


class Player(pygame.sprite.Sprite):
    def __init__(self, neural_network, genome):
        super().__init__()
        player_walk_1 = pygame.image.load("assets/player_walk_1.png").convert_alpha()
        player_walk_2 = pygame.image.load("assets/player_walk_2.png").convert_alpha()
        self.player_walk = [player_walk_1, player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load("assets/jump.png").convert_alpha()

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(random.randint(20, 150), 300))
        self.gravity = 0

        self.neural_network = neural_network
        self.genome = genome

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
            self.gravity = -20

    def AI_programmatic_jump(self):
        if self.rect.bottom >= 300:  # Check if the player is on the ground
            self.gravity = -20

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
        self.obstacle_type = obstacle_type

        if self.obstacle_type == "fly":
            fly_1 = pygame.image.load("assets/Fly1.png").convert_alpha()
            fly_2 = pygame.image.load("assets/Fly2.png").convert_alpha()
            self.frames = [fly_1, fly_2]
            self.y_pos = 150

        elif self.obstacle_type == "snail":
            snail_1 = pygame.image.load("assets/snail1.png").convert_alpha()
            snail_2 = pygame.image.load("assets/snail2.png").convert_alpha()
            self.frames = [snail_1, snail_2]
            self.y_pos = 300

        elif self.obstacle_type == "coin":
            coin_1 = pygame.image.load("assets/Gold1.png").convert_alpha()
            coin_2 = pygame.image.load("assets/Gold2.png").convert_alpha()
            coin_3 = pygame.image.load("assets/Gold3.png").convert_alpha()
            coin_4 = pygame.image.load("assets/Gold4.png").convert_alpha()
            self.frames = [coin_1, coin_2, coin_3, coin_4]
            self.y_pos = choice([150, 300])
            self.collected_by = set()  # Track players who have collected this coin

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(random.randint(900, 1100), self.y_pos))

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
        if self.rect.x <= -50:
            self.kill()


def main(genomes, config):
    global start_time
    global generation

    # display current score on the game screen
    def display_info():
        # Current
        current_time = int(pygame.time.get_ticks() / 1000) - start_time
        score_surface = test_font.render(f'Score: {current_time}', False, (64, 64, 64))
        score_rectangle = score_surface.get_rect(center=(600, 50))
        screen.blit(score_surface, score_rectangle)

        # Display generation
        score_surface = test_font.render(f'Generation: {generation}', False, (64, 64, 64))
        score_rectangle = score_surface.get_rect(center=(200, 50))
        screen.blit(score_surface, score_rectangle)

        return current_time

    def collision_sprite(player):
        collided_sprites = pygame.sprite.spritecollide(player.sprite, obstacle_group, False)

        for obstacle in collided_sprites:
            if obstacle.obstacle_type == "coin":
                if player not in obstacle.collected_by:
                    obstacle.collected_by.add(player)  # Assure player only collects reward once
                    player.sprite.genome.fitness += 10  # Reward the player
                # Do not kill the coin, let it be collected by others
            else:
                # Handle other obstacle types fly, snail)
                player.sprite.genome.fitness -= 3
                player.sprite.kill()
                players_list.remove(player)  # Remove the player from the game
                break  # Exit the loop because player is dead and other collision doesn't matter

    # start pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 400))  # width and height
    pygame.display.set_caption("My Game")
    clock = pygame.time.Clock()
    test_font = pygame.font.Font("assets/Pixeltype.ttf", 50)
    game_active = True
    max_distance_x = 1000
    threshold = 0.5

    # start list of players
    players_list = []

    # create all NEAT individuals
    # for each (gID & genome obj) in genomes TUPLE list
    for _, genome in genomes:
        # create this neural network using genome and config
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        # initiate fitness of this genome obj as 0
        genome.fitness = 0

        # create player object passing this net and genome as arguments
        player = Player(net, genome)
        # create a sprite group single with this player
        players_group = pygame.sprite.GroupSingle(player)
        # add this player sprite group to list of players
        players_list.append(players_group)

    # Groups
    obstacle_group = pygame.sprite.Group()

    # Background
    sky_surface = pygame.image.load("assets/Sky.png").convert()
    ground_surface = pygame.image.load("assets/ground.png").convert()

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
                    obstacle_group.add(Obstacle(choice(["coin", "fly", "fly", "snail", "snail", "snail"])))

        if game_active:
            # Background
            screen.blit(sky_surface, (0, 0))
            screen.blit(ground_surface, (0, 300))
            display_info()

            # Player
            for player in players_list:
                player.draw(screen)
                player.update()
                # increase fitness while the player is alive
                player.sprite.genome.fitness += 0.018

            # Obstacles
            obstacle_group.draw(screen)
            obstacle_group.update()

            # Inside the game loop
            for player in players_list:
                # Check for collisions with coins or enemies
                collision_sprite(player)

            # AI
            # Calculate horizontal distance to the closest obstacle in front of the player for every frame
            for player in players_list:
                # Extract obstacles that are ahead of the player
                obstacles_ahead = [(obstacle, obstacle.rect.x - player.sprite.rect.x) for obstacle in
                                   obstacle_group.sprites() if obstacle.rect.x > player.sprite.rect.x]

                # Sort obstacles by their distance from the player (ascending order)
                obstacles_ahead.sort(key=lambda x: x[1])

                if obstacles_ahead:
                    # Start categorical features
                    isEnemy = 0
                    isCoin = 0
                    isHigh = 0
                    isLow = 0

                    # Get the closest obstacle and its distances
                    closest_obstacle, closest_obstacle_distance_x = obstacles_ahead[0]

                    # Normalize the distance to be between 0 and 1
                    # Smaller the distance, higher the value
                    normalized_distance_x = 1 - (closest_obstacle_distance_x / max_distance_x)

                    # check what kind of obstacle
                    if closest_obstacle.obstacle_type == "snail" or closest_obstacle.obstacle_type == "fly":
                        isEnemy = 1
                    elif closest_obstacle.obstacle_type == "coin":
                        isCoin = 1

                    # check where is the obstacle on Y
                    if closest_obstacle.y_pos == 150:
                        isHigh = 1
                    elif closest_obstacle.y_pos == 300:
                        isLow = 1

                    # NEAT input
                    input_to_network = [normalized_distance_x, isEnemy, isCoin, isHigh, isLow]

                    # Run input on network and get output
                    output = player.sprite.neural_network.activate(input_to_network)

                    # print("Distance:", normalized_distance_x)
                    # print("isEnemy:", isEnemy)
                    # print("isCoin:", isCoin)
                    # print("isHigh:", isHigh)
                    # print("isLow:", isLow)
                    print(player.sprite.genome.fitness)

                    if output[0] > threshold:
                        player.sprite.AI_programmatic_jump()
                        player.sprite.genome.fitness -= 0.02

            if len(players_list) == 0:
                start_time = int(pygame.time.get_ticks() / 1000)  # reset timer (score)
                generation += 1  # increase generation
                break

        pygame.display.update()
        clock.tick(60)  # loop should not run faster than 60x/second


def run(config_path):
    # all subheadings from config file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    # initiate population
    p = neat.Population(config)

    # display statistics on console
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)
