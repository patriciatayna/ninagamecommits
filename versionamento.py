import pgzrun, random, time
from pygame import Rect
#region Config
WIDTH, HEIGHT, TITLE = 1280, 720, "Neo-Nina and The Systems"
GRAVITY, MAX_ALLIES = 0.4, 3
slower_anim_nina = 3
bg_music, bg_image = 'Hardware_Prototype.wav', Actor(
    "background_city", (WIDTH//2, HEIGHT//2))
#endregion
#region Classes
class NeonNina:
    def __init__(self, x, y):
        self.actor = Actor('neon_nina_idle_2', (x, y))
        self.vx, self.vy = 0, 0
        self.speed, self.on_ground = 2, False
        self.action = 'idle'
        self.animations = {
            'idle': ['neon_nina_idle_1', 'neon_nina_idle_2'],
            'jump': ['neon_nina_jump_1','neon_nina_jump_2','neon_nina_jump_3'],
            'run': ['neon_nina_run_1', 'neon_nina_run_2', 'neon_nina_run_3'],
            'hit': ['neon_nina_hit'],
        }
        self.frame, self.last_frame_time = 0, time.time()
        self.animation_delay = slower_anim_nina*0.1
        self.allies, self.hp = [], 100

    def draw(self):
        self.actor.draw()

    def update(self):
        if not self.on_ground: self.action = 'jump'

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
        
        self.actor.x, self.on_ground = max(0, min(WIDTH, self.actor.x)), False

        for p in platforms:
            if self.actor.colliderect(p.rect()) and self.vy >= 0:
                self.actor.y = p.rect().top-self.actor.height//2
                self.vy, self.on_ground = 0, True

        if self.actor.y > HEIGHT: game_over()
        self.animate()

    def animate(self):
        now = time.time()
        if now - self.last_frame_time >= self.animation_delay:
            frames = self.animations[self.action]
            self.frame = (self.frame + 1) % len(frames)
            self.actor.image, self.last_frame_time = frames[self.frame], now
class Platform:
    def __init__(self, x, y, sprite):
        self.actor = Actor(sprite, (x, y))
    def draw(self): self.actor.draw()
    def rect(self): return self.actor._rect
class EnemyDrone:
    def __init__(self, x, y):
        self.actor, self.vy = Actor('enemy_drone', (x, y)), random.choice([-1.5, 1.5])*random.uniform(0.8, 1.6)
        self.upper_limit, self.lower_limit = y-40, y+40
        self.ally, self.target = False, None

    def update(self):
        self.actor.y += self.vy
        if self.actor.y < self.upper_limit or self.actor.y > self.lower_limit:
            self.vy *= -1
        if self.actor.distance_to(neon_nina.actor) < 200:
            self.attack(neon_nina.actor)

    def attack(self, target): screen.draw.line(self.actor.pos, target.pos, "yellow")
    def draw(self): self.actor.draw()
class GameSession:
    def __init__(self):
        self.reset()
        self.neon_nina = NeonNina(WIDTH // 2, HEIGHT//2)
        self.enemies = []

    def reset(self):
        self.state = 'menu'

    def update(self):
        self.neon_nina.update()
        for enemy in self.enemies: enemy.update()

    def draw(self):
        screen.clear()
        self.neon_nina.draw()
        for enemy in self.enemies: enemy.draw()
    
    def start_game(self):
        self.reset()
        self.state = 'playing'
        #sounds.hardware_prototype.play(-1)

    def game_over(self): self.state = 'gameover'
#endregion
#region Session
session = GameSession()
neon_nina = NeonNina(100, 400)
platforms = ([Platform(128 + i * 128, 512, 'plataform_ground') for i in range(3)] 
+ [Platform(640 + i * 128, 368, 'plataform_media') for i in range(2)] 
+ [Platform(1058 + i * 128, 256, 'plataform_special') for i in range(1)])
drones = [EnemyDrone(600, 100), EnemyDrone(700, 200), EnemyDrone(400, 150)]
menu_buttons = [{"label": "Play", "action": "play", "rect": Rect((WIDTH//2 - 60, 200), (120, 40))},
    {"label": "Exit", "action": "exit", "rect": Rect((WIDTH//2 - 60, 260), (120, 40))}]

def update(): session.update()
def draw():
    session.draw()
    if session.state == 'menu': draw_menu()

    elif session.state == 'playing':
        bg_image.draw()
        for p in platforms: p.draw()
        for d in drones: d.draw()
        neon_nina.draw()

    elif session.state == 'victory': session.draw_victory_screen()
    elif session.state == 'gameover': draw_game_over()
#endregion
#region Update
def update():
    if session.state == 'playing':
        neon_nina.update()
        for d in drones:
            d.update()
        if keyboard.h:
            neon_nina.hacking()
#endregion
#region Eventos
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
    screen.fill((10, 10, 20))
    screen.draw.text("Neo-Nina and the Systems", center=(WIDTH//2, 100), fontsize=40, color="white")
    for button in menu_buttons:
        screen.draw.filled_rect(button["rect"], "gray")
        screen.draw.text(button["label"], center=button["rect"].center, fontsize=30, color="white")
def draw_game_over():
    screen.fill("darkred")
    screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="white")
    screen.draw.text("Press Enter to return to menu", center=(WIDTH//2, HEIGHT//2 + 60), fontsize=30, color="white")
#endregion
pgzrun.go()