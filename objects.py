from settings import *

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y, w, h, speed):
        super().__init__()
        self.w = w
        self.h = h
        self.speed = speed
        self.image = pygame.transform.scale(pygame.image.load(image).convert_alpha(), (w, h))
        self.start_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def change_image(self, new_image):
        self.image = pygame.transform.scale(pygame.image.load(new_image).convert_alpha(), (self.w, self.h))
        self.start_image = self.image

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.start_image, angle)
        self.rect = self.image.get_rect(center=(self.rect.centerx, self.rect.centery))

    def draw(self):
        window.blit(self.image, self.rect)
        if self.text_visible:
            rect = self.label.get_rect()
            window.blit(self.label, (self.rect.centerx - rect.width / 2, self.rect.centery + 50))

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class UI:
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self):
        i = 0
        for obj in objects:
            if obj.type == 'tank':
                pygame.draw.rect(window, obj.color, (5 + i * 70, 5, 22, 22))

                text = fontUI.render(str(obj.hp), 1, obj.color)
                rect = text.get_rect(center = (5 + i * 70 + 32, 5 + 11))
                window.blit(text, rect)
                i += 1
                
class Tank:
    def __init__(self, color, px, py, direct, keysList):
        objects.append(self)
        self.type = 'tank'
        
        self.color = color
        self.rect = pygame.Rect(px, py, TILE, TILE)
        self.direct = direct
        self.moveSpeed = 2

        self.shotTimer = 0
        self.shotDelay = 60  # Delay in frames between shots
        self.bulletSpeed = 5
        self.bulletDamage = 1

        self.hp = 30
        
        self.keyLEFT = keysList[0]
        self.keyRIGHT = keysList[1]
        self.keyUP = keysList[2]
        self.keyDOWN = keysList[3]
        self.keySHOT = keysList[4]

        self.rank = 0
        self.image = pygame.transform.rotate(imgTanks[self.rank], -self.direct * 90)
        self.rect = self.image.get_rect(center = self.rect.center)

    def update(self):
        # Update the tank image based on direction
        self.image = pygame.transform.rotate(imgTanks[self.rank], -self.direct * 90)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() - 5, self.image.get_height() - 5))
        self.rect = self.image.get_rect(center = self.rect.center)

        # Update the tank's speed and bullet attributes based on its rank
        self.moveSpeed = MOVE_SPEED[self.rank]
        self.bulletDamage = BULLET_DAMAGE[self.rank]
        self.bulletSpeed = BULLET_SPEED[self.rank]
        self.shotDelay = SHOT_DELAY[self.rank]

        keys = pygame.key.get_pressed()
        
        oldX, oldY = self.rect.topleft
        
        # Movement controls
        if keys[self.keyUP]:
            self.rect.y -= self.moveSpeed
            self.direct = 0
        elif keys[self.keyRIGHT]:
            self.rect.x += self.moveSpeed
            self.direct = 1
        elif keys[self.keyDOWN]:
            self.rect.y += self.moveSpeed
            self.direct = 2
        elif keys[self.keyLEFT]:
            self.rect.x -= self.moveSpeed
            self.direct = 3

        # Shooting logic
        if keys[self.keySHOT] and self.shotTimer == 0:  # If shot button pressed and not in cooldown
            dx = DIRECTS[self.direct][0] * self.bulletSpeed
            dy = DIRECTS[self.direct][1] * self.bulletSpeed
            Bullet(self, self.rect.centerx, self.rect.centery, dx, dy, self.bulletDamage)  # Create a new bullet
            self.shotTimer = self.shotDelay  # Start shot cooldown

        # Decrease shot timer
        if self.shotTimer > 0:
            self.shotTimer -= 1

        # Collision with blocks
        for obj in objects:
            if obj != self and obj.type == 'block':
                if self.rect.colliderect(obj):
                    self.rect.topleft = oldX, oldY  # Reset to old position if collision occurs

        # Boundaries
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > WIDTH - TILE:
            self.rect.x = WIDTH - TILE

        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > HEIGHT - TILE:
            self.rect.y = HEIGHT - TILE

    def draw(self):
        window.blit(self.image, self.rect)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)
            print(self.color, 'is dead')

