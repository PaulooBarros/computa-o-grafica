import pygame
import cv2
import numpy as np
import sys
import os
import random

pygame.init()
pygame.mixer.init()

# Tela
WIDTH, HEIGHT = 800, 400
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino com Efeitos Visuais, Sons e Bird")

clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
GROUND = 300

# Sons
SOUND_JUMP = pygame.mixer.Sound(os.path.join("assets", "sounds", "jump.wav"))
SOUND_HIT = pygame.mixer.Sound(os.path.join("assets", "sounds", "hit.wav"))

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
        shadow = pygame.Surface((self.image.get_width(), self.image.get_height()), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 50))
        SCREEN.blit(shadow, (self.x + 5, self.y + 5))

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
        shadow = pygame.Surface((self.images[0].get_width(), self.images[0].get_height()), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 50))
        SCREEN.blit(shadow, (self.x + 3, self.y + 3))

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

def main():
    dino = Dino()
    cactus = Cactus()
    bird = Bird()
    score = 0
    running = True
    game_over = False
    hit_played = False

    while running:
        clock.tick(FPS)
        SCREEN.fill((240, 240, 240))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if not game_over and event.key == pygame.K_SPACE:
                    dino.jump()
                if game_over and event.key == pygame.K_r:
                    main()
                    return

        if not game_over:
            dino.update(dt=1.075)
            passed = cactus.update(dt=1.075)
            bird.update(dt=1.075)

            if passed:
                score += 1

            if check_collision(dino, cactus) or check_collision_bird(dino, bird):
                dino.dano = True
                if not hit_played:
                    SOUND_HIT.play()
                    piscar_tela(SCREEN, cor=(255, 0, 0), velocidade=15)
                    hit_played = True
                game_over = True

        dino.draw()
        cactus.draw()
        bird.draw()

        # Score
        font = pygame.font.SysFont("Arial", 30)
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        SCREEN.blit(score_text, (10, 10))

        if game_over:
            msg = font.render("GAME OVER - Pressione R para reiniciar", True, (255, 0, 0))
            SCREEN.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
