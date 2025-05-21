import pygame
import cv2
import numpy as np
import sys
import os
import random
import math

pygame.init()
pygame.mixer.init()

# Tela
WIDTH, HEIGHT = 800, 400
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Game")

clock = pygame.time.Clock()
FPS = 60
WHITE = (255, 255, 255)
GROUND = 300

# Sons
SOUND_JUMP = pygame.mixer.Sound(os.path.join("assets", "sounds", "jump.wav"))
SOUND_HIT = pygame.mixer.Sound(os.path.join("assets", "sounds", "hit.wav"))
SOUND_GAME_OVER = pygame.mixer.Sound(os.path.join("assets", "sounds", "game_over.wav"))

# Funções de efeito OpenCV
def aumentar_brilho(path_img, fator=50):
    img = cv2.imread(path_img, cv2.IMREAD_UNCHANGED)  # Carrega com canal alpha se existir
    
    # Separa os canais de cor e alpha (se existir)
    if img.shape[2] == 4:  # Se tem canal alpha
        b, g, r, a = cv2.split(img)
    else:  # Se não tem canal alpha, cria um totalmente opaco
        b, g, r = cv2.split(img)
        a = np.ones_like(b) * 255
    
    # Converte BGR para HSV para ajustar o brilho
    hsv = cv2.cvtColor(cv2.merge((b, g, r)), cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Aumenta o brilho
    lim = 255 - fator
    v[v > lim] = 255
    v[v <= lim] += fator
    
    # Reconstrói a imagem com alpha
    final_hsv = cv2.merge((h, s, v))
    img_brilho = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    img_brilho = cv2.cvtColor(img_brilho, cv2.COLOR_BGR2RGBA)  # Converte para RGBA
    
    # Restaura o canal alpha original
    if img.shape[2] == 4:
        img_brilho[:, :, 3] = a  # Define o canal alpha original
    
    return pygame.image.frombuffer(img_brilho.tobytes(), img_brilho.shape[1::-1], "RGBA")

def distorcao_onda(path_img, intensidade=5):
    img = cv2.imread(path_img, cv2.IMREAD_UNCHANGED)
    h, w = img.shape[:2]
    map_x = np.zeros((h, w), np.float32)
    map_y = np.zeros((h, w), np.float32)
    for i in range(h):
        for j in range(w):
            map_x[i, j] = j + np.sin(i / 10.0) * intensidade
            map_y[i, j] = i + np.sin(j / 10.0) * intensidade
    distorted = cv2.remap(img, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    distorted = cv2.cvtColor(distorted, cv2.COLOR_BGRA2RGBA)
    return pygame.image.frombuffer(distorted.tobytes(), distorted.shape[1::-1], "RGBA")

def aplicar_efeito_cor(img_surf, fator=100):
     arr = pygame.surfarray.pixels3d(img_surf).copy()
     arr[:,:,0] = np.clip(arr[:,:,0] + fator, 0, 255)
     return pygame.surfarray.make_surface(arr)

# Carregar imagens com efeitos
dino_img = aumentar_brilho("assets/dino.png", fator=70)
dino_img = pygame.transform.scale(dino_img, (60, 60))
cactus_img = distorcao_onda("assets/cactus.png", intensidade=4)
cactus_img = pygame.transform.scale(cactus_img, (40, 60))

# Bird com animação simples (duas imagens)
bird_img1 = aumentar_brilho("assets/bird.png", fator=40)
bird_img2 = aumentar_brilho("assets/bird.png", fator=40)
bird_img1 = pygame.transform.scale(bird_img1, (50, 40))
bird_img2 = pygame.transform.scale(bird_img2, (50, 40))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.life = random.randint(20, 40)
        self.speed = random.uniform(1, 5)
        self.angle = random.uniform(0, math.pi * 2)
        self.decay = random.uniform(0.9, 0.98)
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.speed *= self.decay
        self.size *= self.decay
        self.life -= 1
        
    def draw(self, screen):
        alpha = int(255 * (self.life / 40))
        color = (*self.color, alpha)
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (int(self.size), int(self.size)), int(self.size))
        screen.blit(surf, (self.x - self.size, self.y - self.size))

class Poeira:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 20
        self.radius = 5

    def update(self):
        self.timer -= 1
        self.radius += 0.5
        self.y += 1

    def draw(self):
        alpha = max(0, int(255 * (self.timer / 20)))
        surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (180, 180, 180, alpha), (int(self.radius), int(self.radius)), int(self.radius))
        SCREEN.blit(surf, (self.x - self.radius, self.y - self.radius))

