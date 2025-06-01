import pgzrun

WIDTH = 600
HEIGHT = 400

class Fase:
    def __init__(self, nome, cor_fundo, pos_meta):
        self.nome = nome
        self.cor_fundo = cor_fundo
        self.pos_meta = pos_meta
        self.ativo = False

    def iniciar(self):
        self.ativo = True

    def desenhar(self):
        screen.fill(self.cor_fundo)
        # desenha meta (círculo)
        screen.draw.filled_circle(self.pos_meta, 20, "yellow")

    def checar_meta(self, jogador_pos):
        # retorna True se o jogador alcançou a meta
        dx = jogador_pos[0] - self.pos_meta[0]
        dy = jogador_pos[1] - self.pos_meta[1]
        distancia = (dx*dx + dy*dy) ** 0.5
        return distancia < 30

class Jogador:
    def __init__(self):
        self.pos = [50, HEIGHT//2]
        self.tamanho = 30
        self.vel = 4

    def mover(self):
        if keyboard.left:
            self.pos[0] -= self.vel
        if keyboard.right:
            self.pos[0] += self.vel
        if keyboard.up:
            self.pos[1] -= self.vel
        if keyboard.down:
            self.pos[1] += self.vel

        # limitar dentro da tela
        self.pos[0] = max(self.tamanho//2, min(WIDTH - self.tamanho//2, self.pos[0]))
        self.pos[1] = max(self.tamanho//2, min(HEIGHT - self.tamanho//2, self.pos[1]))

    def desenhar(self):
        x, y = self.pos
        screen.draw.filled_rect(Rect((x - self.tamanho//2, y - self.tamanho//2), (self.tamanho, self.tamanho)), "white")

# Criar fases
fase1 = Fase("Fase 1", (30, 144, 255), (550, 350))  # azul, meta no canto inferior direito
fase2 = Fase("Fase 2", (34, 139, 34), (550, 50))   # verde, meta no canto superior direito
fase3 = Fase("Fase 3", (178, 34, 34), (50, 350))   # vermelho, meta no canto inferior esquerdo

fases = [fase1, fase2, fase3]
indice_fase = 0
fase_atual = fases[indice_fase]

jogador = Jogador()
fase_atual.iniciar()

jogo_terminado = False

def update():
    global indice_fase, fase_atual, jogo_terminado

    if jogo_terminado:
        return

    jogador.mover()
    if fase_atual.checar_meta(jogador.pos):
        indice_fase += 1
        if indice_fase >= len(fases):
            jogo_terminado = True
        else:
            fase_atual = fases[indice_fase]
            fase_atual.iniciar()
            # resetar posição do jogador ao centro
            jogador.pos = [50, HEIGHT//2]

def draw():
    if jogo_terminado:
        screen.fill("black")
        screen.draw.text("Você venceu!", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="white")
    else:
        fase_atual.desenhar()
        jogador.desenhar()
        # mostrar texto da fase no topo
        screen.draw.text(fase_atual.nome, (10, 10), fontsize=30, color="white")

pgzrun.go()
