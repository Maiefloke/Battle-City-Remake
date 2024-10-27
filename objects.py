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
        self.shotDelay = 60
        self.bulletSpeed = 5
        self.bulletDamage = 1

        self.hp = 5
        
        self.keyLEFT = keysList[0]
        self.keyRIGHT = keysList[1]
        self.keyUP = keysList[2]
        self.keyDOWN = keysList[3]
        self.keySHOT = keysList[4]

        self.rank = 0
        self.image = pygame.transform.rotate(imgTanks[self.rank], -self.direct * 90)
        self.rect = self.image.get_rect(center = self.rect.center)


    def update(self):
        self.image = pygame.transform.rotate(imgTanks[self.rank], -self.direct * 90)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() - 5, self.image.get_height() - 5))
        self.rect = self.image.get_rect(center = self.rect.center)

        self.moveSpeed = MOVE_SPEED[self.rank]
        self.bulletDamage = BULLET_DAMAGE[self.rank]
        self.bulletSpeed = BULLET_SPEED[self.rank]
        self.shotDelay = SHOT_DELAY[self.rank]

        keys = pygame.key.get_pressed()
        
        oldX, oldY = self.rect.topleft
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

        if keys[self.keySHOT] and self.shotTimer == 0:
            dx = DIRECTS[self.direct][0] * self.bulletSpeed
            dy = DIRECTS[self.direct][1] * self.bulletSpeed
            Bullet(self, self.rect.centerx, self.rect.centery, dx, dy, self.bulletDamage)
            self.shotTimer = self.shotDelay

        if self.shotTimer > 0: self.shotTimer -= 1

        for obj in objects:
            if obj != self and obj.type == 'block':
                if self.rect.colliderect(obj):
                    self.rect.topleft = oldX, oldY

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
    def __init__(self, player, blocks, spawn_position=None):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("images/tank4.png"), (TILE, TILE))
        self.rect = self.image.get_rect()

        # Спавн ворога на позиції без блоків
        self.rect.center = self.get_valid_spawn_position(blocks) if spawn_position is None else spawn_position

        self.speed = 2
        self.player = player
        self.blocks = blocks
        self.path = []  # Шлях ворога до гравця
        self.shoot_cooldown = 30  # Інтервал часу між пострілами
        self.shoot_timer = 0  # Лічильник часу до наступного пострілу

    def get_valid_spawn_position(self, blocks):
        """Знайти позицію для спавну, яка не перекривається з блоками."""
        attempts = 100  # Кількість спроб
        for _ in range(attempts):
            x = random.randint(0, WIDTH // TILE - 1) * TILE
            y = random.randint(0, HEIGHT // TILE - 1) * TILE
            spawn_rect = pygame.Rect(x, y, TILE, TILE)
            if not any(block.rect.colliderect(spawn_rect) for block in blocks):
                return x, y
        # Якщо не знайшли вільне місце, повертаємось на безпечне місце
        return TILE, TILE  # Початковий кут, де точно немає блоків

    def update(self):
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        # Оновлення шляху до гравця
        if not self.path or random.random() < 0.1:  # Оновлюємо шлях кожні кілька кадрів
            self.path = self.find_path(self.rect.center, self.player.rect.center)

        # Стрільба, якщо гравець видимий
        if self.can_see_player():
            self.shoot()

        # Рух по шляху
        self.move_along_path()

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
            Bullet(self, self.rect.centerx, self.rect.centery, dx, dy, 1)
            self.shoot_timer = self.shoot_cooldown

    def move_along_path(self):
        """Рух по шляху до гравця."""
        if self.path:
            target_pos = self.path[0]
            dx = target_pos[0] - self.rect.centerx
            dy = target_pos[1] - self.rect.centery

            if abs(dx) <= self.speed and abs(dy) <= self.speed:
                self.rect.center = target_pos
                self.path.pop(0)  # Переходимо до наступної точки
            else:
                new_rect = self.rect.copy()
                if abs(dx) > abs(dy):
                    new_rect.x += self.speed if dx > 0 else -self.speed
                else:
                    new_rect.y += self.speed if dy > 0 else -self.speed

                # Перевірка на зіткнення з блоками
                if not any(block.rect.colliderect(new_rect) for block in self.blocks):
                    self.rect = new_rect
                else:
                    # Якщо не вдалося рухатись, обходимо перешкоду
                    new_rect = self.rect.copy()
                    if abs(dx) > abs(dy):
                        new_rect.y += self.speed if dy > 0 else -self.speed
                    else:
                        new_rect.x += self.speed if dx > 0 else -self.speed
                    
                    if not any(block.rect.colliderect(new_rect) for block in self.blocks):
                        self.rect = new_rect

    def find_path(self, start, goal):
        """A* алгоритм для пошуку шляху."""
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        start = (start[0] // TILE * TILE, start[1] // TILE * TILE)
        goal = (goal[0] // TILE * TILE, goal[1] // TILE * TILE)
        open_set = PriorityQueue()
        open_set.put((0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        max_depth = 500

        depth = 0
        while not open_set.empty() and depth < max_depth:
            _, current = open_set.get()
            depth += 1

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
        self.parent = parent
        self.px, self.py = px, py
        self.dx, self.dy = dx, dy
        self.damage = damage

        bullets.append(self)

    def update(self):
        self.px += self.dx
        self.py += self.dy

        if self.px < 0 or self.px > WIDTH or self.py < 0 or self.py > HEIGHT:
            bullets.remove(self)
            try:
                bullets.remove(self)
            except ValueError:
                pass
        else:
            for obj in objects:
                if obj != self.parent and obj.type != 'bang' and obj.type != 'bonus':
                    if obj.rect.collidepoint(self.px, self.py):
                        obj.damage(self.damage)
                        bullets.remove(self)
                        Bang(self.px, self.py)
                        break

    def draw(self):
        pygame.draw.circle(window, 'yellow', (self.px, self.py), 2)

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