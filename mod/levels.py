from mod.config import WIDTH, HEIGHT
from characters.level import Level
from characters.platform import Platform
from characters.enemy_drone import EnemyDrone

levels = [
    Level(1, 'background_city_1'),
    Level(2, 'background_city_2'),
    Level(3, 'background_city_2')
]

current_level_index = 0

def change_level(session):
    global current_level_index
    current_level_index += 1
    if current_level_index >= len(levels):
        session.state = 'victory'
        return
    current_level = levels[current_level_index]
    current_level.start()
    session.neon_nina.actor.pos = (100, HEIGHT // 2)
    session.neon_nina.vx = session.neon_nina.vy = 0
    if current_level_index == 1:
        return (
            [Platform(128 + i * 128, 512, 'plataform_ground') for i in range(4)],
            [EnemyDrone(600, 100), EnemyDrone(700, 200)]
        )
    elif current_level_index == 2:
        return (
            [Platform(100 + i * 200, 400, 'plataform_media') for i in range(3)],
            [EnemyDrone(500, 150), EnemyDrone(300, 200), EnemyDrone(800, 180)]
        )
    return [], []