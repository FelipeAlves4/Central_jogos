import pygame
import sys
import random
import asyncio
import platform
import array
import math
import time

# Inicialização do Pygame
pygame.init()
pygame.mixer.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Central de Jogos")
FPS = 60

# Nova paleta de cores
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_PURPLE = (128, 0, 255)
PASTEL_BLUE = (100, 200, 255)
PASTEL_PINK = (255, 150, 200)
DARK_NAVY = (10, 20, 50)
WHITE = (255, 255, 255)
SHADOW_GRAY = (30, 30, 30)
GLOW_YELLOW = (255, 255, 100)

# Sons gerados com array.array
def create_tone(frequency, duration, sample_rate=44100):
    samples = int(sample_rate * duration)
    data = array.array('h', [0] * samples)
    for i in range(samples):
        t = i / sample_rate
        data[i] = int(32767 * math.sin(2 * math.pi * frequency * t) * math.exp(-t * 3))
    return pygame.mixer.Sound(data)

select_sound = create_tone(1000, 0.1)
point_sound = create_tone(800, 0.05)

# Fontes
title_font = pygame.font.SysFont('Arial', 70, bold=True)
menu_font = pygame.font.SysFont('Arial', 40)
game_font = pygame.font.SysFont('Arial', 30)

# Partículas para o fundo do menu
class Particle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(2, 5)
        self.speed = random.uniform(0.5, 2)
        self.angle = random.uniform(0, 2 * math.pi)
        self.color = random.choice([NEON_CYAN, NEON_MAGENTA, PASTEL_BLUE])

    def move(self, time_elapsed):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.x = random.randint(0, WIDTH)
            self.y = random.randint(0, HEIGHT)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

# Função para criar gradiente
def create_gradient(surface, start_color, end_color, vertical=True):
    if vertical:
        for y in range(surface.get_height()):
            ratio = y / surface.get_height()
            color = tuple(int(start_color[i] + (end_color[i] - start_color[i]) * ratio) for i in range(3))
            pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))
    else:
        for x in range(surface.get_width()):
            ratio = x / surface.get_width()
            color = tuple(int(start_color[i] + (end_color[i] - start_color[i]) * ratio) for i in range(3))
            pygame.draw.line(surface, color, (x, 0), (x, surface.get_height()))

