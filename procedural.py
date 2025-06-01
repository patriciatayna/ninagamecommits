import pgzrun, random, time
from pygame import Rect

WIDTH = 1280
HEIGHT = 720

GRAVITY = 0.4
slower_anim_nina = 3
game_level = 1
bg_game = None

bg_music = 'Hardware_Prototype.wav'
bg_menu = Actor("background_menu", (WIDTH//2, HEIGHT//2))

neon_nina = {
    "actor": Actor('neon_nina_idle_1', (WIDTH//2, HEIGHT//2)),
    "vx": 0,
    "vy": 0,
    "speed": 4,
    "on_ground": False,
    "action": 'idle',
    "frame": 0,
    "last_frame_time": time.time(),
    "animation_delay": slower_anim_nina * 0.1,
    "allies": [],
    "hp": 100,
    "animations": {
        'idle': ['neon_nina_idle_1', 'neon_nina_idle_2'],
        'jump': ['neon_nina_jump_1', 'neon_nina_jump_2', 'neon_nina_jump_3'],
        'run': ['neon_nina_run_1', 'neon_nina_run_2'],
        'hit': ['neon_nina_hit']
    }
}

platforms = []
drones = []
session_state = 'menu'

menu_buttons = [
    {"label": "Play", "action": "play", "rect": Rect((WIDTH // 2 - 60, 200), (120, 40))},
    {"label": "Exit", "action": "exit", "rect": Rect((WIDTH // 2 - 60, 260), (120, 40))}
]

levels = [
    {"phase": 1, "bg": "background_city_1"},
    {"phase": 2, "bg": "background_city_2"},
    {"phase": 3, "bg": "background_city_2"}
]
current_level_index = 0

def animate_neon_nina():
    now = time.time()
    if now - neon_nina["last_frame_time"] >= neon_nina["animation_delay"]:
        frames = neon_nina["animations"][neon_nina["action"]]
        neon_nina["frame"] = (neon_nina["frame"] + 1) % len(frames)
        neon_nina["actor"].image = frames[neon_nina["frame"]]
        neon_nina["last_frame_time"] = now

def update_neon_nina():
    a = neon_nina["actor"]
    if not neon_nina["on_ground"]:
        neon_nina["action"] = 'jump'
    elif keyboard.left:
        neon_nina["vx"], a.flip_x, neon_nina["action"] = -neon_nina["speed"], True, 'run'
    elif keyboard.right:
        neon_nina["vx"], a.flip_x, neon_nina["action"] = neon_nina["speed"], False, 'run'
    else:
        if keyboard.up:
            neon_nina["vy"], neon_nina["on_ground"], neon_nina["action"] = -12, False, 'jump'
        else:
            neon_nina["vx"], neon_nina["action"] = 0, 'idle'

    neon_nina["vy"] += GRAVITY
    a.x += neon_nina["vx"]
    a.y += neon_nina["vy"]
    a.x = max(0, min(WIDTH, a.x))
    neon_nina["on_ground"] = False

    for p in platforms:
        if a.colliderect(p["rect"]) and neon_nina["vy"] >= 0:
            a.y = p["rect"].top - a.height // 2
            neon_nina["vy"], neon_nina["on_ground"] = 0, True

    if a.x > WIDTH - 48:
        change_level()

    animate_neon_nina()

def update():
    global session_state
    if session_state == 'playing':
        update_neon_nina()
        for d in drones:
            d["actor"].y += d["vy"]
            if d["actor"].y < d["upper_limit"] or d["actor"].y > d["lower_limit"]:
                d["vy"] *= -1
            if d["actor"].distance_to(neon_nina["actor"]) < 200:
                screen.draw.line(d["actor"].pos, neon_nina["actor"].pos, "yellow")

def draw_hud():
    x, y = 20, 20
    width, height = 200, 24
    hp_ratio = neon_nina["hp"] / 100
    screen.draw.rect(Rect((x, y), (width, height)), "white")
    screen.draw.filled_rect(Rect((x+2, y+2), (int((width-4)*hp_ratio), height-4)), "red")
    screen.draw.text("HP", (x - 30, y), fontsize=24, color="white")
    icon_x = x + width + 40
    icon_y = y + height // 2
    spacing = 40
    for i in range(len(neon_nina["allies"])):
        screen.draw.image('ally_icon', (icon_x + i*spacing, icon_y), anchor=("center", "center"))
    screen.draw.text(f"Phase {levels[current_level_index]['phase']}", center=(WIDTH // 2, 30),
                     fontsize=36, color="cyan", shadow=(1, 1))

def draw():
    if session_state == 'menu':
        draw_menu()
    elif session_state == 'playing':
        if bg_game: bg_game.draw()
        for p in platforms: p["actor"].draw()
        for d in drones: d["actor"].draw()
        neon_nina["actor"].draw()
        draw_hud()
    elif session_state == 'victory':
        draw_victory()
    elif session_state == 'gameover':
        draw_game_over()

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

def on_mouse_down(pos):
    global session_state
    if session_state == 'menu':
        for button in menu_buttons:
            if button["rect"].collidepoint(pos):
                if button["action"] == "play":
                    start_game()
                elif button["action"] == "exit":
                    quit()

def on_key_down(key):
    global session_state
    if session_state in ['gameover', 'victory'] and key == keys.RETURN:
        reset_session()

def reset_session():
    global session_state
    session_state = 'menu'

def start_game():
    global session_state, platforms, drones, bg_game
    session_state = 'playing'
    neon_nina["actor"].pos = (100, 400)
    neon_nina["vx"] = neon_nina["vy"] = 0
    neon_nina["hp"] = 100
    neon_nina["allies"] = []

    change_level(first=True)

def change_level(first=False):
    global current_level_index, platforms, drones, bg_game
    if not first:
        current_level_index += 1
        if current_level_index >= len(levels):
            session_state = 'victory'
            return
    bg_game = Actor(levels[current_level_index]["bg"], (WIDTH//2, HEIGHT//2))

    if current_level_index == 0:
        platforms = [{"actor": Actor('plataform_ground', (128 + i * 128, 512)),
                      "rect": Actor('plataform_ground', (128 + i * 128, 512))._rect} for i in range(3)]
        drones[:] = [make_drone(600, 100), make_drone(700, 200), make_drone(400, 150)]
    elif current_level_index == 1:
        platforms = [{"actor": Actor('plataform_ground', (128 + i * 128, 512)),
                      "rect": Actor('plataform_ground', (128 + i * 128, 512))._rect} for i in range(4)]
        drones[:] = [make_drone(600, 100), make_drone(700, 200)]
    elif current_level_index == 2:
        platforms = [{"actor": Actor('plataform_media', (100 + i * 200, 400)),
                      "rect": Actor('plataform_media', (100 + i * 200, 400))._rect} for i in range(3)]
        drones[:] = [make_drone(500, 150), make_drone(300, 200), make_drone(800, 180)]

def make_drone(x, y):
    vy = random.choice([-1.5, 1.5]) * random.uniform(0.8, 1.6)
    return {
        "actor": Actor('enemy_drone', (x, y)),
        "vy": vy,
        "upper_limit": y - 40,
        "lower_limit": y + 40
    }

pgzrun.go()
