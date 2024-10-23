import pygame
from random import randint

pygame.init()

WIDTH = 900
HEIGHT = 600

FPS = 60
TILE = 32

window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

fontUI = pygame.font.Font(None, 30)

imgBrick = pygame.image.load('images/block_brick.png')

background_menu = pygame.transform.scale(pygame.image.load('images/main_screen.png'), (WIDTH, HEIGHT))

imgTanks = [
    pygame.image.load('images/tank1.png'),
    pygame.image.load('images/tank2.png'),
    pygame.image.load('images/tank3.png'),
    pygame.image.load('images/tank4.png'),
    pygame.image.load('images/tank5.png'),
    pygame.image.load('images/tank6.png'),
    pygame.image.load('images/tank7.png'),
    pygame.image.load('images/tank8.png'),
    ]
imgBangs = [
    pygame.image.load('images/bang1.png'),
    pygame.image.load('images/bang2.png'),
    pygame.image.load('images/bang3.png'),
    ]

DIRECTS = [[0, -1], [1, 0], [0, 1], [-1, 0]]

bullets = []
objects = []