import pygame
import random
import math
import time

# Ініціалізація Pygame
pygame.init()

# Параметри вікна (повноекранний режим 1600x900)
WIDTH, HEIGHT = 1600, 900
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("60 Seconds")

# Кольори
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (169, 169, 169)  # Сірий колір фону

# Звуки
pygame.mixer.music.load("background_music.mp3")  # Завантажуємо музику
pygame.mixer.music.set_volume(0.5)  # Встановлюємо гучність
pygame.mixer.music.play(-1, 0.0)  # Відтворюємо музику на зациклення

shoot_sound = pygame.mixer.Sound("shoot_sound.mp3")  # Звук пострілу
game_over_sound = pygame.mixer.Sound("game_over_sound.mp3")  # Звук поразки

# Головні параметри
player_speed = 2  # Зменшена швидкість гравця
bullet_speed = 15  # Збільшена швидкість куль
initial_monster_speed = 1.2  # Збільшена швидкість монстрів
initial_monster_spawn_time = 2000  # Спавн монстрів кожні 2 секунди
final_monster_spawn_time = 500  # Мінімальний час спавну монстрів (0.5 секунди)
monster_speed_increase_factor = 1.5  # Збільшення швидкості монстрів в 1.5 рази
shot_delay = 100  # Затримка між пострілами 100 мс

# Шрифти
font = pygame.font.SysFont("Arial", 24)

# Зображення фону
background_image = pygame.image.load("background.jpg")  # Завантажуємо зображення фону
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Масштабування під розмір вікна

# Клас для гравця
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("player.png")  # Заміна на спрайт гравця
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.health = 10  # Більше здоров'я
        self.last_shot_time = 0  # Час останнього пострілу
        self.alive = True  # Прапор для перевірки, чи живий гравець

    def update(self):
        if not self.alive:  # Якщо гравець мертвий, не оновлюємо його рух
            return
        
        # Отримуємо поточний стан клавіатури
        keys = pygame.key.get_pressed()
        
        # Рух гравця
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= player_speed
        if keys[pygame.K_s] and self.rect.bottom < HEIGHT:
            self.rect.y += player_speed
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= player_speed
        if keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += player_speed

    def shoot(self, target_x, target_y, current_time):
        if current_time - self.last_shot_time >= shot_delay and self.alive:
            bullet = Bullet(self.rect.centerx, self.rect.centery, target_x, target_y)
            all_sprites.add(bullet)
            bullets.add(bullet)
            self.last_shot_time = current_time  # Оновлюємо час останнього пострілу
            shoot_sound.play()  # Відтворюємо звук пострілу

    def die(self):
        self.alive = False  # Встановлюємо гравця мертвим
        game_over_sound.play()  # Звук поразки

# Клас для кулі
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.image.load("bullet.png")  # Заміна на спрайт кулі
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # Розрахунок кута для прицілювання
        dx = target_x - x
        dy = target_y - y
        angle = math.atan2(dy, dx)
        
        self.velocity = [math.cos(angle) * bullet_speed, math.sin(angle) * bullet_speed]

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.kill()

