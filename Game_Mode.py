import random
import pygame
from sys import exit
from random import choice


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # walking frames
        player_walk_1 = pygame.image.load("assets/player_walk_1.png").convert_alpha()
        player_walk_2 = pygame.image.load("assets/player_walk_2.png").convert_alpha()
        self.player_walk = [player_walk_1, player_walk_2]
        self.player_index = 0

        # ducking frames
        player_duck_1 = pygame.image.load("assets/duck1.png").convert_alpha()
        player_duck_2 = pygame.image.load("assets/duck2.png").convert_alpha()
        player_duck_3 = pygame.image.load("assets/duck3.png").convert_alpha()
        self.player_duck = [player_duck_1, player_duck_2, player_duck_3]
        self.is_ducking = False
        self.duck_index = 0

        # jump frame
        self.player_jump = pygame.image.load("assets/jump.png").convert_alpha()
        self.gravity = 0
        self.jump_sound = pygame.mixer.Sound("assets/jump.mp3")
        self.jump_sound.set_volume(0.03)

        # set player position
        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(random.randint(20, 150), 300))

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300 and not self.is_ducking:
            self.gravity = -20
            self.jump_sound.play()

        # If 's' is pressed, initiate ducking
        if keys[pygame.K_s] and not self.is_ducking:
            self.start_ducking()

        # if 's' is released, stop ducking
        if not keys[pygame.K_s] and self.is_ducking:
            self.stop_ducking()

    def start_ducking(self):
        self.is_ducking = True
        self.duck_index = 0
        self.rect.height = self.player_duck[2].get_height()  # Adjust the hitbox height

    def stop_ducking(self):
        self.is_ducking = False
        self.rect.height = self.player_walk[0].get_height()  # Reset the hitbox height

    def apply_gravity(self):
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

        elif self.obstacle_type == "water":
            water_1 = pygame.image.load("assets/water1.png").convert_alpha()
            water_2 = pygame.image.load("assets/water2.png").convert_alpha()
            water_3 = pygame.image.load("assets/water3.png").convert_alpha()
            water_4 = pygame.image.load("assets/water4.png").convert_alpha()
            water_5 = pygame.image.load("assets/water5.png").convert_alpha()
            water_6 = pygame.image.load("assets/water6.png").convert_alpha()
            water_7 = pygame.image.load("assets/water7.png").convert_alpha()
            water_8 = pygame.image.load("assets/water8.png").convert_alpha()
            water_9 = pygame.image.load("assets/water9.png").convert_alpha()

            self.frames = [water_1, water_2, water_3, water_4, water_5, water_6, water_7, water_8, water_9]
            self.y_pos = 250

        elif self.obstacle_type == "coin":
            coin_1 = pygame.image.load("assets/Gold1.png").convert_alpha()
            coin_2 = pygame.image.load("assets/Gold2.png").convert_alpha()
            coin_3 = pygame.image.load("assets/Gold3.png").convert_alpha()
            coin_4 = pygame.image.load("assets/Gold4.png").convert_alpha()
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
        self.rect.x -= 6
        self.destroy()

    def destroy(self):
        if self.rect.x <= -250:
            self.kill()


def display_score():
    global collected_coins

    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    total_score = current_time + (collected_coins * 5)  # Combine time-based score with coin collection score
    score_surface = test_font.render(f'Score: {total_score}', False, (64, 64, 64))
    score_rectangle = score_surface.get_rect(center=(400, 50))
    screen.blit(score_surface, score_rectangle)
    return total_score


def collision_sprite():
    global collected_coins
    collided_sprites = pygame.sprite.spritecollide(player.sprite, obstacle_group, False)

    if collided_sprites:
        for obstacle in collided_sprites:
            if obstacle.obstacle_type == "coin":
                if player not in obstacle.collected_by:
                    obstacle.collected_by.add(player)  # Assure player only collects reward once
                    collected_coins += 1
                    print("coin collected")

                return True

            else:
                obstacle_group.empty()
                print("Game Over")
                return False
    else:
        return True


pygame.init()
screen = pygame.display.set_mode((800, 400))  # width and height
pygame.display.set_caption("Normal Game Mode")
clock = pygame.time.Clock()
test_font = pygame.font.Font("assets/Pixeltype.ttf", 50)
game_active = False
start_time = 0
score = 0
collected_coins = 0
bg_music = pygame.mixer.Sound("assets/music.wav")
bg_music.set_volume(0.03)
bg_music.play(loops=-1)

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

game_name = test_font.render("2D Runner", False, (111, 196, 169))
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
        player.draw(screen)
        player.update()

        # Obstacles
        obstacle_group.draw(screen)
        obstacle_group.update()

        # collision
        game_active = collision_sprite()

    else:
        screen.fill((94, 129, 162))
        screen.blit(player_stand, player_stand_rectangle)

        player_gravity = 0
        collected_coins = 0

        score_message = test_font.render(f'Your score: {score}', False, (111, 196, 169))
        score_message_rectangle = score_message.get_rect(center=(400, 330))
        screen.blit(game_name, game_name_rectangle)

        if score == 0:
            screen.blit(game_message, game_message_rectangle)
        else:
            screen.blit(score_message, score_message_rectangle)

    pygame.display.update()
    clock.tick(60)  # loop should not run faster than 60x/second
