# region Imports
import pgzrun
import random
from pygame import Rect
# endregion
# region Constants
WIDTH = 1080
HEIGHT = 720
TITLE = "Neo-Nina and The Systems"
GRAVITY = 0.5
MAX_ALLIES = 3
MAX_HEALTH = 100
# endregion
# region Game Control
class GameSession:
    state = 'menu'
    volume_on = True
    level = 1
    health = MAX_HEALTH
    boss_health = MAX_HEALTH
    in_transition = False
    transition_alpha = 0
    total_levels = 3

    @staticmethod
    def next_level():
        if GameSession.level < GameSession.total_levels:
            GameSession.level += 1
            GameSession.in_transition = True
            GameSession.transition_alpha = 255
        else:
            GameSession.state = 'menu'

    @staticmethod
    def reset_to_menu():
        GameSession.state = 'menu'
        GameSession.level = 1
        GameSession.transition_alpha = 0
        GameSession.in_transition = False
        GameSession.health = MAX_HEALTH
        GameSession.boss_health = MAX_HEALTH
# endregion
# region Platform
class Platform:
    def __init__(self, x, y, sprite):
        self.actor = Actor(sprite, (x, y))
    def draw(self):
        self.actor.draw()
    def rect(self):
        return self.actor._rect
# endregion
# region NeoNina
class NeoNina:
    def __init__(self, x, y):
        self.actor = Actor('neo_nina_idle', (x, y))
        self.vx = 0
        self.vy = 0
        self.speed = 3
        self.on_ground = False
        self.action = 'idle'
        self.animations = {'idle': ['neo_nina_idle'],
                           'run': ['neo_nina_run'],
                           'walk': ['neo_nina_walk'],
                           'jump': ['neo_nina_jump'],
                           'hacking': ['neo_nina_hacking'],
                           'hit': ['neo_nina_hit'],
                           'death': ['neo_nina_death']}
        self.frame = 0
        self.counter = 0
        self.delay = 6
        self.allies = []

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

        if self.actor.y > HEIGHT + 100:
            GameSession.state = 'game_over'

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
                    break

    def draw(self):
        self.actor.draw()

# endregion
# region Drone
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
        elif self.actor.distance_to(neo_nina.actor) < 100:
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
# endregion
# region Initialization
background = Actor('background')
menu_buttons = [
    {"label": "Play", "action": "play", "rect": Rect((WIDTH//2 - 60, 200), (120, 40))},
    {"label": "Volume", "action": "volume", "rect": Rect((WIDTH//2 - 60, 260), (120, 40))},
    {"label": "Mute", "action": "mute", "rect": Rect((WIDTH//2 - 60, 320), (120, 40))},
    {"label": "Exit", "action": "exit", "rect": Rect((WIDTH//2 - 60, 380), (120, 40))}
]
neo_nina = NeoNina(100, 400)
platforms = [
    Platform(100 + 60 * i, 500, 'plataforma_chao') for i in range(3)
] + [
    Platform(420 + 60 * i, 350, 'plataforma_media') for i in range(4)
] + [
    Platform(760 + 60 * i, 290, 'plataforma_movel') for i in range(3)
]
drones = [Drone(600, 100), Drone(700, 200), Drone(400, 150)]
laser_attacks = []
# endregion
# region Draw Functions
def draw():
    if GameSession.state == 'menu':
        draw_menu()
    elif GameSession.state == 'playing':
        draw_playing()
    elif GameSession.state == 'game_over':
        draw_game_over()

def draw_menu():
    screen.fill((10, 10, 20))
    screen.draw.text("Neo-Nina and the Systems", center=(WIDTH//2, 100), fontsize=40, color="white")
    for button in menu_buttons:
        screen.draw.filled_rect(button["rect"], "gray")
        screen.draw.text(button["label"], center=button["rect"].center, fontsize=30, color="white")

def draw_game_over():
    screen.fill((20, 0, 0))
    screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2 - 40), fontsize=80, color="red")
    screen.draw.text("Press ENTER to return to menu", center=(WIDTH // 2, HEIGHT // 2 + 40), fontsize=40, color="white")

def draw_playing():
    background.draw()
    for p in platforms: p.draw()
    for d in drones: d.draw()
    for laser in laser_attacks:
        screen.draw.line((laser[0], laser[1]), (laser[0], HEIGHT), "red")
    neo_nina.draw()
    screen.draw.text("Use arrow keys to move | H to hack", (10, 10), color="black")
# endregion
# region Update
def update():
    if GameSession.state == 'playing':
        neo_nina.update()
        for d in drones: d.update()
        for laser in laser_attacks:
            if neo_nina.actor.collidepoint(laser):
                print("Neo-Nina hit by laser!")
        if keyboard.h:
            neo_nina.hacking()
    elif GameSession.state == 'game_over' and keyboard.RETURN:
        GameSession.reset_to_menu()
# endregion
# region Input Handling
def on_mouse_down(pos):
    if GameSession.state == 'menu':
        for button in menu_buttons:
            if button["rect"].collidepoint(pos):
                if button["action"] == "play":
                    GameSession.state = 'playing'
                elif button["action"] == "unmute":
                    GameSession.volume_on = True
                elif button["action"] == "mute":
                    GameSession.volume_on = False
                elif button["action"] == "exit":
                    quit()
# endregion
pgzrun.go()
