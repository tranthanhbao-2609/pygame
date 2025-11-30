import pygame, sys, random
from database import load_or_create_player, update_player_score, get_highest_score
from ai import AIPlayer

# -------------------- PIPE CLASS (LEVEL 2: 50% ỐNG DI CHUYỂN) --------------------
class Pipe:
    def __init__(self, x, y, level, pipe_gap, pipe_surface):
        self.level = level
        self.pipe_surface = pipe_surface
        self.gap = pipe_gap

        # rect của pipe
        self.bottom_rect = pipe_surface.get_rect(midtop=(x, y))
        self.top_rect = pipe_surface.get_rect(midbottom=(x, y - pipe_gap))

        # chỉ màn 2: ~50% ống di chuyển nhẹ
        if level == 2 and random.random() < 0.5:
            self.speed = random.choice([1, -1])
            self.is_moving = True
            self.limit_top = self.bottom_rect.centery - 45
            self.limit_bottom = self.bottom_rect.centery + 45
        else:
            self.is_moving = False

    def move(self):
        self.bottom_rect.centerx -= 4
        self.top_rect.centerx -= 4

        if self.is_moving and self.level == 2:
            self.bottom_rect.centery += self.speed
            self.top_rect.centery += self.speed
            if self.bottom_rect.centery < self.limit_top or self.bottom_rect.centery > self.limit_bottom:
                self.speed *= -1

    def draw(self, screen):
        screen.blit(self.pipe_surface, self.bottom_rect)
        flip_pipe = pygame.transform.flip(self.pipe_surface, False, True)
        screen.blit(flip_pipe, self.top_rect)

    def off_screen(self):
        return self.bottom_rect.right < -50

# -------------------- OBSTACLE CLASS (LEVEL 3) --------------------
class Obstacle:
    def __init__(self, x, y, surface):
        self.surface = surface
        self.rect = surface.get_rect(center=(x, y))
        self.speed = random.randint(3, 5)

    def move(self):
        self.rect.centerx -= self.speed

    def draw(self, screen):
        screen.blit(self.surface, self.rect)

    def off_screen(self):
        return self.rect.right < -50

# -------------------- HÀM HỖ TRỢ CHUNG --------------------
def create_pipe(level):
    random_pipe_pos = random.choice(pipe_height)
    return Pipe(500, random_pipe_pos, level, pipe_gap, pipe_surface)

def move_pipes(pipes):
    for pipe in pipes:
        pipe.move()
    return [pipe for pipe in pipes if not pipe.off_screen()]

def draw_pipes(pipes, screen):
    for pipe in pipes:
        pipe.draw(screen)

def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe.bottom_rect) or bird_rect.colliderect(pipe.top_rect):
            hit_sound.play()
            return False
    if bird_rect.top <= -75 or bird_rect.bottom >= 650:
        hit_sound.play()
        return False
    return True

def draw_floor():
    screen.blit(floor, (floor_x_pos, 650))
    screen.blit(floor, (floor_x_pos + 432, 650))

def rotate_bird(bird1, movement):
    return pygame.transform.rotozoom(bird1, -movement * 3, 1)

def bird_animation():
    new_bird = bird_list[bird_index]
    new_bird_rect = new_bird.get_rect(center=(100, bird_rect.centery))
    return new_bird, new_bird_rect

# -------------------- OBSTACLE (LEVEL 3) - ÍT --------------------
# -------------------- OBSTACLE (LEVEL 3) - ÍT HƠN --------------------
def spawn_obstacle():
    # Độ khó tăng theo điểm
    if score < 6:
        max_obs = 1
        chance = 8     # 0.8%
    elif score < 13:
        max_obs = 3
        chance = 15    # 1.5%
    elif score < 20:
        max_obs = 5
        chance = 30    # 3%
    else:
        max_obs = random.randint(7, 10)   # nhiều cực mạnh
        chance = random.randint(50, 70)   # 5% → 7% spawn liên tục

    # Khi chưa chạm số lượng tối đa mới được tạo thêm quái
    if len(obstacle_list) < max_obs and random.randint(0, 1000) < chance:
        # tạo quái lệch vị trí để không đứng thành hàng chặn hết
        base = random.randint(250, 490)
        y_pos = base + random.randint(-40, 40)   # cho dao động tự nhiên

        obstacle_list.append(Obstacle(520, y_pos, obstacle_surface))





