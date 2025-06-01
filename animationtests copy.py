import pgzrun
import random
import math

from pygame import Rect

#region Config
WIDTH, HEIGHT = 1280, 720
TITLE = "Neo-Nina and The Systems"
GRAVITY = 0.5
bg_music = 'Hardware_Prototype.wav'
fullscreen = True
background = Actor("background_city", (WIDTH//2, HEIGHT//2))

#endregion

#region GameControl
class GameSession:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state = 'menu'

    def start_game(self):
        self.reset()
        self.state = 'playing'
        #sounds.hardware_prototype.play(-1)

    def game_over(self):
        self.state = 'gameover'
#endregion
#region Classes
class Platform:
    def __init__(self, x, y, sprite):
        self.actor = Actor(sprite, (x, y))

    def draw(self):
        self.actor.draw()

    def rect(self):
        return self.actor._rect
import time  # adicione no topo do seu código

class NeoNina:
    def __init__(self, x, y):
        self.actor = Actor('neon_nina_idle_2', (x, y))
        self.vx = 0
        self.vy = 0
        self.speed = 3
        self.on_ground = False
        self.action = 'idle'
        self.animations = {
            'idle': ['neon_nina_idle_1'],
            'jump': ['neon_nina_jump_1','neon_nina_jump_2','neon_nina_jump_3'],
            'run': ['neon_nina_run_1', 'neon_nina_run_2', 'neon_nina_run_3'],
            'hit': ['neon_nina_hit'],
        }
        self.frame = 0
        self.last_frame_time = time.time()
        self.animation_delay = 0.2  # tempo entre frames da animação (em segundos)
        self.allies = []
        self.hp = 100

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
            session.game_over()

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

    def hacking(self):
        for d in drones:
            if self.actor.distance_to(d.actor) < 100 and not d.ally:
                if len(self.allies) < MAX_ALLIES:
                    d.ally = True
                    self.allies.append(d)
                    break

    def draw(self):
        self.actor.draw()
        for i, ally in enumerate(self.allies):
            icon = Actor("ally_icon", (30 + i * 40, 50))
            icon.draw()
        screen.draw.filled_rect(Rect(10, 10, self.hp * 2, 20), "red")
        screen.draw.rect(Rect(10, 10, 200, 20), "white")

class Drone:
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
        if self.ally:
            self.search_target()
        else:
            if self.actor.distance_to(neo_nina.actor) < 100:
                self.attack(neo_nina.actor)

    def search_target(self):
        for d in drones:
            if not d.ally and self.actor.distance_to(d.actor) < 150:
                self.target = d
                break
        if self.target:
            dx = self.target.actor.x - self.actor.x
            dy = self.target.actor.y - self.actor.y
            self.actor.x += 0.8 if dx > 0 else -0.8
            self.actor.y += 0.5 if dy > 0 else -0.5
            if self.actor.distance_to(self.target.actor) < 20:
                self.attack(self.target.actor)

    def attack(self, target):
        screen.draw.line(self.actor.pos, target.pos, "yellow")

    def draw(self):
        self.actor.draw()
#endregion

# Objects

session = GameSession()
neo_nina = NeoNina(100, 400)
platforms = ([Platform(128 + i * 128, 512, 'plataform_ground') for i in range(3)] 
+ [Platform(640 + i * 128, 368, 'plataform_media') for i in range(2)] 
+ [Platform(1058 + i * 128, 256, 'plataform_special') for i in range(1)])

drones = [Drone(600, 100), Drone(700, 200), Drone(400, 150)]
menu_buttons = [{"label": "Play", "action": "play", "rect": Rect((WIDTH//2 - 60, 200), (120, 40))},
    {"label": "Exit", "action": "exit", "rect": Rect((WIDTH//2 - 60, 260), (120, 40))}]

# Draw

def draw():
    if session.state == 'menu':
        draw_menu()
    elif session.state == 'playing':
        background.draw()
        for p in platforms:
            p.draw()
        for d in drones:
            d.draw()
        neo_nina.draw()
    elif session.state == 'victory':
        session.draw_victory_screen()
    elif session.state == 'gameover':
        draw_game_over()

# Update

def update():
    if session.state == 'playing':
        neo_nina.update()
        for d in drones:
            d.update()
        if keyboard.h:
            neo_nina.hacking()

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
