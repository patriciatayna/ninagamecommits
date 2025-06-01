import time
from mod.config import GRAVITY, WIDTH, slower_anim_nina
from pgzero.actor import Actor
from pgzero.keyboard import keyboard
from mod.levels import change_level, platforms

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

    def draw(self):
        self.actor.draw()

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

        if self.actor.x > WIDTH - 48:
            change_level()

        self.animate()

    def animate(self):
        now = time.time()
        if now - self.last_frame_time >= self.animation_delay:
            frames = self.animations[self.action]
            self.frame = (self.frame + 1) % len(frames)
            self.actor.image = frames[self.frame]
            self.last_frame_time = now
