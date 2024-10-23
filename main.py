from objects import *

Tank('blue', 100, 275, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))

ui = UI()

for _ in range(100):
    while True:
        x = randint(0, WIDTH // TILE - 1) * TILE
        y = randint(1, HEIGHT // TILE - 1) * TILE
        rect = pygame.Rect(x, y, TILE, TILE)
        fined = False
        for obj in objects:
            if rect.colliderect(obj.rect): fined = True

        if not fined:
            break

    Block(x, y, TILE)

menu = False
play = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    if play:
    
        for bullet in bullets:
            bullet.update()

        for obj in objects:
            obj.update()

        ui.update()

        window.fill('black')

        for bullet in bullets:
            bullet.draw()

        for obj in objects:
            obj.draw()

        ui.draw()
        
        pygame.display.update()
        clock.tick(FPS)

    if menu:
        window.blit(background_menu, (0, 0))

        pygame.display.update()
        clock.tick(FPS)
