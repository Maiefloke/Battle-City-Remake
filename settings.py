import pygame
from random import randint
from pygame import mixer

mixer.init()
pygame.init()

WIDTH = 900
HEIGHT = 600

FPS = 60
TILE = 32
GO = False

window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

fontUI = pygame.font.Font(None, 30)

imgBrick = pygame.image.load('images/block_brick.png')
background_menu = pygame.transform.scale(pygame.image.load('images/main_screen.png'), (WIDTH, HEIGHT))
background_pause = pygame.transform.scale(pygame.image.load('images/background_pause.png'), (WIDTH, HEIGHT))

mixer.music.load('sounds/main_song.mp3')

shot_sound = mixer.Sound("sounds/shot.wav")

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
