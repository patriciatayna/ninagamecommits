import pgzrun
import random
import math

from pygame import Rect

#region Config
WIDTH, HEIGHT = 1280, 720
TITLE = "Neo-Nina and The Systems"
GRAVITY = 0.5
MAX_ALLIES = 3

bg_music = 'Hardware_Prototype.wav'

fullscreen = True
#endregion

# Gaming
class GameSession:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state = 'menu'
        self.level = 1
        self.score = 0
        self.total_game_time = 0
        self.total_allies = 0
        self.victory_fade_alpha = 0
        self.victory_sound_played = False

    def start_game(self):
        self.reset()
        self.state = 'playing'
        sounds.bg_music.play(-1)

    def game_over(self):
        self.state = 'gameover'

    def victory(self):
        self.state = 'victory'

    def next_level(self):
        if self.level < 3:
            self.level += 1
        else:
            self.victory()

    def draw_victory_screen(self):
        screen.fill((10, 10, 20))
        try:
            bg = Actor("victory_bg", center=(WIDTH//2, HEIGHT//2))
            bg.draw()
        except:
            screen.fill((10, 10, 20))

        if self.victory_fade_alpha < 255:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(255 - self.victory_fade_alpha)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            self.victory_fade_alpha = min(self.victory_fade_alpha + 5, 255)

        screen.draw.text("THE END", center=(WIDTH//2, HEIGHT//2 - 80), fontsize=60, color="lightgreen")
        elapsed = int(self.total_game_time)
        screen.draw.text(f"Time: {elapsed} seconds", center=(WIDTH//2, HEIGHT//2), fontsize=35, color="white")
        screen.draw.text(f"Score: {self.score}", center=(WIDTH//2, HEIGHT//2 + 40), fontsize=35, color="white")
        screen.draw.text(f"Allies Hacked: {self.total_allies}", center=(WIDTH//2, HEIGHT//2 + 80), fontsize=35, color="white")
        screen.draw.text("Press Enter to return to menu", center=(WIDTH//2, HEIGHT - 50), fontsize=30, color="white")

        if not self.victory_sound_played:
            sounds.victory.play()
            self.victory_sound_played = True

#region Classes
class Platform:
    def __init__(self, x, y, sprite):
        self.actor = Actor(sprite, (x, y))

    def draw(self):
        self.actor.draw()

    def rect(self):
        return self.actor._rect

class NeoNina:
    def __init__(self, x, y):
        self.actor = Actor('neo_nina_idle', (x, y))
        self.vx = 0
        self.vy = 0
        self.speed = 3
        self.on_ground = False
        self.action = 'idle'
        self.animations = {
            'idle': ['neo_nina_idle']
        }
        self.frame = 0
        self.counter = 0
        self.delay = 6
        self.allies = []
        self.hp = 100

    def update(self):
        if keyboard.left:
            self.vx = -self.speed
            self.action = 'walk'
            self.actor.flip_x = True
        elif keyboard.right:
            self.vx = self.speed
            self.action = 'walk'
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
        self.counter += 1
        if self.counter >= self.delay:
            self.counter = 0
            self.frame = (self.frame + 1) % len(self.animations[self.action])
            self.actor.image = self.animations[self.action][self.frame]

    def hacking(self):
        for d in drones:
            if self.actor.distance_to(d.actor) < 100 and not d.ally:
                if len(self.allies) < MAX_ALLIES:
                    d.ally = True
                    self.allies.append(d)
                    session.total_allies += 1
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
        self.actor = Actor('drone_inimigo', (x, y))
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

# Objects

session = GameSession()
neo_nina = NeoNina(100, 400)
platforms = [Platform(100 + i * 60, 500, 'plataforma_chao') for i in range(3)] 
+ [Platform(420 + i * 60, 350, 'plataforma_media') for i in range(4)] 
+ [Platform(760 + i * 60, 290, 'plataforma_movel') for i in range(3)]

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
        session.total_game_time += 1 / 60
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