class Dino:
    def __init__(self):
        self.image = dino_img
        self.mask = pygame.mask.from_surface(self.image)
        self.x = 50
        self.y = GROUND - self.image.get_height()
        self.vel_y = 0
        self.jump_force = -15
        self.gravity = 1
        self.is_jumping = False
        self.dano = False
        self.dano_timer = 0
        self.poeira_particles = []

    def update(self, dt):
        self.vel_y += self.gravity * dt
        self.y += self.vel_y * dt
        if self.y >= GROUND - self.image.get_height():
            if self.is_jumping:
                # Poeira ao aterrissar
                for _ in range(5):
                    self.poeira_particles.append(Poeira(self.x + 10 + random.randint(0, 20), GROUND))
            self.y = GROUND - self.image.get_height()
            self.is_jumping = False

        for p in self.poeira_particles[:]:
            p.update()
            if p.timer <= 0:
                self.poeira_particles.remove(p)

        if self.dano:
            self.dano_timer += 1
            if self.dano_timer > FPS * 2:
                self.dano = False
                self.dano_timer = 0

    def jump(self):
        if not self.is_jumping:
            self.vel_y = self.jump_force
            self.is_jumping = True
            SOUND_JUMP.play()

    def draw(self):
        # shadow = pygame.Surface((self.image.get_width(), self.image.get_height()), pygame.SRCALPHA)
        # shadow.fill((0, 0, 0, 50))
        #SCREEN.blit(shadow, (self.x + 5, self.y + 5))

        for p in self.poeira_particles:
            p.draw()

        if self.dano:
            img = aplicar_efeito_cor(self.image, fator=150)
            SCREEN.blit(img, (self.x, self.y))
        else:
            SCREEN.blit(self.image, (self.x, self.y))

class Cactus:
    def __init__(self):
        self.image = cactus_img
        self.x = WIDTH
        self.y = GROUND - self.image.get_height()
        self.speed = 8
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.x -= self.speed * dt
        if self.x < -self.image.get_width():
            self.x = WIDTH + random.randint(200, 600)
            return True
        return False

    def draw(self):
        SCREEN.blit(self.image, (self.x, self.y))

class Bird:
    def __init__(self):
        self.images = [bird_img1, bird_img2]
        self.frame = 0
        self.frame_timer = 0
        self.x = WIDTH
        self.y = GROUND - 150  # voando acima do chão
        self.speed = 6
        self.mask = pygame.mask.from_surface(self.images[0])

    def update(self, dt):
        self.x -= self.speed * dt
        self.frame_timer += 1
        if self.frame_timer > 10:
            self.frame = (self.frame + 1) % len(self.images)
            self.frame_timer = 0
            self.mask = pygame.mask.from_surface(self.images[self.frame])

        if self.x < -self.images[0].get_width():
            self.x = WIDTH + random.randint(300, 700)
            self.y = GROUND - random.randint(130, 180)  # pequena variação de altura

    def draw(self):
        # sombra leve
        # shadow = pygame.Surface((self.images[0].get_width(), self.images[0].get_height()), pygame.SRCALPHA)
        # shadow.fill((0, 0, 0, 50))
        # SCREEN.blit(shadow, (self.x + 3, self.y + 3))

        SCREEN.blit(self.images[self.frame], (self.x, self.y))

def check_collision(dino, cactus):
    offset = (int(cactus.x - dino.x), int(cactus.y - dino.y))
    return dino.mask.overlap(cactus.mask, offset)

def check_collision_bird(dino, bird):
    offset = (int(bird.x - dino.x), int(bird.y - dino.y))
    return dino.mask.overlap(bird.mask, offset)

def piscar_tela(tela, cor=(255, 0, 0), velocidade=10):
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(cor)
    for alpha in list(range(0, 255, velocidade)) + list(range(255, 0, -velocidade)):
        fade_surface.set_alpha(alpha)
        tela.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)

class GameOverEffect:
    def __init__(self):
        self.particles = []
        self.timer = 0
        self.max_time = 120  # 2 segundos a 60 FPS
        self.shake_intensity = 0
        self.color_shift = 0
        
    def create_explosion(self, x, y):
        colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (255, 69, 0)]
        for _ in range(50):
            color = random.choice(colors)
            self.particles.append(Particle(x, y, color))
            
    def update(self):
        self.timer += 1
        self.shake_intensity = max(0, 10 - (self.timer / 12))
        self.color_shift = (self.color_shift + 2) % 360
        
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)
                
    def draw(self, screen):
        # Aplicar efeito de shake
        shake_x = random.uniform(-self.shake_intensity, self.shake_intensity)
        shake_y = random.uniform(-self.shake_intensity, self.shake_intensity)
        
        # Desenhar partículas
        for p in self.particles:
            p.draw(screen)
            
        # Efeito de cor na tela inteira
        if self.timer < self.max_time:
            hue = self.color_shift
            sat = 100
            val = 100
            hsv_color = pygame.Color(0, 0, 0)
            hsv_color.hsva = (hue, sat, val, 20)  # 20% de opacidade
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill(hsv_color)
            screen.blit(overlay, (shake_x, shake_y))
            
        return (shake_x, shake_y)

