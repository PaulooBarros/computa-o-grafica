import pygame
import cv2
import numpy as np
import sys
import os

pygame.init()

# Tela
WIDTH, HEIGHT = 800, 400
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino com Efeitos Visuais")

# Clock
clock = pygame.time.Clock()
FPS = 60

# Cores
WHITE = (255, 255, 255)
GROUND = 300

# Sons
pygame.mixer.init()
JUMP_SOUND = pygame.mixer.Sound("assets/sounds/jump.wav")
HIT_SOUND = pygame.mixer.Sound("assets/sounds/hit.wav")

# Efeitos com OpenCV
def aumentar_brilho(path_img, fator=50):
    img = cv2.imread(path_img, cv2.IMREAD_UNCHANGED)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    lim = 255 - fator
    v[v > lim] = 255
    v[v <= lim] += fator
    final_hsv = cv2.merge((h, s, v))
    img_brilho = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    img_brilho = cv2.cvtColor(img_brilho, cv2.COLOR_BGR2RGBA)
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

# Carregar imagens com efeitos
dino_img = aumentar_brilho("assets/dino.png", fator=70)
dino_img = pygame.transform.scale(dino_img, (60, 60))
cactus_img = distorcao_onda("assets/cactus.png", intensidade=4)
cactus_img = pygame.transform.scale(cactus_img, (40, 60))

# Classe de partículas
class Particle:
    def __init__(self, x, y):
        self.x = x + np.random.randint(-5, 5)
        self.y = y + np.random.randint(0, 10)
        self.vel_x = np.random.uniform(-1.5, 1.5)
        self.vel_y = np.random.uniform(-3, -1)
        self.size = np.random.randint(4, 8)
        self.lifetime = 30
        self.surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.surface.fill((120, 120, 120, 120))

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.2
        self.lifetime -= 1
        if self.size > 0:
            self.size -= 0.1
        self.surface = pygame.transform.scale(self.surface, (int(self.size), int(self.size)))

    def draw(self, tela):
        tela.blit(self.surface, (self.x, self.y))

    def is_alive(self):
        return self.lifetime > 0 and self.size > 0

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

    def update(self):
        self.vel_y += self.gravity
        self.y += self.vel_y
        if self.y >= GROUND - self.image.get_height():
            self.y = GROUND - self.image.get_height()
            self.is_jumping = False

    def jump(self):
        if not self.is_jumping:
            self.vel_y = self.jump_force
            self.is_jumping = True
            JUMP_SOUND.play()

    def draw(self):
        shadow = pygame.Surface((self.image.get_width(), self.image.get_height()), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 50))
        SCREEN.blit(shadow, (self.x + 5, self.y + 5))
        SCREEN.blit(self.image, (self.x, self.y))

    def gerar_particulas(self, lista_particulas):
        for _ in range(5):
            lista_particulas.append(Particle(self.x + 20, self.y + self.image.get_height()))

class Cactus:
    def __init__(self):
        self.image = cactus_img
        self.x = WIDTH
        self.y = GROUND - self.image.get_height()
        self.speed = 8
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.x -= self.speed
        if self.x < -self.image.get_width():
            self.x = WIDTH + np.random.randint(200, 600)
            return True
        return False

    def draw(self):
        SCREEN.blit(self.image, (self.x, self.y))

def check_collision(dino, cactus):
    offset = (int(cactus.x - dino.x), int(cactus.y - dino.y))
    return dino.mask.overlap(cactus.mask, offset)

def fade(tela, cor=(0, 0, 0), velocidade=5):
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(cor)
    for alpha in range(0, 255, velocidade):
        fade_surface.set_alpha(alpha)
        tela.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)

def main():
    dino = Dino()
    cactus = Cactus()
    score = 0
    running = True
    game_over = False
    particles = []
    tocou_chao = False

    while running:
        clock.tick(FPS)
        SCREEN.fill((240, 240, 240))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if not game_over and event.key == pygame.K_SPACE:
                    dino.jump()
                    dino.gerar_particulas(particles)
                if game_over and event.key == pygame.K_r:
                    fade(SCREEN, cor=(0, 0, 0))
                    main()
                    return

        if not game_over:
            dino.update()
            passed = cactus.update()
            if passed:
                score += 1

            if check_collision(dino, cactus):
                HIT_SOUND.play()
                game_over = True
                fade(SCREEN, cor=(255, 0, 0), velocidade=10)

        # Efeito de poeira ao aterrissar
        if dino.y >= GROUND - dino.image.get_height():
            if not tocou_chao:
                dino.gerar_particulas(particles)
                tocou_chao = True
        else:
            tocou_chao = False

        # Atualizar partículas
        for p in particles[:]:
            p.update()
            p.draw(SCREEN)
            if not p.is_alive():
                particles.remove(p)

        dino.draw()
        cactus.draw()

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        SCREEN.blit(score_text, (10, 10))

        if game_over:
            msg = font.render("Game Over - Pressione R para Reiniciar", True, (200, 0, 0))
            SCREEN.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
