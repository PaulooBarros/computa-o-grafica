# Jogo do Dinossauro com Efeitos Visuais e Segmentação de Imagem

Este é um jogo inspirado no famoso "Dino Game" do Chrome, mas com recursos avançados de processamento de imagem e efeitos visuais criativos.

## Funcionalidades Implementadas

### a) Jogo Completo (2,0 pontos)
- **Personagem principal**: Dinossauro que pode pular
- **Obstáculos**: Cactos e pássaros que aparecem aleatoriamente
- **Objetivo final**: Obter a maior pontuação possível desviando dos obstáculos
- **Efeitos sonoros**: Sons para pulo, colisão e game over
- **Efeitos visuais**: Partículas, poeira, slow motion ao colidir
- **Movimentação fluida**: Física de pulo e gravidade suave
- **Detecção de colisões**: Usando máscaras de pixels para precisão
- **Resposta às ações**: Sistema de dano, efeitos de colisão e reinício do jogo

### b) Segmentação de Imagens (1,0 ponto)
- **Ajuste de brilho**: Usando OpenCV para converter imagens para HSV e aumentar o canal V (value)
- **Distorção de onda**: Aplicando transformações de remapeamento para criar efeitos ondulados
- **Efeitos de cor**: Manipulação direta dos canais RGB para criar variações visuais
- **Máscaras de colisão**: Geração automática de máscaras a partir das imagens processadas

### c) Efeitos Visuais Criativos (0,5 pontos)
- **Slow motion**: Quando ocorre uma colisão
- **Partículas**: Efeito de explosão ao perder
- **Poeira**: Partículas que aparecem ao pular e aterrissar
- **Vignette**: Escurecimento nas bordas da tela
- **Efeito de shake**: Tela treme ao perder
- **Transição de cores**: Efeito de mudança de cor durante o game over
- **Textos com contorno**: Melhor legibilidade em qualquer fundo

## Como Executar

1. Certifique-se de ter Python instalado
2. Instale as dependências: `pip install pygame opencv-python numpy`
3. Execute o arquivo principal: `python dinogame.py`

## Controles
- **Barra de espaço**: Pular
- **Tecla R**: Reiniciar após game over

## Estrutura de Arquivos
- `assets/`: Pasta contendo imagens e sons do jogo
  - `sounds/`: Efeitos sonoros
  - `dino.png`, `cactus.png`, `bird.png`: Imagens dos elementos do jogo

## Tecnologias Utilizadas
- Pygame: Renderização e controle do jogo
- OpenCV: Processamento de imagens para efeitos visuais
- NumPy: Manipulação de arrays para efeitos de imagem
