import pgzrun, random, time
from pygame import Rect

#region GameConfig
WIDTH, HEIGHT, TITLE = (1280, 720, "Neo-Nina and The Systems")
GRAVITY, MAX_ALLIES = (0.4, 3)
slower_anim_nina = 3
game_level, bg_game = (1, None)
platforms, enemies = ([], [])

bg_music = 'Hardware_Prototype.wav'
bg_menu = Actor("background_menu", (WIDTH//2, HEIGHT//2))
#endregion

#region Classes
class NeonNina:
    def __init__(self, x, y):
        self.actor = Actor('neon_nina_idle_1', (x, y))
        self.vx, self.vy = (0, 0)
        self.speed, self.on_ground = (4, False)
        self.action = 'idle'
        self.animations = {
            'idle': ['neon_nina_idle_1', 'neon_nina_idle_2'],
            'jump': ['neon_nina_jump_1','neon_nina_jump_2','neon_nina_jump_3'],
            'run': ['neon_nina_run_1', 'neon_nina_run_2'],
            'hit': ['neon_nina_hit'],
        }
        self.frame, self.last_frame_time = 0, time.time()
        self.animation_delay = slower_anim_nina * 0.1
        self.allies, self.hp = [], 100

    def draw(self): self.actor.draw()

    def update(self):
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

        if self.actor.x > WIDTH-48:
            change_level()

        self.animate()

    def animate(self):
        now = time.time()
        if now - self.last_frame_time >= self.animation_delay:
            frames = self.animations[self.action]
            self.frame = (self.frame + 1) % len(frames)
            self.actor.image = frames[self.frame]
            self.last_frame_time = now

    def hacking(self):
        # Hackear inimigos próximos e transformar em aliados (máx. MAX_ALLIES)
        nearby_enemies = [e for e in session.enemies if not e.ally and self.actor.distance_to(e.actor) < 80]
        if nearby_enemies and len(self.allies) < MAX_ALLIES:
            to_hack = nearby_enemies[0]
            to_hack.ally = True
            self.allies.append(to_hack)
            to_hack.actor.image = 'enemy_drone_hacked'  # Troque pelo sprite correto do aliado


class Platform:
    def __init__(self, x, y, sprite):
        self.actor = Actor(sprite, (x, y))
    def draw(self): self.actor.draw()
    def rect(self): return self.actor._rect

class EnemyDrone:
    def __init__(self, x, y):
        self.actor = Actor('enemy_drone', (x, y))
        self.vy = random.choice([-1.5, 1.5]) * random.uniform(0.8, 1.6)
        self.upper_limit, self.lower_limit = y - 40, y + 40
        self.ally = False  # Flag para inimigos hackeados
        self.target = None

    def update(self):
        if self.ally:
            self.follow_ally()
            self.attack_nearby_enemies()
        else:
            self.actor.y += self.vy
            if self.actor.y < self.upper_limit or self.actor.y > self.lower_limit:
                self.vy *= -1
            if self.actor.distance_to(session.neon_nina.actor) < 200:
                self.attack(session.neon_nina.actor)

    def follow_ally(self):
        # Aliado segue a Neo-Nina mantendo distância para não empilhar
        target_pos = session.neon_nina.actor.pos
        dx = target_pos[0] - self.actor.x
        dy = target_pos[1] - self.actor.y
        dist = (dx**2 + dy**2)**0.5
        if dist > 50:
            self.actor.x += dx * 0.05
            self.actor.y += dy * 0.05

    def attack_nearby_enemies(self):
        # Ataca inimigos (não aliados) próximos (150 px)
        for enemy in session.enemies:
            if enemy != self and not enemy.ally:
                if self.actor.distance_to(enemy.actor) < 150:
                    self.attack(enemy.actor)
                    break

    def attack(self, target):
        screen.draw.line(self.actor.pos, target.pos, "cyan" if self.ally else "yellow")

    def draw(self):
        if self.ally:
            # Desenho extra para aliados (exemplo: brilho azul)
            screen.draw.filled_circle(self.actor.pos, 25, (0, 100, 255, 100))
        self.actor.draw()

class WreckerBoss:
    def __init__(self, x, y):
        self.actor = Actor('eggwrecker_1', (x, y))
        self.vy = random.choice([-1.5, 1.5]) * random.uniform(0.8, 1.6)
        self.upper_limit, self.lower_limit = y-40, y+40
        self.target = session.neon_nina.actor
    def update(self):
        self.actor.y += self.vy
        if self.actor.y < self.upper_limit or self.actor.y > self.lower_limit:
            self.vy *= -1
        if self.actor.distance_to(self.target) < 200:
            self.attack(self.target)
    def attack(self, target):
        screen.draw.line(self.actor.pos, target.pos, "yellow")
    def draw(self): self.actor.draw()

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
        screen.clear()
        if self.state == 'playing':
            self.neon_nina.draw()
        for enemy in self.enemies:
            enemy.draw()
    def start_game(self):
        self.reset()
        self.state = 'playing'
        self.neon_nina = NeonNina(100, 400)
        self.enemies = drones
    def game_over(self):
        pass  # Disabled to prevent interruption during level testing

class Level:
    def __init__(self, phase, bg):
        self.bg = bg
        self.phase = phase
        self.active = False
    def start(self):
        global bg_game
        self.active = True
        bg_game = Actor(self.bg, (WIDTH // 2, HEIGHT // 2))
    def draw(self):
        if self.active and bg_game:
            bg_game.draw()
#endregion

#region Level system
levels = [
    Level(1, 'background_city_1'),
    Level(2, 'background_city_2'),
    Level(3, 'background_city_2')
]
current_level_index = 0
current_level = levels[current_level_index]
def change_level():
    global current_level_index, platforms, drones
    current_level_index += 1
    if current_level_index >= len(levels):
        session.state = 'victory'
        return
    current_level = levels[current_level_index]
    current_level.start()
    session.neon_nina.actor.pos = (100, HEIGHT // 2)
    session.neon_nina.vx = session.neon_nina.vy = 0
    if current_level_index == 1:
        platforms = [Platform(128 + i * 128, 512, 'plataform_ground') for i in range(4)]
        drones = [EnemyDrone(600, 100), EnemyDrone(700, 200)]
    elif current_level_index == 2:
        platforms = [Platform(100 + i * 200, 400, 'plataform_media') for i in range(3)]
        drones = [EnemyDrone(500, 150), EnemyDrone(300, 200), EnemyDrone(800, 180)]
#endregion

#region Session
session = GameSession()
levels[current_level_index].start()  # Set background for first level
platforms = (
    [Platform(128 + i * 128, 512, 'plataform_ground') for i in range(3)] +
    [Platform(640 + i * 128, 368, 'plataform_media') for i in range(2)] +
    [Platform(1058 + i * 128, 256, 'plataform_special') for i in range(1)]
)
drones = [EnemyDrone(600, 100), EnemyDrone(700, 200), EnemyDrone(400, 150)]
menu_buttons = [
    {"label": "Play", "action": "play", "rect": Rect((WIDTH // 2 - 60, 200), (120, 40))},
    {"label": "Exit", "action": "exit", "rect": Rect((WIDTH // 2 - 60, 260), (120, 40))}
]
#endregion

#region Game loop
def update():
    if session.state == 'playing':
        session.update()
        for d in drones: d.update()
        if keyboard.h:
            session.neon_nina.hacking()
def draw():
    if session.state == 'menu':
        draw_menu()
    elif session.state == 'playing':
        if bg_game: bg_game.draw()
        for p in platforms: p.draw()
        for d in drones: d.draw()
        session.neon_nina.draw()
    elif session.state == 'victory':
        draw_victory()
    elif session.state == 'gameover':
        draw_game_over()
#endregion

#region Events
def on_mouse_down(pos):
    if session.state == 'menu':
        for button in menu_buttons:
            if button["rect"].collidepoint(pos):
                if button["action"] == "play":
                    session.start_game()
                elif button["action"] == "exit":
                    quit()
def on_key_down(key):
    if session.state in ['gameover', 'victory'] and key == keys.RETURN:
        session.reset()
#endregion

#region UI
def draw_menu():
    bg_menu.draw()
    screen.draw.text("Neo-Nina and the Systems", center=(WIDTH // 2 - 64, 100),
                     fontsize=64, color="white")
    for button in menu_buttons:
        screen.draw.filled_rect(button["rect"], "gray")
        screen.draw.text(button["label"], center=button["rect"].center,
                         fontsize=40, color="white")
def draw_game_over():
    screen.fill("darkred")
    screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="white")
    screen.draw.text("Press Enter to return to menu", center=(WIDTH // 2, HEIGHT // 2 + 60), fontsize=48, color="white")
def draw_victory():
    screen.fill("darkgreen")
    screen.draw.text("VICTORY!", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="white")
    screen.draw.text("Press Enter to return to menu", center=(WIDTH // 2, HEIGHT // 2 + 60), fontsize=48, color="white")
#endregion

pgzrun.go()