def move_obstacle():
    for obs in obstacle_list:
        obs.move()
    return [o for o in obstacle_list if not o.off_screen()]

def draw_obstacle():
    for obs in obstacle_list:
        obs.draw(screen)

def check_obstacle_collision():
    for obs in obstacle_list:
        if bird_rect.colliderect(obs.rect):
            hit_sound.play()
            return False
    return True

# -------------------- HIỂN THỊ ĐIỂM / TOP --------------------
def score_display(game_state):
    score_surface = game_font.render(f'{player_name}: {int(score)}', True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(216, 100))
    screen.blit(score_surface, score_rect)

    top_score = get_highest_score()
    top_surface = game_font.render(f'Top: {top_score}', True, (255, 200, 0))
    screen.blit(top_surface, (10, 10))

    if game_state != 'main game':
        high_surface = game_font.render(f'Best: {high_score}', True, (255, 255, 255))
        high_rect = high_surface.get_rect(center=(216, 630))
        screen.blit(high_surface, high_rect)

    ai_color = (100, 255, 100) if ai_player.alive else (120, 120, 120)
    ai_score_surface = game_font.render(f'AI: {int(ai_player.score)}', True, ai_color)
    ai_score_rect = ai_score_surface.get_rect(center=(350, 100))
    screen.blit(ai_score_surface, ai_score_rect)

# -------------------- INIT PYGAME --------------------
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
screen = pygame.display.set_mode((432, 768))
clock = pygame.time.Clock()
game_font = pygame.font.Font('04B_19.ttf', 35)

# -------------------- NHẬP TÊN NGƯỜI CHƠI --------------------
player_name = ""
input_active = True
input_font = pygame.font.Font('04B_19.ttf', 40)
input_rect = pygame.Rect(66, 350, 300, 50)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False

while input_active:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            active = input_rect.collidepoint(event.pos)
            color = color_active if active else color_inactive
        if event.type == pygame.KEYDOWN and active:
            if event.key == pygame.K_RETURN:
                player_name = player_name.strip() or "Player"
                input_active = False
            elif event.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]
            else:
                if len(player_name) < 12:
                    player_name += event.unicode

    screen.fill((0, 0, 0))
    txt_surface = input_font.render(player_name, True, (255, 255, 255))
    input_rect.w = max(300, txt_surface.get_width() + 10)
    screen.blit(txt_surface, (input_rect.x + 5, input_rect.y + 5))
    pygame.draw.rect(screen, color, input_rect, 2)
    info_surface = game_font.render("Enter your name:", True, (255, 255, 255))
    info_rect = info_surface.get_rect(center=(216, 300))
    screen.blit(info_surface, info_rect)
    pygame.display.flip()
    clock.tick(30)

player_data = load_or_create_player(player_name)
high_score = player_data.get("best_score", 0)

# -------------------- INIT AI --------------------
ai_player = AIPlayer(x_pos=250, y_pos=384, pipe_gap=180)
ai_passed_pipes = []

# -------------------- GAME VARIABLES --------------------
gravity = 0.4
bird_movement = 0
game_active = True
score = 0
passed_pipes = []

current_level = 1
pipe_list = []
pipe_height = [250, 300, 350, 400]
pipe_gap = 180

# -------------------- LOAD ASSETS --------------------
bg = pygame.transform.scale2x(pygame.image.load('assets/background-night.png').convert())
floor = pygame.transform.scale2x(pygame.image.load('assets/floor.png').convert())

