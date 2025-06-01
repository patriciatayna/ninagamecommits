from characters.neon_nina import NeonNina
from mod.config import WIDTH, HEIGHT
from mod.levels import drones

class GameSession:
    def __init__(self):
        self.reset()
        self.neon_nina = NeonNina(WIDTH // 2, HEIGHT // 2)
        self.enemies = []

    def reset(self):
        self.state = 'menu'

    def update(self):
        self.neon_nina.update()
        for enemy in self.enemies:
            enemy.update()

    def draw(self):
        self.neon_nina.draw()
        for enemy in self.enemies:
            enemy.draw()

    def start_game(self):
        self.reset()
        self.state = 'playing'
        self.neon_nina = NeonNina(100, 400)
        self.enemies = drones

    def game_over(self):
        pass  # Desativado durante testes

session = GameSession()

def update_session():
    if session.state == 'playing':
        session.update()
        for d in drones:
            d.update()

def draw_session():
    session.draw()