# Клас для монстрів
class Monster(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.image.load("monster.png")  # Заміна на спрайт монстра
        self.rect = self.image.get_rect()

        # Спавнимо монстрів поза межами екрану
        spawn_side = random.choice(["left", "right", "top", "bottom"])
        if spawn_side == "left":
            self.rect.x = -50
            self.rect.y = random.randint(0, HEIGHT)
        elif spawn_side == "right":
            self.rect.x = WIDTH + 50
            self.rect.y = random.randint(0, HEIGHT)
        elif spawn_side == "top":
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = -50
        elif spawn_side == "bottom":
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = HEIGHT + 50
        
        self.speed = speed  # Швидкість монстра

    def update(self):
        if player.alive:
            # Монстри рухаються до центру (гравця)
            angle = math.atan2(player.rect.centery - self.rect.centery, player.rect.centerx - self.rect.centerx)
            self.rect.x += math.cos(angle) * self.speed
            self.rect.y += math.sin(angle) * self.speed

    def die(self):
        self.kill()  # Видаляємо монстра

# Функція для перезапуску гри
def restart_game():
    global player, all_sprites, monsters, bullets, start_time, score, game_over, monster_last_spawn_time, initial_monster_spawn_time

    # Очищаємо всі старі спрайти
    all_sprites = pygame.sprite.Group()  # Перевизначаємо all_sprites
    monsters = pygame.sprite.Group()     # Перевизначаємо monsters
    bullets = pygame.sprite.Group()      # Перевизначаємо bullets

    player = Player()
    all_sprites.add(player)

    start_time = time.time()
    monster_last_spawn_time = pygame.time.get_ticks()

    score = 0
    game_over = False
    initial_monster_spawn_time = 2000  # Початковий час спавну монстрів (2 секунди)

# Ініціалізація об'єктів гри
all_sprites = pygame.sprite.Group()  # Створення групи для всіх спрайтів
monsters = pygame.sprite.Group()     # Створення групи для монстрів
bullets = pygame.sprite.Group()      # Створення групи для куль
restart_game()

# Головний цикл гри
running = True
game_over = False
while running:
    win.fill(WHITE)  # Очищаємо екран (можна також використовувати win.blit(background_image, (0, 0)) для фону)
    win.blit(background_image, (0, 0))  # Встановлюємо фон
    
    # Таймер
    elapsed_time = time.time() - start_time
    remaining_time = max(0, 60 - int(elapsed_time))
    
    # Виведення часу
    time_text = font.render(f"Time: {remaining_time}s", True, WHITE)
    win.blit(time_text, (10, 10))

    # Виведення рахунку
    score_text = font.render(f"Score: {score}", True, WHITE)
    win.blit(score_text, (1510, 10))  # Змінили позицію рахунку

    if remaining_time == 0 and not game_over:
        game_over_text = font.render("You Win!", True, GREEN)
        win.blit(game_over_text, (WIDTH // 2 - 60, HEIGHT // 2))
        pygame.display.update()
        pygame.time.delay(3000)  # Затримка на 3 секунди
        restart_game()  # Перезапуск гри
        continue  # Продовжуємо виконання гри після перезапуску
    
    if game_over:
        game_over_text = font.render("Game Over! Press R to Restart", True, RED)
        win.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))
        pygame.display.update()

    # Обробка подій
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:  # Перезапуск гри після програшу
                restart_game()

    # Оновлення положення гравця
    if not game_over:
        player.update()

    # Визначаємо положення миші для прицілювання
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Стрільба на ліву кнопку миші (ЛКМ)
    current_time = pygame.time.get_ticks()  # Отримуємо поточний час
    if pygame.mouse.get_pressed()[0] and player.alive:  # ЛКМ і тільки якщо гравець живий
        player.shoot(mouse_x, mouse_y, current_time)

    # Оновлення об'єктів
    all_sprites.update()

    # Перевірка на зіткнення з монстрами
    for bullet in bullets:
        hit_monsters = pygame.sprite.spritecollide(bullet, monsters, True)
        if hit_monsters:
            score += 1
            bullet.kill()

    # Якщо гравець стикається з монстром, він вмирає
    if pygame.sprite.spritecollide(player, monsters, True):
        player.die()
        game_over = True

    # Спавнимо монстрів через заданий інтервал
    current_time_ms = pygame.time.get_ticks()
    if current_time_ms - monster_last_spawn_time >= initial_monster_spawn_time:
        monster = Monster(initial_monster_speed)
        all_sprites.add(monster)
        monsters.add(monster)
        monster_last_spawn_time = current_time_ms

    # Плавне зменшення інтервалу спавну монстрів
    if initial_monster_spawn_time > final_monster_spawn_time:
        initial_monster_spawn_time = max(final_monster_spawn_time, initial_monster_spawn_time - 10)

    # Оновлюємо відображення
    all_sprites.draw(win)
    pygame.display.update()

# Завершення гри
pygame.quit()
