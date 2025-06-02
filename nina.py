import pgzrun
import random
import time
from pygame import Rect

WIDTH, HEIGHT, TITLE = 1280, 720, "Neo-Nina and The Systems"
GRAVITY, MAX_ALLIES = 0.4, 3
ANIM_DELAY_FACTOR = 3
BG_MUSIC = 'hardware_prototype.wav'
CLICK_SOUND = 'click'
VOLUME = 0.5
IS_MUTED = False

session, bg_phase = None, None
bg_menu = Actor("background_menu", (WIDTH // 2, HEIGHT // 2))

class NeonNina:
    def __init__(self, x, y):
        self.actor = Actor('neon_nina_idle_1', (x, y + 100))
        self.vx, self.vy, self.speed = 0, 0, 4
        self.on_ground, self.action = False, 'idle'
        self.animations = {
            'idle': ['neon_nina_idle_1', 'neon_nina_idle_2'],
            'jump': ['neon_nina_jump_1', 'neon_nina_jump_2', 'neon_nina_jump_3'],
            'run': ['neon_nina_run_1', 'neon_nina_run_2'],
            'hit': ['neon_nina_hit'],
            'hacking': ['neon_nina_hacking_1','neon_nina_hacking_2','neon_nina_hacking_3']
        }
        self.frame, self.last_frame_time = 0, time.time()
        self.animation_delay = ANIM_DELAY_FACTOR * 0.1
        self.allies, self.hp = [], 100
        self.score = 0

    def draw(self):
        self.actor.draw()

    def update(self, platforms):
        if self.on_ground:
            if keyboard.left:
                self.vx, self.actor.flip_x, self.action = -self.speed, True, 'run'
            elif keyboard.right:
                self.vx, self.actor.flip_x, self.action = self.speed, False, 'run'
            elif keyboard.up:
                self.vy, self.on_ground, self.action = -12, False, 'jump'
            elif keyboard.h:
                self.vx, self.action = 0, 'hacking'
            else:
                self.vx, self.action = 0, 'idle'

        self.vy += GRAVITY
        self.actor.x += self.vx
        self.actor.y += self.vy

        self.actor.x = max(0, min(WIDTH, self.actor.x))
        self.on_ground = False

        if self.actor.y > HEIGHT + 100:
            session.state = 'gameover'

        for p in platforms:
            if self.vy >= 0:
                nina_rect = self.actor._rect
                platform_rect = p.rect()

                horizontal_overlap = (
                    nina_rect.right > platform_rect.left and
                    nina_rect.left < platform_rect.right
                )
                vertical_touch = (
                    nina_rect.bottom <= platform_rect.top + 10 and
                    nina_rect.bottom + self.vy >= platform_rect.top
                )

                if horizontal_overlap and vertical_touch:
                    self.actor.y = platform_rect.top - self.actor.height // 2
                    self.vy = 0
                    self.on_ground = True

    def animate(self):
        now = time.time()
        if now - self.last_frame_time >= self.animation_delay:
            frames = self.animations[self.action]
            self.frame = (self.frame + 1) % len(frames)
            self.actor.image = frames[self.frame]
            self.last_frame_time = now

class Platform:
    def __init__(self, x, y, sprite):
        self.actor = Actor(sprite, (x, y + 100))

    def draw(self):
        self.actor.draw()

    def rect(self):
        return self.actor._rect

class Drone:
    def __init__(self, image, x, y, y_range=40):
        self.actor = Actor(image, (x, y + 100))
        self.vy = random.choice([-1.5, 1.5]) * random.uniform(0.8, 1.6)
        self.upper_limit, self.lower_limit = y + 100 - y_range, y + 100 + y_range

    def update(self):
        self.actor.y += self.vy
        if self.actor.y < self.upper_limit or self.actor.y > self.lower_limit:
            self.vy *= -1
        if session and session.nina and self.actor.distance_to(session.nina.actor) < 200:
            self.attack(session.nina.actor)

    def attack(self, target):
        screen.draw.line(self.actor.pos, target.pos, "yellow")

    def draw(self):
        self.actor.draw()

class BlueHackable(Drone):
    def __init__(self, x, y):
        super().__init__('blue_drone', x, y - 50)
        self.hacked = False
        self.collected = False

    def update(self):
        if self.collected:
            return

        if not self.hacked and keyboard.c and self.actor.distance_to(session.nina.actor) < 60:
            self.collected = True
            session.nina.score += 10
            return

        if not self.hacked and keyboard.h and self.actor.distance_to(session.nina.actor) < 60:
            self.hacked = True

        if self.hacked:
            self.actor.image = 'blue_drone_hacked'
            self.actor.y = session.nina.actor.y
            self.actor.x += 2
            for enemy in session.enemies:
                if isinstance(enemy, RedEnemy) and self.actor.distance_to(enemy.actor) < 40:
                    session.nina.score += 30
                    session.enemies.remove(enemy)

        super().update()

class RedEnemy(Drone):
    def __init__(self):
        x = random.randint(WIDTH//2, WIDTH - 100)
        y = random.randint(100, HEIGHT//2)
        super().__init__('red_drone', x, y + 50)

class Level:
    def __init__(self, phase, bg_image):
        self.phase = phase
        self.bg_image = bg_image
        self.active = False

    def start(self):
        global bg_phase
        self.active = True
        bg_phase = Actor(self.bg_image, (WIDTH // 2, HEIGHT // 2))

    def draw(self):
        if self.active and bg_phase:
            bg_phase.draw()

class GameSession:
    def __init__(self):
        self.state = 'menu'
        self.nina = NeonNina(WIDTH // 2, HEIGHT // 2)
        self.platforms, self.enemies = [], []
        self.level_index = 0
        self.levels = [
            Level(1, 'background_city_1'),
            Level(2, 'background_city_2'),
            Level(3, 'background_city_2')
        ]
        self.load_level(self.level_index)

    def update(self):
        self.nina.update(self.platforms)
        self.nina.animate()  # <- animação atualizada aqui
        for enemy in self.enemies:
            enemy.update()

    def draw(self):
        screen.clear()
        match self.state:
            case 'playing':
                self.levels[self.level_index].draw()
                for blocks in self.platforms: blocks.draw()
                for enemy in self.enemies: enemy.draw()
                self.nina.draw()
                draw_hud()
            case 'menu': draw_menu()
            case 'victory': draw_victory()
            case 'gameover': draw_game_over()

    def start_game(self):
        self.state, self.level_index = 'playing', 0
        self.load_level(self.level_index)

    def load_level(self, index):
        if index >= len(self.levels):
            self.state = 'victory'
            return

        self.level_index = index
        level = self.levels[index]
        level.start()
        self.platforms = []
        self.enemies = []
        self.nina.actor.pos = (100, HEIGHT // 2 + 100)
        self.nina.vx = self.nina.vy = 0

        if index == 0:
            self.platforms = (
                [Platform(128 + i * 128, 512, 'plataform_ground') for i in range(3)] +
                [Platform(640 + i * 128, 368, 'plataform_media') for i in range(2)] +
                [Platform(1058 + i * 128, 256, 'plataform_special') for i in range(1)]
            )
            self.enemies = [RedEnemy(), RedEnemy(), BlueHackable(400, 150)]
        elif index == 1:
            self.platforms = [Platform(128 + i * 128, 512, 'plataform_ground') for i in range(4)]
            self.enemies = [BlueHackable(600, 100), RedEnemy()]
        elif index == 2:
            self.platforms = [Platform(100 + i * 200, 400, 'plataform_media') for i in range(3)]
            self.enemies = [RedEnemy(), BlueHackable(800, 180), BlueHackable(300, 200)]

    def next_level(self):
        self.load_level(self.level_index + 1)

session = GameSession()
menu_buttons = [
    {"label": "play(hero=Nina)", "action": "play", "rect": Rect((WIDTH // 2 - 60, HEIGHT//2 -50), (136, 32))},
    {"label": "change_vol()", "action": "volume", "rect": Rect((WIDTH // 2 - 60, HEIGHT//2 -15), (136, 32))},
    {"label": "mute or unmute", "action": "mute", "rect": Rect((WIDTH // 2 - 60, HEIGHT//2 +20), (136, 32))},
    {"label": "exit_game()", "action": "exit", "rect": Rect((WIDTH // 2 - 60, HEIGHT//2 +55), (136, 32))}
]

def update():
    if session.state == 'playing':
        session.update()

def draw():
    session.draw()

def draw_hud():
    x, y = 20, 20
    width, height = 200, 24
    hp_ratio = session.nina.hp / 100
    screen.draw.filled_rect(Rect((x, y), (width, height)), "red")
    screen.draw.filled_rect(Rect((x, y), (width * hp_ratio, height)), "green")
    screen.draw.rect(Rect((x, y), (width, height)), "white")
    screen.draw.text(f"Score: {session.nina.score}", (x, y + 30), fontsize=24, color="black")
    screen.draw.text(f"use arrow keys to move and jump, H to hack or C to collect", (WIDTH//4, y+5), fontsize=32, color="black")

def draw_menu():
    bg_menu.draw()
    screen.draw.text("Neon Nina",
        center=(WIDTH//2, HEIGHT//4),
        fontsize=160,
        color=(150, 66, 242)
    )
    screen.draw.text("vs TheSystems",
        center=(WIDTH//2, HEIGHT//4+60),
        fontsize=50,
        color=(235,255,235))

    for button in menu_buttons:
        screen.draw.filled_rect(button['rect'], (34,17,34))
        screen.draw.text(button['label'], center=button['rect'].center,
                         fontsize=24, color=(57,255,20))

def draw_victory(): screen.draw.text("Victory!", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="green")

def draw_game_over(): screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="red")

def on_mouse_down(pos):
    if session.state == 'menu':
        for button in menu_buttons:
            if button['rect'].collidepoint(pos):
                match button['action']:
                    case 'play': session.start_game()
                    case 'exit': exit()
                    case 'volume': print("Volume button pressed")
                    case 'mute': print("Mute/unmute button pressed")

pgzrun.go()