from mod.config import WIDTH, HEIGHT, TITLE
from mod.game_session import GameSession
from mod.levels import levels, change_level
from characters.neo_nina import NeonNina
from characters.enemy_drone import EnemyDrone
from characters.platform import Platform
from characters.ui import draw_menu, draw_game_over, draw_victory, draw_hud

import pgzrun
from pygame import Rect

session = GameSession()
platforms = []
drones = []
current_level = levels[0]
current_level.start()

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

def update():
    if session.state == 'playing':
        session.update()
        for d in drones:
            d.update()

def draw():
    if session.state == 'menu':
        draw_menu(menu_buttons)
    elif session.state == 'playing':
        current_level.draw()
        for p in platforms:
            p.draw()
        for d in drones:
            d.draw()
        session.neon_nina.draw()
        draw_hud(session)
    elif session.state == 'victory':
        draw_victory()
    elif session.state == 'gameover':
        draw_game_over()

def on_mouse_down(pos):
    if session.state == 'menu':
        for button in menu_buttons:
            if button["rect"].collidepoint(pos):
                if button["action"] == "play":
                    session.start_game(drones)
                elif button["action"] == "exit":
                    quit()

def on_key_down(key):
    from pygame import K_RETURN
    if session.state in ['gameover', 'victory'] and key == K_RETURN:
        session.reset()

pgzrun.go()