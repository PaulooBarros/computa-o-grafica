# README - Jogo do Dino com Efeitos Visuais Avançados

## Visão Geral
Este é um jogo do dinossauro (estilo Chrome Dino) com efeitos visuais avançados, sistema de partículas, shaders e otimizações de performance. O jogo foi desenvolvido em Python usando Pygame e OpenCV para os efeitos especiais.

## Tecnologias e Técnicas Utilizadas

### 1. **Motor Gráfico e Biblioteca de Som**
- **Pygame**: Biblioteca principal para renderização gráfica, tratamento de input e som
- **pygame.mixer**: Sistema de áudio para efeitos sonoros

### 2. **Processamento de Imagem**
- **OpenCV (cv2)**: Para manipulação avançada de imagens:
  - Ajuste de brilho/contraste
  - Efeitos de distorção de onda
  - Transformações de espaço de cor (BGR para HSV)

### 3. **Efeitos Visuais**
- **Sistema de Partículas**:
  - Partículas de poeira ao pular/aterrissar
  - Efeito de explosão no game over
  - Object Pooling para otimização
- **Shaders Simples**:
  - Efeito de vignette (escurecimento das bordas)
  - Filtros de cor em tempo real
- **Efeitos de Pós-processamento**:
  - Screen shake (tremor de tela)
  - Slow motion
  - Piscar de tela
  - Mudança de cores (hue shifting)

### 4. **Otimizações de Performance**
- **Surface Caching**: Armazenamento de superfícies pré-renderizadas
- **Delta Time**: Movimento independente de framerate
- **Object Pooling**: Reutilização de objetos de partículas
- **Renderização Intermediária**: Desenho em surface off-screen antes de exibir
- **Colisão em Duas Etapas**: Primeiro bounding box, depois máscara de pixel

### 5. **Estruturas de Dados**
- **NumPy**: Para operações matriciais eficientes em imagens
- **deque**: Para gerenciamento eficiente de partículas

## Mecânicas do Jogo

### Controles
- **Barra de Espaço**: Pular
- **Tecla R**: Reiniciar após game over

### Objetos do Jogo
- **Dinossauro**: Personagem controlado pelo jogador
- **Cactos**: Obstáculos terrestres
- **Pássaros**: Obstáculos aéreos
- **Sistema de Pontuação**: Aumenta ao passar por obstáculos

### Efeitos Especiais
- **Slow Motion**: Quando ocorre colisão
- **Explosão de Partículas**: No momento do game over
- **Tremor de Tela**: Durante o game over
- **Efeito de Dano**: Mudança de cor no dinossauro

## Estrutura do Código

### Classes Principais
1. **Particle**: Representa uma partícula individual
2. **ParticleSystem**: Gerencia todas as partículas com object pooling
3. **Dino**: Personagem jogável com física de pulo
4. **Obstacle**: Classe base para cactos e pássaros
5. **GameOverEffect**: Gerencia efeitos visuais de game over

### Funções Importantes
- `load_assets()`: Carrega e processa todos os recursos do jogo
- `apply_color_effect()`: Aplica filtros de cor em superfícies
- `check_collision()`: Verificação otimizada de colisão

## Como Executar

1. Instale os requisitos:
```bash
pip install pygame opencv-python numpy
```
```
pip install -r requirements.txt
```

2. Execute o jogo:
```bash
python dinogame.py
```



