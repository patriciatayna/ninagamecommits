import pgzrun
import random
from pygame import Rect
import time

#region Config
WIDTH, HEIGHT = 1280,720
TITLE = "Neo-Nina and The Systems"
GRAVITY = 0.4
SLOWERANIMATION = 2
MAX_ALLIES = 3
bg_music = 'Hardware_Prototype.wav'
background = Actor("background_city", (WIDTH//2, HEIGHT//2))

class NeonNina:
    def __init__(self, x, y):
        self.actor = Actor('neon_nina_idle_2', (x, y))
        self.vx = 0
        self.vy = 0
        self.speed = 3
        self.on_ground = False
        self.action = 'idle'
        self.animations = {
            'idle': ['neon_nina_idle_1', 'neon_nina_idle_2'],
            'jump': ['neon_nina_jump_1','neon_nina_jump_2','neon_nina_jump_3'],
            'run': ['neon_nina_run_1', 'neon_nina_run_2', 'neon_nina_run_3'],
            'hit': ['neon_nina_hit'],
        }
        self.frame = 0
        self.last_frame_time = time.time()
        self.animation_delay = SLOWERANIMATION*0.1
        self.allies = []
        self.hp = 100

    def draw(self):
        self.actor.draw()

    def update(self):
        if keyboard.left:
            self.vx = -self.speed
            self.action = 'run'
            self.actor.flip_x = True
        elif keyboard.right:
            self.vx = self.speed
            self.action = 'run'
            self.actor.flip_x = False
        else:
            self.vx = 0
            self.action = 'idle'

        if keyboard.up and self.on_ground:
            self.vy = -14
            self.on_ground = False
            self.action = 'jump'

        self.vy += GRAVITY
        self.actor.x += self.vx
        self.actor.y += self.vy
        self.actor.x = max(0, min(WIDTH, self.actor.x))
        self.on_ground = False

        for p in platforms:
            if self.actor.colliderect(p.rect()) and self.vy >= 0:
                self.actor.y = p.rect().top
                self.vy = 0
                self.on_ground = True

        if self.actor.y > HEIGHT:
            game_over()

        self.animate()

    def animate(self):
        if self.action not in self.animations:
            return
        
        now = time.time()
        if now - self.last_frame_time >= self.animation_delay:
            frames = self.animations[self.action]
            self.frame = (self.frame + 1) % len(frames)
            self.actor.image = frames[self.frame]
            self.last_frame_time = now

    # def hacking(self):
    #     for d in drones:
    #         if self.actor.distance_to(d.actor) < 100 and not d.ally:
    #             if len(self.allies) < MAX_ALLIES:
    #                 d.ally = True
    #                 self.allies.append(d)
    #                 break    

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
        self.vy = random.choice([-1, 1]) * random.uniform(0.5, 1.2)
        self.upper_limit = y - 40
        self.lower_limit = y + 40
        self.ally = False
        self.target = None

    def update(self):
        self.actor.y += self.vy
        if self.actor.y < self.upper_limit or self.actor.y > self.lower_limit:
            self.vy *= -1
        # if self.ally:
        #     self.search_target()
        else:
            if self.actor.distance_to(neon_nina.actor) < 200:
                self.attack(neon_nina.actor)

    def attack(self, target):
        screen.draw.line(self.actor.pos, target.pos, "yellow")

    def draw(self):
        self.actor.draw()
        #if hasattr(target, "hp"):
            #target.hp -= 10

    # def search_target(self):
    #     nearest = None
    #     min_dist = float('inf')
    #     for enemy in self.game.enemies:
    #         if enemy is not self and not enemy.ally:
    #             dist = self.actor.distance_to(enemy.actor)
    #             if dist < min_dist:
    #                 min_dist = dist
    #                 nearest = enemy
    #     if nearest and min_dist < 150:
    #         self.attack(nearest)

class GameSession:
    def __init__(self):
        self.reset()
        self.neon_nina = NeonNina(WIDTH // 2, HEIGHT//2)
        self.enemies = []

    def reset(self):
        self.state = 'menu'

    def update(self):
        self.neon_nina.update()
        for enemy in self.enemies:
            enemy.update()

    def draw(self):
        screen.clear()
        self.neon_nina.draw()
        for enemy in self.enemies:
            enemy.draw()
    
    def start_game(self):
        self.reset()
        self.state = 'playing'
        #sounds.hardware_prototype.play(-1)

    def game_over(self):
        self.state = 'gameover'

session = GameSession()
neon_nina = NeonNina(100, 400)
platforms = ([Platform(128 + i * 128, 512, 'plataform_ground') for i in range(3)] 
+ [Platform(640 + i * 128, 368, 'plataform_media') for i in range(2)] 
+ [Platform(1058 + i * 128, 256, 'plataform_special') for i in range(1)])

drones = [EnemyDrone(600, 100), EnemyDrone(700, 200), EnemyDrone(400, 150)]
menu_buttons = [{"label": "Play", "action": "play", "rect": Rect((WIDTH//2 - 60, 200), (120, 40))},
    {"label": "Exit", "action": "exit", "rect": Rect((WIDTH//2 - 60, 260), (120, 40))}]

def update():
    session.update()

def draw():
    session.draw()
    if session.state == 'menu':
        draw_menu()
    elif session.state == 'playing':
        background.draw()
        for p in platforms:
            p.draw()
        for d in drones:
            d.draw()
        neon_nina.draw()
    elif session.state == 'victory':
        session.draw_victory_screen()
    elif session.state == 'gameover':
        draw_game_over()

# Update
def update():
    if session.state == 'playing':
        neon_nina.update()
        for d in drones:
            d.update()
        if keyboard.h:
            neon_nina.hacking()

# Eventos
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

# UI
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

# Run Game
pgzrun.go()

