from objects import *

player = Tank('blue', 100, 275, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
enemy = Enemy(player, blocks)

btn_start = GameSprite("images/Play_button.png", WIDTH / 2, HEIGHT / 2 + 170, 150, 70, 0)
btn_start_pause = GameSprite("images/Play_button.png", WIDTH / 2, HEIGHT / 2 - 30, 150, 70, 0)
btn_back = GameSprite("images/Backt_button.png", WIDTH / 2, HEIGHT / 2 + 70, 170, 70, 0)
btn_Quit = GameSprite("images/Quit_button.png", WIDTH / 2, HEIGHT / 2 + 170, 250, 90, 0)

fontUI = pygame.font.Font(None, 30)

ui = UI()

for i in range(100):
    while True:
        x = randint(0, WIDTH // TILE - 1) * TILE
        y = randint(1, HEIGHT // TILE - 1) * TILE
        rect = pygame.Rect(x, y, TILE, TILE)
        fined = False
        for obj in objects:
            if rect.colliderect(obj.rect):
                fined = True

        if not fined:
            break

    Block(x, y, TILE)

bonusTimer = 180

game = "menu"
mixer.music.play(-1)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    if game == "game":
        window.fill('black')
        mixer.music.set_volume(0.2)

        if bonusTimer > 0:
            bonusTimer -= 1
        else:
            Bonus(randint(50, WIDTH - 50), randint(50, HEIGHT - 50), randint(0, len(imgBonuses) - 1))
            bonusTimer = randint(120, 240)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game = "pause"

        for enm in enemys:
            enm.update()

        for enm in enemys:
            enm.draw(window)
    
        for bullet in bullets:
            bullet.update()

        for obj in objects:
            obj.update()

        for bullet in bullets:
            bullet.draw()

        for obj in objects:
            obj.draw()

        ui.update()
        ui.draw()
        
        pygame.display.update()
        clock.tick(FPS)

    elif game == "menu":
        window.blit(background_menu, (0, 0))
        mixer.music.set_volume(0.3)

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if btn_start.rect.collidepoint(x, y):
                game = "game"

        btn_start.reset()

        pygame.display.update()
        clock.tick(FPS)

    elif game == "pause":
        window.blit(background_pause, (0, 0))

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if btn_start_pause.rect.collidepoint(x, y):
                game = "game"
            elif btn_back.rect.collidepoint(x, y):
                game = "menu"
            elif btn_Quit.rect.collidepoint(x, y):
                pygame.quit()

        btn_start_pause.reset()
        btn_Quit.reset()
        btn_back.reset()
        pygame.display.update()
        clock.tick(FPS)