def draw_text_with_outline(text, font, x, y, color, outline_color, outline_size=2):
    # Renderiza o texto com contorno
    text_surface = font.render(text, True, outline_color)
    for dx in range(-outline_size, outline_size+1):
        for dy in range(-outline_size, outline_size+1):
            if dx != 0 or dy != 0:
                SCREEN.blit(text_surface, (x + dx, y + dy))
    
    # Renderiza o texto principal
    text_surface = font.render(text, True, color)
    SCREEN.blit(text_surface, (x, y))

def main():
    dino = Dino()
    cactus = Cactus()
    bird = Bird()
    score = 0
    running = True
    game_over = False
    hit_played = False
    slow_motion = False
    slow_motion_timer = 0
    game_over_effect = None
    shake_offset = (0, 0)
    
    # Efeito de vignette
    vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(vignette, (0, 0, 0, 0), (WIDTH//2, HEIGHT//2), WIDTH//2)
    pygame.draw.circle(vignette, (0, 0, 0, 150), (WIDTH//2, HEIGHT//2), WIDTH)

    while running:
        dt = 1.075  # Delta time normal
        
        # Slow motion quando o jogo está acabando
        if slow_motion:
            dt = 0.3  # Diminui a velocidade do jogo
            slow_motion_timer += 1
            if slow_motion_timer > 30:  # 0.5 segundos de slow motion
                game_over = True
                slow_motion = False
                if not hit_played:
                    SOUND_HIT.play()
                    SOUND_GAME_OVER.play()
                    game_over_effect = GameOverEffect()
                    game_over_effect.create_explosion(dino.x + dino.image.get_width()//2, 
                                                    dino.y + dino.image.get_height()//2)
                    hit_played = True

        clock.tick(FPS)
        SCREEN.fill((48, 127 ,124))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if not game_over and event.key == pygame.K_SPACE:
                    dino.jump()
                if game_over and event.key == pygame.K_r:
                    main()
                    return

        if not game_over and not slow_motion:
            dino.update(dt)
            passed = cactus.update(dt)
            bird.update(dt)

            if passed:
                score += 1

            if (check_collision(dino, cactus) or check_collision_bird(dino, bird)) and not slow_motion:
                slow_motion = True
                dino.dano = True

        elif game_over:
            if game_over_effect:
                game_over_effect.update()
                shake_offset = game_over_effect.draw(SCREEN)

        # Desenhar elementos do jogo com offset de shake
        dino.draw()
        cactus.draw()
        bird.draw()

        # Score
        font = pygame.font.SysFont("Arial", 30)
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        SCREEN.blit(score_text, (10 + shake_offset[0], 10 + shake_offset[1]))

        if game_over:
            # Texto de game over com efeitos
            game_over_font = pygame.font.SysFont("Arial", 40, bold=True)
            
            # Cor intermitente
            color_value = (pygame.time.get_ticks() // 100) % 255
            color = (255, color_value, color_value)
            
            # Texto principal
            msg = game_over_font.render("GAME OVER", True, color)
            msg_x = WIDTH // 2 - msg.get_width() // 2 + shake_offset[0]
            msg_y = HEIGHT // 2 - 50 + shake_offset[1]
            
            # Texto com contorno
            draw_text_with_outline("GAME OVER", game_over_font, msg_x, msg_y, color, (0, 0, 0))
            
            # Instruções para reiniciar
            restart_font = pygame.font.SysFont("Arial", 20)
            restart_text = restart_font.render("Pressione R para reiniciar", True, (255, 255, 255))
            restart_x = WIDTH // 2 - restart_text.get_width() // 2 + shake_offset[0]
            restart_y = HEIGHT // 2 + 20 + shake_offset[1]
            
            # Fundo para o texto de reiniciar
            pygame.draw.rect(SCREEN, (0, 0, 0, 150), 
                           (restart_x - 10, restart_y - 5, 
                            restart_text.get_width() + 20, 
                            restart_text.get_height() + 10))
            
            SCREEN.blit(restart_text, (restart_x, restart_y))

        # Aplicar vignette
        SCREEN.blit(vignette, (0, 0))

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()