import pygame
from random import randint
import random
from pygame import mixer
from queue import PriorityQueue

mixer.init()
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

imgBonuses = [
    pygame.image.load('images/bonus_star.png'),
    pygame.image.load('images/bonus_tank.png'),
    ]

DIRECTS = [[0, -1], [1, 0], [0, 1], [-1, 0]]

MOVE_SPEED =    [1, 2, 2, 1, 2, 3, 3, 2]
BULLET_SPEED =  [4, 5, 6, 5, 5, 5, 6, 7]
BULLET_DAMAGE = [1, 1, 2, 3, 2, 2, 3, 4]
SHOT_DELAY =    [60, 50, 30, 40, 30, 25, 25, 30]

bullets = []
objects = []
blocks = []
enemys = []