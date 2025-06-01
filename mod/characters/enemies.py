import random
from pgzero.actor import Actor
from mod.config import HEIGHT
from mod.game_session import session

class EnemyDrone:
    def __init__(self, x, y):
        self.actor = Actor('enemy_drone', (x, y))
        self.vy = random.choice([-1.5, 1.5]) * random.uniform(0.8, 1.6)
        self.upper_limit = y - 40
        self.lower_limit = y + 40
        self.ally = False
        self.target = None

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


class WreckerBoss:
    def __init__(self, x, y):
        self.actor = Actor('eggwrecker_1', (x, y))
        self.vy = random.choice([-1.5, 1.5]) * random.uniform(0.8, 1.6)
        self.upper_limit = y - 40
        self.lower_limit = y + 40
        self.target = session.neon_nina.actor

    def update(self):
        self.actor.y += self.vy
        if self.actor.y < self.upper_limit or self.actor.y > self.lower_limit:
            self.vy *= -1
        if self.actor.distance_to(self.target) < 200:
            self.attack(self.target)

    def attack(self, target):
        screen.draw.line(self.actor.pos, target.pos, "yellow")

    def draw(self):
        self.actor.draw()