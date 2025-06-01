from pygame import Rect
from pgzero.actor import Actor

WIDTH, HEIGHT, TITLE = (1280, 720, "Neo-Nina and The Systems")
GRAVITY, MAX_ALLIES = (0.4, 3)
slower_anim_nina = 3
bg_music = 'Hardware_Prototype.wav'

bg_menu = Actor("background_menu", (WIDTH // 2, HEIGHT // 2))
bg_game = None

menu_buttons = [
    {"label": "Play", "action": "play", "rect": Rect((WIDTH // 2 - 60, 200), (120, 40))},
    {"label": "Exit", "action": "exit", "rect": Rect((WIDTH // 2 - 60, 260), (120, 40))},
]