bird_down = pygame.transform.scale2x(pygame.image.load('assets/yellowbird-downflap.png').convert_alpha())
bird_mid = pygame.transform.scale2x(pygame.image.load('assets/yellowbird-midflap.png').convert_alpha())
bird_up = pygame.transform.scale2x(pygame.image.load('assets/yellowbird-upflap.png').convert_alpha())
bird_list = [bird_down, bird_mid, bird_up]
bird_index = 0
bird = bird_list[bird_index]
bird_rect = bird.get_rect(center=(100, 384))

# AI bird
ai_bird_list = [bird_down.copy(), bird_mid.copy(), bird_up.copy()]
for img in ai_bird_list:
    overlay = pygame.Surface(img.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 255, 0, 90))
    img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
ai_bird = ai_bird_list[0]
ai_bird_index = 0

pipe_surface = pygame.transform.scale2x(pygame.image.load('assets/pipe-green.png').convert())
game_over_surface = pygame.transform.scale2x(pygame.image.load('assets/message.png').convert_alpha())
game_over_rect = game_over_surface.get_rect(center=(216, 384))

flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
hit_sound = pygame.mixer.Sound('sound/sfx_hit.wav')
score_sound = pygame.mixer.Sound('sound/sfx_point.wav')

# Obstacle image
enemy_img = pygame.image.load('assets/enemy.png').convert_alpha()
obstacle_surface = pygame.transform.scale(enemy_img, (45, 45))
obstacle_list = []

# -------------------- TIMERS --------------------
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1400)
BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP, 200)

floor_x_pos = 0

# -------------------- GAME LOOP --------------------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = -8
                flap_sound.play()
            if event.key == pygame.K_SPACE and not game_active:
                game_active = True
                pipe_list.clear()
                passed_pipes.clear()
                bird_rect.center = (100, 384)
                bird_movement = 0
                score = 0
                ai_passed_pipes.clear()
                ai_player.reset(250, 384)
                obstacle_list.clear()
                current_level = 1
        if event.type == SPAWNPIPE:
            pipe_list.append(create_pipe(current_level))
        if event.type == BIRDFLAP:
            bird_index = (bird_index + 1) % 3
            bird, bird_rect = bird_animation()
            ai_bird_index = (ai_bird_index + 1) % 3
            ai_bird = ai_bird_list[ai_bird_index]

    screen.blit(bg, (0, 0))

    if game_active:
        bird_movement += gravity
        bird_rect.centery += bird_movement
        rotated_bird = rotate_bird(bird, bird_movement)

        game_active = check_collision(pipe_list)

        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list, screen)

        for pipe in pipe_list:
            if pipe.bottom_rect.centerx < 100 and pipe not in passed_pipes:
                score += 1
                passed_pipes.append(pipe)
                score_sound.play()

        # AI logic
        if ai_player.alive:
            current_time = pygame.time.get_ticks()
            if ai_player.should_jump(pipe_list, current_time):
                ai_player.jump()
            ai_player.update_movement(gravity)
            ai_player.check_collision(pipe_list)
            for pipe in pipe_list:
                if pipe.bottom_rect.centerx < ai_player.bird_rect.centerx and pipe not in ai_passed_pipes:
                    ai_player.increment_score()
                    ai_passed_pipes.append(pipe)
            rotated_ai = rotate_bird(ai_bird, ai_player.bird_movement)
            screen.blit(rotated_ai, ai_player.bird_rect)

        # LEVEL 3: obstacles ít
        if current_level == 3:
            spawn_obstacle()
            obstacle_list = move_obstacle()
            draw_obstacle()
            game_active = game_active and check_obstacle_collision()

        score_display('main game')

        if score >= 3 and current_level == 1:
            current_level = 2
            pipe_list.clear()
        elif score >= 6 and current_level == 2:
            current_level = 3
            pipe_list.clear()
            obstacle_list.clear()

    else:
        screen.blit(game_over_surface, game_over_rect)
        high_score = update_player_score(player_name, score)
        score_display('game_over')

    floor_x_pos -= 1
    draw_floor()
    if floor_x_pos <= -432:
        floor_x_pos = 0

    screen.blit(rotated_bird, bird_rect)
    pygame.display.update()
    clock.tick(60)
