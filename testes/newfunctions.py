import pgzrun, random, time
from pygame import Rect

# region Configurações Gerais

WIDTH, HEIGHT, TITLE = (1280, 720, "Neo-Nina and The Systems")
GRAVITY, MAX_ALLIES = (0.4, 3)
SLOWER_ANIM_NINA = 3
BG_MUSIC = 'Hardware_Prototype.wav'

# region Recursos Iniciaisg_game = None
bg_menu = Actor("background_menu", (WIDTH // 2, HEIGHT // 2))

# region Classes
class NeonNina:
    def __init__(self, x, y):
        self.actor = Actor('neon_nina_idle_1', (x, y))
        self.vx, self.vy = 0, 0
        self.speed, self.on_ground = 4, False
        self.action = 'idle'
        self.animations = {
            'idle': ['neon_nina_idle_1', 'neon_nina_idle_2'],
            'jump': ['neon_nina_jump_1','neon_nina_jump_2','neon_nina_jump_3'],
            'run': ['neon_nina_run_1', 'neon_nina_run_2'],
            'hit': ['neon_nina_hit']
        }
        self.frame, self.last_frame_time = 0, time.time()
        self.animation_delay = SLOWER_ANIM_NINA * 0.1
        self.allies, self.hp = [], 100

    def draw(self):
        self.actor.draw()

    def update(self, platforms):
        if not self.on_ground:
            self.action = 'jump'
        elif keyboard.left:
            self.vx, self.actor.flip_x, self.action = -self.speed, True, 'run'
        elif keyboard.right:
            self.vx, self.actor.flip_x, self.action = self.speed, False, 'run'
        else:
            if keyboard.up:
                self.vy, self.on_ground, self.action = -12, False, 'jump'
            else:
                self.vx, self.action = 0, 'idle'

        self.vy += GRAVITY
        self.actor.x += self.vx
        self.actor.y += self.vy
        self.actor.x = max(0, min(WIDTH, self.actor.x))
        self.on_ground = False
        for p in platforms:
            if self.actor.colliderect(p.rect()) and self.vy >= 0:
                self.actor.y = p.rect().top - self.actor.height // 2
                self.vy, self.on_ground = 0, True

        if self.actor.x > WIDTH - 48:
            session.change_level()

        self.animate()

    def animate(self):
        now = time.time()
        if now - self.last_frame_time >= self.animation_delay:
            frames = self.animations[self.action]
            self.frame = (self.frame + 1) % len(frames)
            self.actor.image = frames[self.frame]
            self.last_frame_time = now

class Platform:
    def __init__(self, x, y, sprite):
        self.actor = Actor(sprite, (x, y))

    def draw(self):
        self.actor.draw()

    def rect(self):
        return self.actor._rect

class EnemyDrone:
    def __init__(self, x, y):
        self.actor = Actor('enemy_drone', (x, y))
        self.vy = random.choice([-1.5, 1.5]) * random.uniform(0.8, 1.6)
        self.upper_limit, self.lower_limit = y - 40, y + 40
        self.ally, self.target = False, None

    def update(self):
        self.actor.y += self.vy
        if self.actor.y < self.upper_limit or self.actor.y > self.lower_limit:
            self.vy *= -1
        if self.actor.distance_to(session.neon_nina.actor) < 200:
            self.attack(session.neon_nina.actor)

    def attack(self, target):
        screen.draw.line(self.actor.pos, target.pos, "yellow")

    def draw(self):
        self.actor.draw()

class Level:
    def __init__(self, phase, bg):
        self.phase = phase
        self.bg = bg
        self.active = False

    def start(self):
        global bg_game
        self.active = True
        bg_game = Actor(self.bg, (WIDTH // 2, HEIGHT // 2))

    def draw(self):
        if self.active and bg_game:
            bg_game.draw()

class GameSession:
    def __init__(self):
        self.state = 'menu'
        self.neon_nina = NeonNina(WIDTH // 2, HEIGHT // 2)
        self.platforms = []
        self.enemies = []
        self.level_index = 0
        self.levels = [
            Level(1, 'background_city_1'),
            Level(2, 'background_city_2'),
            Level(3, 'background_city_2')
        ]
        self.start_level(self.level_index)

    def update(self):
        self.neon_nina.update(self.platforms)
        for enemy in self.enemies:
            enemy.update()

    def draw(self):
        screen.clear()
        if self.state == 'playing':
            if bg_game:
                bg_game.draw()
            for p in self.platforms:
                p.draw()
            for enemy in self.enemies:
                enemy.draw()
            self.neon_nina.draw()
            draw_hud()
        elif self.state == 'menu':
            draw_menu()
        elif self.state == 'victory':
            draw_victory()
        elif self.state == 'gameover':
            draw_game_over()

    def start_game(self):
        self.state = 'playing'
        self.level_index = 0
        self.start_level(self.level_index)

    def start_level(self, index):
        if index >= len(self.levels):
            self.state = 'victory'
            return

        self.level_index = index
        level = self.levels[index]
        level.start()
        self.platforms = []
        self.enemies = []
        self.neon_nina.actor.pos = (100, HEIGHT // 2)
        self.neon_nina.vx = self.neon_nina.vy = 0

        if index == 0:
            self.platforms = (
                [Platform(128 + i * 128, 512, 'plataform_ground') for i in range(3)] +
                [Platform(640 + i * 128, 368, 'plataform_media') for i in range(2)] +
                [Platform(1058 + i * 128, 256, 'plataform_special') for i in range(1)]
            )
            self.enemies = [EnemyDrone(600, 100), EnemyDrone(700, 200), EnemyDrone(400, 150)]
        elif index == 1:
            self.platforms = [Platform(128 + i * 128, 512, 'plataform_ground') for i in range(4)]
            self.enemies = [EnemyDrone(600, 100), EnemyDrone(700, 200)]
        elif index == 2:
            self.platforms = [Platform(100 + i * 200, 400, 'plataform_media') for i in range(3)]
            self.enemies = [EnemyDrone(500, 150), EnemyDrone(300, 200), EnemyDrone(800, 180)]

    def change_level(self):
        self.start_level(self.level_index + 1)

# region Sessão e Jogo
session = GameSession()
menu_buttons = [
    {"label": "Play", "action": "play", "rect": Rect((WIDTH // 2 - 60, 200), (120, 40))},
    {"label": "Exit", "action": "exit", "rect": Rect((WIDTH // 2 - 60, 260), (120, 40))}
]

def update():
    if session.state == 'playing':
        session.update()

def draw():
    session.draw()

def draw_hud():
    x, y = 20, 20
    width, height = 200, 24
    hp_ratio = session.neon_nina.hp / 100
    screen.draw.filled_rect(Rect((x, y), (width, height)), "red")
    screen.draw.filled_rect(Rect((x, y), (width * hp_ratio, height)), "green")
    screen.draw.rect(Rect((x, y), (width, height)), "white")

def draw_menu():
    bg_menu.draw()
    for button in menu_buttons:
        screen.draw.filled_rect(button['rect'], 'darkblue')
        screen.draw.text(button['label'], center=button['rect'].center, fontsize=36, color='white')

def draw_victory():
    screen.draw.text("Vitória!", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="white")

def draw_game_over():
    screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="red")

def on_mouse_down(pos):
    if session.state == 'menu':
        for button in menu_buttons:
            if button['rect'].collidepoint(pos):
                if button['action'] == 'play':
                    session.start_game()
                elif button['action'] == 'exit':
                    exit()

pgzrun.go()