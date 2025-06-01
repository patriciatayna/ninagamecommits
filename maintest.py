import pgzrun
import random
import math

WIDTH = 1080
HEIGHT = 720
TITLE = "Neo-Nina and The Systems"

GRAVITY = 0.5
MAX_ALLIES = 3

background = Actor('background')

class Plataform:
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
            # 'idle': ['neo_nina_idle1', 'neo_nina_idle2'],
            # 'walk': ['neo_nina_walk1', 'neo_nina_walk2'],
            # 'jump': ['neo_nina_jump1', 'neo_nina_jump2']
        }
        self.frame = 0
        self.counter = 0
        self.delay = 6
        self.allies = []

    def update(self):
        if keyboard.left:
            self.vx = -self.speed
            self.acao = 'walk'
            self.actor.flip_x = True
        elif keyboard.right:
            self.vx = self.speed
            self.action = 'walk'
            self.actor.flip_x = False
        else:
            self.vx = 0
            self.action = 'idle'

        if keyboard.up and self.no_chao:
            self.vy = -14
            self.on_ground = False
            self.action = 'jump'

        self.vy += GRAVITY
        self.actor.x += self.vx
        self.actor.y += self.vy

        # Lim horiz
        self.actor.x = max(0, min(WIDTH, self.actor.x))

        # Coll plataforms
        self.on_ground = False
        for p in plataforms:
            if self.actor.colliderect(p.rect()) and self.vy >= 0:
                self.actor.y = p.rect().top
                self.vy = 0
                self.no_chao = True
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
                if len(self.allies) < MAX_ALLY:
                    d.ally = True
                    self.allies.append(d)
                    break

    def draw(self):
        self.actor.draw()

class Drone:
    def __init__(self, x, y):
        self.actor = Actor('drone_inimigo', (x, y))
        self.vy = random.choice([-1, 1]) * random.uniform(0.5, 1.2)
        self.lim_sup = y - 40
        self.lim_inf = y + 40
        self.ally = False
        self.target = None

    def update(self):
        # Mov vertical
        self.actor.y += self.vy
        if self.actor.y < self.lim_sup or self.actor.y > self.lim_inf:
            self.vy *= -1

        if self.ally:
            self.search_target()
        else:
            # simple enemy behaviour
            if self.actor.distance_to(neo_nina.actor) < 100:
                self.atacar(neo_nina.actor)

    def search_target(self):
        for d in drones:
            if not d.ally and self.actor.distance_to(d.actor) < 150:
                self.alvo = d
                break

        if self.target:
            dx = self.target.actor.x - self.actor.x
            dy = self.target.actor.y - self.actor.y
            self.actor.x += 0.8 if dx > 0 else -0.8
            self.actor.y += 0.5 if dy > 0 else -0.5

            if self.actor.distance_to(self.alvo.actor) < 20:
                self.attack(self.target.actor)

    def attack(self, alvo):
        # visual effect
        screen.draw.line(self.actor.pos, alvo.pos, "yellow")

    def draw(self):
        self.actor.draw()

# Instances
neo_nina = NeoNina(100, 400)

plataforms = [
    Plataform(100, 500, 'plataforma_chao'),
    Plataform(160, 500, 'plataforma_chao'),
    Plataform(220, 500, 'plataforma_chao'),
    Plataform(420, 350, 'plataforma_media'),
    Plataform(480, 350, 'plataforma_media'),
    Plataform(540, 350, 'plataforma_media'),
    Plataform(600, 350, 'plataforma_media'),
    Plataform(760, 290, 'plataforma_movel'),
    Plataform(820, 290, 'plataforma_movel'),
    Plataform(880, 290, 'plataforma_movel'),
]

drones = [
    Drone(600, 100),
    Drone(700, 200),
    Drone(400, 150)
]

laser_attacks = []

def update():
    neo_nina.update()
    for d in drones:
        d.update()

    for laser in laser_attacks:
        if neo_nina.actor.collidepoint(laser):
            print("Neo-Nina hit by laser!")

    if keyboard.h:
        neo_nina.hacking()

def draw():
    background.draw()

    for p in plataforms:
        p.draw()
    
    for d in drones:
        d.draw()
    
    for laser in laser_attacks:
        screen.draw.line((laser[0], laser[1]), (laser[0], HEIGHT), "red")

    neo_nina.draw()
    screen.draw.text("press arrow keys to walk and jump | press H to hack", (10, 10), color="black")

pgzrun.go()