class Enemy(pygame.sprite.Sprite):

    spawn_timer = 0  # Таймер для спавну ворогів
    spawn_interval = 3000

    def __init__(self, player, blocks):
        super().__init__()
        enemys.append(self)
        self.type = "enemy"
        self.image = pygame.transform.scale(pygame.image.load("images/tank4.png"), (25, 25))
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        self.speed = 1
        self.player = player
        self.blocks = blocks
        self.hp = 1  # Вороги також повинні мати здоров'я
        self.path = []
        self.target_index = 0
        self.shoot_cooldown = 50
        self.shoot_timer = 0

    def damage(self, value):
        self.hp -= value 
        if self.hp <= 0:
            for object in enemys:
                self.kill()  # Видаляємо ворога, якщо його здоров'я стало 0 або менше
                enemys.remove(object)

    @classmethod
    def spawn(cls, player, blocks):
        # Перевіряємо, чи минув інтервал спавну
        current_time = pygame.time.get_ticks()
        if current_time - cls.spawn_timer >= cls.spawn_interval:
            # Спавнимо нового ворога та оновлюємо таймер
            cls(player, blocks)
            cls.spawn_timer = current_time

    def update(self):
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        # Знаходження шляху до гравця
        if not self.path or self.target_index >= len(self.path):
            self.path = self.find_path(self.rect.center, self.player.rect.center)
            self.target_index = 0

        # Рух ворога до наступної точки
        if self.path and self.target_index < len(self.path):
            target_pos = self.path[self.target_index]
            dx = target_pos[0] - self.rect.x
            dy = target_pos[1] - self.rect.y

            # Перевірка, чи досягнуто наступної точки
            if abs(dx) <= self.speed and abs(dy) <= self.speed:
                self.rect.x, self.rect.y = target_pos
                self.target_index += 1  # Перейти до наступної точки шляху
            else:
                # Рух до цільової точки (по горизонталі або вертикалі)
                if abs(dx) > abs(dy):
                    self.rect.x += self.speed if dx > 0 else -self.speed
                else:
                    self.rect.y += self.speed if dy > 0 else -self.speed

        # Стрільба по гравцеві
        if self.can_see_player():
            self.shoot()

        for bullet in bullets:
            if bullet.parent != self and bullet.rect.colliderect(self.rect):
                self.damage(bullet.damage)
                bullets.remove(bullet)
                Bang(self.rect.centerx, self.rect.centery)

    def can_see_player(self):
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            line_to_player = pygame.Rect(min(self.rect.centerx, self.player.rect.centerx),
                                         min(self.rect.centery, self.player.rect.centery),
                                         abs(self.rect.centerx - self.player.rect.centerx) or 1,
                                         abs(self.rect.centery - self.player.rect.centery) or 1)
            if not any(block.rect.colliderect(line_to_player) for block in self.blocks):
                return True
        return False

    def shoot(self):
        if self.shoot_timer == 0:
            dx = self.player.rect.centerx - self.rect.centerx
            dy = self.player.rect.centery - self.rect.centery
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > 0:
                dx, dy = dx / distance * BULLET_SPEED[0], dy / distance * BULLET_SPEED[0]
            Bullet(self, self.rect.centerx, self.rect.centery, dx, dy, 1)  # Передайте аргументи для створення кулі
            self.shoot_timer = self.shoot_cooldown

    def find_path(self, start, goal):
        """A* алгоритм для пошуку шляху до гравця з урахуванням перешкод."""
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        start = (start[0] // TILE * TILE, start[1] // TILE * TILE)
        goal = (goal[0] // TILE * TILE, goal[1] // TILE * TILE)
        open_set = PriorityQueue()
        open_set.put((0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}

        while not open_set.empty():
            _, current = open_set.get()

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for dx, dy in [(TILE, 0), (-TILE, 0), (0, TILE), (0, -TILE)]:
                neighbor = (current[0] + dx, current[1] + dy)
                tentative_g_score = g_score[current] + 1

                if any(block.rect.collidepoint(neighbor) for block in self.blocks):
                    continue

                if neighbor in g_score and tentative_g_score >= g_score[neighbor]:
                    continue

                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                open_set.put((f_score[neighbor], neighbor))

        return []

    def draw(self, window):
        window.blit(self.image, self.rect)

class Bullet:
    def __init__(self, parent, px, py, dx, dy, damage):
        self.parent = parent  # Зберігаємо посилання на танк, який стріляє
        self.px, self.py = px, py  # Початкові координати кулі
        self.dx, self.dy = dx, dy  # Напрямок та швидкість кулі
        self.damage = damage  # Завдані ушкодження

        self.radius = 2  # Радіус кулі для малювання та колізій
        self.rect = pygame.Rect(px - self.radius, py - self.radius, self.radius * 2, self.radius * 2)  # Прямокутник для колізій

        bullets.append(self)  # Додаємо кулю до списку куль

    def update(self):
        # Оновлюємо позицію кулі
        self.px += self.dx
        self.py += self.dy

        # Оновлюємо прямокутник для колізій
        self.rect.topleft = (self.px - self.radius, self.py - self.radius)

        # Перевірка, чи куля виходить за межі екрану
        if self.px < 0 or self.px > WIDTH or self.py < 0 or self.py > HEIGHT:
            bullets.remove(self)  # Видаляємо кулю, якщо вона за межами екрана
        else:
            # Перевірка на колізії з іншими об'єктами
            for obj in objects:
                # Перевірка, чи куля вразила інший об'єкт
                if obj != self.parent and obj.type != 'bang' and obj.type != 'bonus':
                    if obj.rect.colliderect(self.rect):
                        obj.damage(self.damage)  # Наносимо ушкодження
                        bullets.remove(self)  # Видаляємо кулю
                        Bang(self.px, self.py)  # Створюємо ефект вибуху
                        break

    def draw(self):
        # Малюємо кулю на екрані
        pygame.draw.circle(window, 'yellow', (int(self.px), int(self.py)), self.radius)

class Bang:
    def __init__(self, px, py):
        objects.append(self)
        self.type = 'bang'

        self.px, self.py = px, py
        self.frame = 0

    def update(self):
        self.frame += 0.2
        if self.frame >= 3: objects.remove(self)

    def draw(self):
        image = imgBangs[int(self.frame)]
        rect = image.get_rect(center = (self.px, self.py))
        window.blit(image, rect)
    
class Block:
    def __init__(self, px, py, size):
        objects.append(self)
        blocks.append(self)

        self.type = 'block'

        self.rect = pygame.Rect(px, py, size, size)
        self.hp = 1

    def update(self):
        pass

    def draw(self):
        window.blit(imgBrick, self.rect)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0: objects.remove(self)

class Bonus:
    def __init__(self, px, py, bonusNum):
        objects.append(self)
        self.type = 'bonus'

        self.image = imgBonuses[bonusNum]
        self.rect = self.image.get_rect(center = (px, py))

        self.timer = 600
        self.bonusNum = bonusNum

    def update(self):
        if self.timer > 0: self.timer -= 1
        else: objects.remove(self)

        for obj in objects:
            if obj.type == 'tank' and self.rect.colliderect(obj.rect):
                if self.bonusNum == 0:
                    if obj.rank < len(imgTanks) - 1:
                        obj.rank += 1
                        objects.remove(self)
                        break
                elif self.bonusNum == 1:
                    obj.hp += 1
                    objects.remove(self)
                    break

    def draw(self):
        if self.timer % 30 < 15:
            window.blit(self.image, self.rect)