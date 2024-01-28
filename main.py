import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((800, 400))  # width and height
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()
test_font = pygame.font.Font("assets/Pixeltype.ttf", 50)

# Background
sky_surface = pygame.image.load("assets/Sky.png").convert()
ground_surface = pygame.image.load("assets/ground.png").convert()
text_surface = test_font.render("My Game", False, "Black")

# snail
snail_surface = pygame.image.load("assets/snail1.png").convert_alpha()
snail_rectangle = snail_surface.get_rect(midbottom=(600, 300))

# player
player_surface = pygame.image.load("assets/player_walk_1.png").convert_alpha()
player_rectangle = player_surface.get_rect(midbottom=(80, 300))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        #if event.type == pygame.MOUSEMOTION:
        #    if player_rectangle.collidepoint(event.pos):print("collision")


    screen.blit(sky_surface, (0, 0))
    screen.blit(ground_surface, (0, 300))
    screen.blit(text_surface, (300, 50))

    snail_rectangle.x -= 4
    if snail_rectangle.right <= 0: snail_rectangle.left = 800
    screen.blit(snail_surface, snail_rectangle)
    screen.blit(player_surface, player_rectangle)

    #if player_rectangle.colliderect(snail_rectangle):
    #    print("collision")

    #mouse_pos = pygame.mouse.get_pos()
    #if player_rectangle.collidepoint(mouse_pos):
    #    print(pygame.mouse.get_pressed())

    pygame.display.update()
    clock.tick(60)  # loop should not run faster than 60x/second