# Menu principal
def draw_menu(selected, time_elapsed, particles):
    # Fundo com gradiente animado
    bg = pygame.Surface((WIDTH, HEIGHT))
    phase = math.sin(time_elapsed * 0.3) * 0.2 + 0.8
    create_gradient(bg, (int(10 * phase), int(20 * phase), int(40 * phase)), (int(30 * phase), int(50 * phase), int(80 * phase)))
    screen.blit(bg, (0, 0))
    
    # Partículas
    for particle in particles:
        particle.move(time_elapsed)
        particle.draw(screen)
    
    # Título com efeito de brilho
    title = title_font.render("Central de Jogos", True, NEON_CYAN)
    title_glow = title_font.render("Central de Jogos", True, GLOW_YELLOW)
    title_glow.set_alpha(int(128 + 127 * math.sin(time_elapsed * 2)))
    screen.blit(title_glow, (WIDTH//2 - title.get_width()//2 + 4, 84))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
    
    # Botões com hover e sombra
    options = ["Snake", "Pong", "Tic-Tac-Toe", "Breakout", "Sair"]
    mouse_pos = pygame.mouse.get_pos()
    for i, option in enumerate(options):
        color = GLOW_YELLOW if i == selected else WHITE
        text = menu_font.render(option, True, color)
        rect = text.get_rect(center=(WIDTH//2, 220 + i*70))
        button_bg = pygame.Surface((rect.width + 40, rect.height + 20), pygame.SRCALPHA)
        hover = rect.collidepoint(mouse_pos)
        create_gradient(button_bg, PASTEL_BLUE if hover else NEON_PURPLE, DARK_NAVY)
        button_bg.set_alpha(200 if hover else 150)
        button_rect = button_bg.get_rect(center=rect.center)
        screen.blit(button_bg, button_rect)
        shadow = menu_font.render(option, True, SHADOW_GRAY)
        screen.blit(shadow, (rect.x + 4, rect.y + 4))
        screen.blit(text, rect)
    
    pygame.display.flip()

async def main_menu():
    selected = 0
    start_time = time.time()
    particles = [Particle() for _ in range(30)]
    while True:
        time_elapsed = time.time() - start_time
        draw_menu(selected, time_elapsed, particles)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % 5
                    select_sound.play()
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % 5
                    select_sound.play()
                if event.key == pygame.K_RETURN:
                    if selected == 0:
                        await snake_game()
                    elif selected == 1:
                        await pong_game()
                    elif selected == 2:
                        await tic_tac_toe_game()
                    elif selected == 3:
                        await breakout_game()
                    elif selected == 4:
                        pygame.quit()
                        sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for i, option in enumerate(["Snake", "Pong", "Tic-Tac-Toe", "Breakout", "Sair"]):
                    rect = menu_font.render(option, True, WHITE).get_rect(center=(WIDTH//2, 220 + i*70))
                    if rect.collidepoint(mouse_pos):
                        selected = i
                        select_sound.play()
                        if i == 0:
                            await snake_game()
                        elif i == 1:
                            await pong_game()
                        elif i == 2:
                            await tic_tac_toe_game()
                        elif i == 3:
                            await breakout_game()
                        elif i == 4:
                            pygame.quit()
                            sys.exit()
        
        await asyncio.sleep(1.0 / FPS)

# Jogo Snake
async def snake_game():
    snake_pos = [[400, 300]]
    snake_dir = [20, 0]
    food_pos = [random.randrange(0, WIDTH, 20), random.randrange(0, HEIGHT, 20)]
    score = 0
    paused = False
    game_over = False
    start_time = time.time()
    
    while True:
        time_elapsed = time.time() - start_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_r and game_over:
                    snake_pos = [[400, 300]]
                    snake_dir = [20, 0]
                    food_pos = [random.randrange(0, WIDTH, 20), random.randrange(0, HEIGHT, 20)]
                    score = 0
                    game_over = False
                    start_time = time.time()
                if not paused and not game_over:
                    if event.key == pygame.K_UP and snake_dir[1] == 0:
                        snake_dir = [0, -20]
                    if event.key == pygame.K_DOWN and snake_dir[1] == 0:
                        snake_dir = [0, 20]
                    if event.key == pygame.K_LEFT and snake_dir[0] == 0:
                        snake_dir = [-20, 0]
                    if event.key == pygame.K_RIGHT and snake_dir[0] == 0:
                        snake_dir = [20, 0]
        
        if not paused and not game_over:
            new_head = [snake_pos[0][0] + snake_dir[0], snake_pos[0][1] + snake_dir[1]]
            snake_pos.insert(0, new_head)
            
            if new_head == food_pos:
                score += 1
                point_sound.play()
                food_pos = [random.randrange(0, WIDTH, 20), random.randrange(0, HEIGHT, 20)]
            else:
                snake_pos.pop()
            
            if (new_head[0] < 0 or new_head[0] >= WIDTH or 
                new_head[1] < 0 or new_head[1] >= HEIGHT or 
                new_head in snake_pos[1:]):
                game_over = True
        
        # Fundo com gradiente
        bg = pygame.Surface((WIDTH, HEIGHT))
        create_gradient(bg, DARK_NAVY, NEON_PURPLE)
        screen.blit(bg, (0, 0))
        
        # Grid com transparência
        grid_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for x in range(0, WIDTH, 20):
            pygame.draw.line(grid_surf, (255, 255, 255, 50), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 20):
            pygame.draw.line(grid_surf, (255, 255, 255, 50), (0, y), (WIDTH, y), 1)
        screen.blit(grid_surf, (0, 0))
        
        # Comida com pulsação
        food_scale = 10 + 5 * math.sin(time_elapsed * 3)
        food_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(food_surf, NEON_MAGENTA, (20, 20), food_scale)
        pygame.draw.circle(food_surf, GLOW_YELLOW, (20, 20), food_scale * 0.5, 2)
        screen.blit(food_surf, (food_pos[0] - 10, food_pos[1] - 10))
        
        # Cobra com gradiente e sombra
        for i, pos in enumerate(snake_pos):
            snake_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            create_gradient(snake_surf, NEON_CYAN, PASTEL_BLUE)
            shadow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, SHADOW_GRAY, (0, 0, 16, 16), border_radius=4)
            screen.blit(shadow_surf, (pos[0] + 4, pos[1] + 4))
            screen.blit(snake_surf, (pos[0], pos[1]))
            if i == 0:  # Cabeça
                pygame.draw.circle(screen, GLOW_YELLOW, (pos[0] + 10, pos[1] + 10), 3)
        
        # HUD com fundo
        hud_bg = pygame.Surface((150, 40), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 150))
        screen.blit(hud_bg, (5, 5))
        score_text = game_font.render(f"Pontos: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        if paused:
            pause_bg = pygame.Surface((400, 100), pygame.SRCALPHA)
            pause_bg.fill((0, 0, 0, 200))
            pause_text = game_font.render("Pausado (P para continuar)", True, GLOW_YELLOW)
            screen.blit(pause_bg, (WIDTH//2 - 200, HEIGHT//2 - 50))
            screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - pause_text.get_height()//2))
        
        if game_over:
            game_over_bg = pygame.Surface((400, 100), pygame.SRCALPHA)
            game_over_bg.fill((0, 0, 0, 200))
            game_over_text = game_font.render("Game Over! (R para reiniciar)", True, NEON_MAGENTA)
            screen.blit(game_over_bg, (WIDTH//2 - 200, HEIGHT//2 - 50))
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - game_over_text.get_height()//2))
        
        pygame.display.flip()
        await asyncio.sleep(1.0 / 10 if not paused else 1.0 / FPS)

# Jogo Pong
async def pong_game():
    paddle1 = pygame.Rect(50, HEIGHT//2 - 50, 20, 100)
    paddle2 = pygame.Rect(WIDTH - 70, HEIGHT//2 - 50, 20, 100)
    ball = pygame.Rect(WIDTH//2 - 10, HEIGHT//2 - 10, 20, 20)
    ball_speed = [7, 7]
    score1 = score2 = 0
    paused = False
    speed_modifier = 1.0
    trail = []
    start_time = time.time()
    
    while True:
        time_elapsed = time.time() - start_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_r:
                    ball.center = (WIDTH//2, HEIGHT//2)
                    ball_speed = [7, 7]
                    score1 = score2 = 0
                    speed_modifier = 1.0
                    trail = []
                    start_time = time.time()
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    speed_modifier += 0.1
                if event.key == pygame.K_MINUS and speed_modifier > 0.5:
                    speed_modifier -= 0.1
        
        if not paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] and paddle1.top > 0:
                paddle1.y -= 8
            if keys[pygame.K_s] and paddle1.bottom < HEIGHT:
                paddle1.y += 8
            if keys[pygame.K_UP] and paddle2.top > 0:
                paddle2.y -= 8
            if keys[pygame.K_DOWN] and paddle2.bottom < HEIGHT:
                paddle2.y += 8
            
            ball.x += ball_speed[0] * speed_modifier
            ball.y += ball_speed[1] * speed_modifier
            trail.append(ball.center)
            if len(trail) > 15:
                trail.pop(0)
            
            if ball.top <= 0 or ball.bottom >= HEIGHT:
                ball_speed[1] = -ball_speed[1]
            
            if ball.colliderect(paddle1) or ball.colliderect(paddle2):
                ball_speed[0] = -ball_speed[0]
                point_sound.play()
            
            if ball.left <= 0:
                score2 += 1
                ball.center = (WIDTH//2, HEIGHT//2)
                ball_speed[0] = 7
                trail = []
            if ball.right >= WIDTH:
                score1 += 1
                ball.center = (WIDTH//2, HEIGHT//2)
                ball_speed[0] = -7
                trail = []
        
        # Fundo com gradiente dinâmico
        bg = pygame.Surface((WIDTH, HEIGHT))
        create_gradient(bg, DARK_NAVY, NEON_PURPLE)
        screen.blit(bg, (0, 0))
        
        # Linhas centrais animadas
        for y in range(0, HEIGHT, 30):
            offset = math.sin(time_elapsed + y * 0.05) * 15
            line_surf = pygame.Surface((10, 20), pygame.SRCALPHA)
            create_gradient(line_surf, NEON_CYAN, PASTEL_BLUE)
            screen.blit(line_surf, (WIDTH//2 - 5 + offset, y))
        
        # Raquetes com gradiente e sombra
        paddle1_surf = pygame.Surface((20, 100), pygame.SRCALPHA)
        create_gradient(paddle1_surf, NEON_CYAN, PASTEL_BLUE)
        paddle1_shadow = pygame.Surface((20, 100), pygame.SRCALPHA)
        paddle1_shadow.fill(SHADOW_GRAY)
        screen.blit(paddle1_shadow, (paddle1.x + 4, paddle1.y + 4))
        screen.blit(paddle1_surf, paddle1.topleft)
        
        paddle2_surf = pygame.Surface((20, 100), pygame.SRCALPHA)
        create_gradient(paddle2_surf, NEON_CYAN, PASTEL_BLUE)
        paddle2_shadow = pygame.Surface((20, 100), pygame.SRCALPHA)
        paddle2_shadow.fill(SHADOW_GRAY)
        screen.blit(paddle2_shadow, (paddle2.x + 4, paddle2.y + 4))
        screen.blit(paddle2_surf, paddle2.topleft)
        
        # Rastro da bola
        for i, pos in enumerate(trail):
            alpha = i / len(trail)
            trail_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (255, 255, 255, int(255 * alpha)), (10, 10), 5 * alpha)
            screen.blit(trail_surf, (pos[0] - 10, pos[1] - 10))
        
        # Bola com brilho
        ball_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(ball_surf, NEON_MAGENTA, (0, 0, 20, 20))
        pygame.draw.circle(ball_surf, GLOW_YELLOW, (10, 10), 5)
        screen.blit(ball_surf, ball.topleft)
        
        # HUD com fundo
        hud_bg = pygame.Surface((150, 40), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 150))
        screen.blit(hud_bg, (WIDTH//2 - 75, 5))
        score_text = game_font.render(f"{score1} : {score2}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 10))
        
        hud_bg = pygame.Surface((200, 40), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 150))
        screen.blit(hud_bg, (5, HEIGHT - 45))
        speed_text = game_font.render(f"Velocidade: {speed_modifier:.1f}x (+/-)", True, WHITE)
        screen.blit(speed_text, (10, HEIGHT - 40))
        
        if paused:
            pause_bg = pygame.Surface((400, 100), pygame.SRCALPHA)
            pause_bg.fill((0, 0, 0, 200))
            pause_text = game_font.render("Pausado (P para continuar)", True, GLOW_YELLOW)
            screen.blit(pause_bg, (WIDTH//2 - 200, HEIGHT//2 - 50))
            screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - pause_text.get_height()//2))
        
        pygame.display.flip()
        await asyncio.sleep(1.0 / FPS)

# Jogo Tic-Tac-Toe
async def tic_tac_toe_game():
    board = [[None for _ in range(3)] for _ in range(3)]
    player = 'X'
    game_over = False
    winner = None
    paused = False
    animations = {}
    start_time = time.time()
    
    def check_winner():
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] and board[i][0]:
                return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] and board[0][i]:
                return board[0][i]
        if board[0][0] == board[1][1] == board[2][2] and board[0][0]:
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] and board[0][2]:
            return board[0][2]
        if all(board[i][j] for i in range(3) for j in range(3)):
            return 'Empate'
        return None
    
    while True:
        time_elapsed = time.time() - start_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_r:
                    board = [[None for _ in range(3)] for _ in range(3)]
                    player = 'X'
                    game_over = False
                    winner = None
                    animations = {}
                    start_time = time.time()
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and not paused:
                x, y = event.pos
                col = (x - 200) // 100
                row = (y - 150) // 100
                if 0 <= row < 3 and 0 <= col < 3 and not board[row][col]:
                    board[row][col] = player
                    animations[(row, col)] = time.time()
                    winner = check_winner()
                    if winner:
                        game_over = True
                    else:
                        player = 'O' if player == 'X' else 'X'
                    point_sound.play()
        
        # Fundo com gradiente
        bg = pygame.Surface((WIDTH, HEIGHT))
        create_gradient(bg, DARK_NAVY, NEON_PURPLE)
        screen.blit(bg, (0, 0))
        
        # Tabuleiro com sombra
        shadow = pygame.Surface((300, 300), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 100))
        screen.blit(shadow, (204, 154))
        tab_surf = pygame.Surface((300, 300), pygame.SRCALPHA)
        create_gradient(tab_surf, PASTEL_BLUE, NEON_CYAN)
        screen.blit(tab_surf, (200, 150))
        
        for i in range(3):
            for j in range(3):
                pygame.draw.rect(screen, WHITE, (200 + j*100, 150 + i*100, 90, 90), 3)
                if board[i][j]:
                    anim_time = animations.get((i, j), start_time)
                    scale = min(1.0, (time.time() - anim_time) * 3)
                    if board[i][j] == 'X':
                        surf = pygame.Surface((80, 80), pygame.SRCALPHA)
                        pygame.draw.line(surf, NEON_MAGENTA, (10, 10), (70, 70), int(7 * scale))
                        pygame.draw.line(surf, NEON_MAGENTA, (70, 10), (10, 70), int(7 * scale))
                        surf = pygame.transform.scale(surf, (80 * scale, 80 * scale))
                        screen.blit(surf, (205 + j*100 + 40 * (1 - scale), 155 + i*100 + 40 * (1 - scale)))
                    elif board[i][j] == 'O':
                        surf = pygame.Surface((80, 80), pygame.SRCALPHA)
                        pygame.draw.circle(surf, NEON_CYAN, (40, 40), 35 * scale, int(7 * scale))
                        surf = pygame.transform.scale(surf, (80 * scale, 80 * scale))
                        screen.blit(surf, (205 + j*100 + 40 * (1 - scale), 155 + i*100 + 40 * (1 - scale)))
        
        # HUD com fundo
        hud_bg = pygame.Surface((400, 40), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 150))
        screen.blit(hud_bg, (WIDTH//2 - 200, 50))
        if game_over:
            if winner == 'Empate':
                text = game_font.render("Empate! (R para reiniciar)", True, GLOW_YELLOW)
            else:
                text = game_font.render(f"{winner} venceu! (R para reiniciar)", True, GLOW_YELLOW)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 55))
        
        if paused:
            pause_bg = pygame.Surface((400, 100), pygame.SRCALPHA)
            pause_bg.fill((0, 0, 0, 200))
            pause_text = game_font.render("Pausado (P para continuar)", True, GLOW_YELLOW)
            screen.blit(pause_bg, (WIDTH//2 - 200, HEIGHT//2 - 50))
            screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - pause_text.get_height()//2))
        
        pygame.display.flip()
        await asyncio.sleep(1.0 / FPS)

# Jogo Breakout
async def breakout_game():
    paddle = pygame.Rect(WIDTH//2 - 50, HEIGHT - 50, 100, 20)
    ball = pygame.Rect(WIDTH//2 - 10, HEIGHT//2 - 10, 20, 20)
    ball_speed = [5, -5]
    bricks = [pygame.Rect(50 + i*100, 50 + j*40, 80, 30) for j in range(4) for i in range(7)]
    score = 0
    paused = False
    game_over = False
    start_time = time.time()
    
    while True:
        time_elapsed = time.time() - start_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_r and game_over:
                    paddle = pygame.Rect(WIDTH//2 - 50, HEIGHT - 50, 100, 20)
                    ball = pygame.Rect(WIDTH//2 - 10, HEIGHT//2 - 10, 20, 20)
                    ball_speed = [5, -5]
                    bricks = [pygame.Rect(50 + i*100, 50 + j*40, 80, 30) for j in range(4) for i in range(7)]
                    score = 0
                    game_over = False
                    start_time = time.time()
        
        if not paused and not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and paddle.left > 0:
                paddle.x -= 7
            if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
                paddle.x += 7
            
            ball.x += ball_speed[0]
            ball.y += ball_speed[1]
            
            if ball.left <= 0 or ball.right >= WIDTH:
                ball_speed[0] = -ball_speed[0]
            if ball.top <= 0:
                ball_speed[1] = -ball_speed[1]
            
            if ball.colliderect(paddle):
                ball_speed[1] = -ball_speed[1]
                point_sound.play()
            
            for brick in bricks[:]:
                if ball.colliderect(brick):
                    bricks.remove(brick)
                    ball_speed[1] = -ball_speed[1]
                    score += 10
                    point_sound.play()
                    break
            
            if not bricks:
                game_over = True
                winner = True
            if ball.bottom >= HEIGHT:
                game_over = True
                winner = False
        
        # Fundo com gradiente
        bg = pygame.Surface((WIDTH, HEIGHT))
        create_gradient(bg, DARK_NAVY, NEON_PURPLE)
        screen.blit(bg, (0, 0))
        
        # Raquete com gradiente e sombra
        paddle_surf = pygame.Surface((100, 20), pygame.SRCALPHA)
        create_gradient(paddle_surf, PASTEL_PINK, NEON_MAGENTA, vertical=False)
        paddle_shadow = pygame.Surface((100, 20), pygame.SRCALPHA)
        paddle_shadow.fill(SHADOW_GRAY)
        screen.blit(paddle_shadow, (paddle.x + 4, paddle.y + 4))
        screen.blit(paddle_surf, paddle.topleft)
        
        # Bola com brilho
        ball_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(ball_surf, NEON_CYAN, (0, 0, 20, 20))
        pygame.draw.circle(ball_surf, GLOW_YELLOW, (10, 10), 5)
        screen.blit(ball_surf, ball.topleft)
        
        # Tijolos com gradiente e sombra
        for brick in bricks:
            brick_shadow = pygame.Surface((80, 30), pygame.SRCALPHA)
            brick_shadow.fill(SHADOW_GRAY)
            screen.blit(brick_shadow, (brick.x + 4, brick.y + 4))
            brick_surf = pygame.Surface((80, 30), pygame.SRCALPHA)
            create_gradient(brick_surf, PASTEL_BLUE, NEON_CYAN)
            screen.blit(brick_surf, brick.topleft)
        
        # HUD com fundo
        hud_bg = pygame.Surface((150, 40), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 150))
        screen.blit(hud_bg, (5, 5))
        score_text = game_font.render(f"Pontos: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        if paused:
            pause_bg = pygame.Surface((400, 100), pygame.SRCALPHA)
            pause_bg.fill((0, 0, 0, 200))
            pause_text = game_font.render("Pausado (P para continuar)", True, GLOW_YELLOW)
            screen.blit(pause_bg, (WIDTH//2 - 200, HEIGHT//2 - 50))
            screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - pause_text.get_height()//2))
        
        if game_over:
            game_over_bg = pygame.Surface((400, 100), pygame.SRCALPHA)
            game_over_bg.fill((0, 0, 0, 200))
            if winner:
                text = game_font.render("Você venceu! (R para reiniciar)", True, GLOW_YELLOW)
            else:
                text = game_font.render("Game Over! (R para reiniciar)", True, NEON_MAGENTA)
            screen.blit(game_over_bg, (WIDTH//2 - 200, HEIGHT//2 - 50))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
        
        pygame.display.flip()
        await asyncio.sleep(1.0 / FPS)

# Função principal
async def main():
    await main_menu()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())