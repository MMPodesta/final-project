import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((800, 400))  # width and height
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    # draw all our elements
    # update everything
    pygame.display.update()
    clock.tick(60)  # loop should not run faster than 60x/second

