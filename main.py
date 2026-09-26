import random
import time
import msvcrt
import os
import math

widht = 200
height = 40


class Entity:
    def __init__(self, x: int, y: int, symbol: str):
        self.x = x
        self.y = y
        self.symbol = symbol

    def draw(self, matrix: list[list[str]]):
        if 0 <= self.y < height and 0 <= self.x < widht:
            matrix[self.y][self.x] = self.symbol


class Player(Entity):
    def __init__(self, x: int, y: int, hp: int = 5):
        super().__init__(x, y, symbol="@")
        self.hp = hp
        self.max_hp = hp
        self.xp = 0
        self.lvl = 1
        self.xp_to_next_lvl = 5

        # Посох
        self.staff_lvl = 1
        self.staff_dmg = 1
        self.staff_cd = 15

        # Чеснок
        self.garlic_lvl = 0
        self.garlic_dmg = 0
        self.garlic_radius = 0
        self.garlic_cd = 15

    def move(self, key: str):
        if key == 'w' and self.y > 1: self.y -= 1
        if key == 's' and self.y < height - 2: self.y += 1
        if key == 'a' and self.x > 1: self.x -= 1
        if key == 'd' and self.x < widht - 2: self.x += 1


class Enemy(Entity):
    def __init__(self, x: int, y: int, hp: int = 1):
        super().__init__(x, y, symbol="E")
        self.hp = hp
        self.tick = 0
        self.move_rate = 8

    def update(self, target_x: int, target_y: int):
        self.tick += 1
        if self.tick % self.move_rate != 0: return
        if self.x < target_x:
            self.x += 1
        elif self.x > target_x:
            self.x -= 1
        if self.y < target_y:
            self.y += 1
        elif self.y > target_y:
            self.y -= 1


class Exp(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, symbol='.')


class Projectile(Entity):
    def __init__(self, x: int, y: int, target_x: int, target_y: int, damage: int):
        super().__init__(x, y, symbol="*")
        self.damage = damage
        self.rx = float(x)
        self.ry = float(y)
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.dx = dx / dist
            self.dy = dy / dist
        else:
            self.dx = 0
            self.dy = 0

    def update(self):
        self.rx += self.dx
        self.ry += self.dy
        self.x = int(round(self.rx))
        self.y = int(round(self.ry))


def spawn_enemy(frames) -> Enemy:
    # Мобы становятся жирнее со временем
    bonus_hp = frames // 900
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        return Enemy(x=random.randint(1, widht - 2), y=1, hp=1 + bonus_hp)
    elif side == 'bottom':
        return Enemy(x=random.randint(1, widht - 2), y=height - 2, hp=1 + bonus_hp)
    elif side == 'left':
        return Enemy(x=1, y=random.randint(1, height - 2), hp=1 + bonus_hp)
    else:
        return Enemy(x=widht - 2, y=random.randint(1, height - 2), hp=1 + bonus_hp)


def get_closest_enemy(player_x, player_y, enemies):
    if not enemies: return None
    closest = None
    min_dist = float('inf')
    for enemy in enemies:
        dist = (enemy.x - player_x) ** 2 + (enemy.y - player_y) ** 2
        if dist < min_dist:
            min_dist = dist
            closest = enemy
    return closest


def get_empty_matrix():
    matrix = []
    for y in range(height):
        row = []
        for x in range(widht):
            if y == 0 or y == height - 1 or x == 0 or x == widht - 1:
                row.append('#')
            else:
                row.append(' ')
        matrix.append(row)
    return matrix


def draw(matrix):
    frame = '\n'.join([''.join(row) for row in matrix])
    print('\033[H' + frame, end='')


def show_start_screen():
    banner = """=============================================
         ДОБРО ПОЖАЛОВАТЬ В РОГАЛИК!         
=============================================

 ВАЖНО: Переключите клавиатуру на EN!

 Управление:
   [W] [A] [S] [D]  - Движение персонажа (@)
   [Q]              - Выход из игры

=============================================
 Нажмите любую клавишу для начала игры..."""
    print(banner)
    msvcrt.getch()
    os.system('cls')


def main():
    show_start_screen()
    player = Player(x=widht // 2, y=height // 2)

    enemies = []
    bullets = []
    exp_drops = []
    frames = 0

    try:
        while True:
            frames += 1

            # Спавн мобов
            if frames % 30 == 0:
                enemies.append(spawn_enemy(frames))

            # Стрельба посоха
            if frames % player.staff_cd == 0 and len(enemies) > 0:
                target = get_closest_enemy(player.x, player.y, enemies)
                if target:
                    projectile = Projectile(player.x, player.y, target.x, target.y, player.staff_dmg)
                    bullets.append(projectile)

            # Чеснок (выровнен на один уровень с посохом)
            if player.garlic_lvl > 0 and frames % player.garlic_cd == 0:
                for enemy in enemies.copy():
                    dist = math.hypot(enemy.x - player.x, enemy.y - player.y)
                    if dist <= player.garlic_radius:
                        enemy.hp -= player.garlic_dmg
                        if enemy.hp <= 0:
                            exp_drops.append(Exp(enemy.x, enemy.y))
                            enemies.remove(enemy)

            # Управление
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('ascii', errors='ignore').lower()
                if key == 'q':
                    break
                player.move(key)

            # Враги (Урон по игроку исправлен с bullet.damage на 1)
            for enemy in enemies.copy():
                enemy.update(player.x, player.y)
                if enemy.x == player.x and enemy.y == player.y:
                    player.hp -= 1
                    enemies.remove(enemy)

            # Пули
            for bullet in bullets.copy():
                bullet.update()
                if bullet.x <= 0 or bullet.x >= widht - 1 or bullet.y <= 0 or bullet.y >= height - 1:
                    bullets.remove(bullet)
                    continue

                hit = False
                for enemy in enemies.copy():
                    if abs(bullet.x - enemy.x) <= 1 and abs(bullet.y - enemy.y) <= 1:
                        enemy.hp -= bullet.damage
                        hit = True
                        if enemy.hp <= 0:
                            exp_drops.append(Exp(enemy.x, enemy.y))
                            enemies.remove(enemy)
                        break

                if hit:
                    bullets.remove(bullet)

            # СБОР ОПЫТА (вынесен из цикла пуль)
            for xp in exp_drops.copy():
                if xp.x == player.x and xp.y == player.y:
                    player.xp += 1
                    exp_drops.remove(xp)

            # ЛЕВЕЛ АП
            if player.xp >= player.xp_to_next_lvl:
                player.lvl += 1
                player.xp = 0
                player.xp_to_next_lvl = 5 * player.lvl

                is_maxed = (player.staff_lvl == 5 and player.garlic_lvl == 5 and player.max_hp == 10)

                if is_maxed:
                    player.hp = player.max_hp
                else:
                    # Очищаем буфер клавиатуры, чтобы "зажатый" WASD не скипал меню
                    while msvcrt.kbhit():
                        msvcrt.getch()

                    os.system('cls')
                    banner= f"""\n=============================================
                    \n          НОВЫЙ УРОВЕНЬ {player.lvl}!               
                    \n=============================================
                    \nВыберите улучшение:"""

                    print(banner)

                    if player.max_hp < 10: print(" [1] Восстановить HP и +1 к Макс HP")
                    else: print(" [1] Полное исцеление (ХП на максимуме)")
                    if player.staff_lvl < 5: print(f" [2] Посох ур.{player.staff_lvl + 1}")
                    else: print(" [2] Посох (МАКСИМУМ)")
                    if player.garlic_lvl == 0: print(" [3] Взять Чеснок (Аура урона)")
                    elif player.garlic_lvl < 5: print(f" [3] Чеснок ур.{player.garlic_lvl + 1}")
                    else: print(" [3] Чеснок (МАКСИМУМ)")
                    print("=============================================\n")

                    while True:
                        if msvcrt.kbhit():
                            choice = msvcrt.getch().decode('ascii', errors='ignore')

                            if choice == '1':
                                if player.max_hp < 10: player.max_hp += 1
                                player.hp = player.max_hp
                                break

                            elif choice == '2' and player.staff_lvl < 5:
                                player.staff_lvl += 1
                                if player.staff_lvl == 2:
                                    player.staff_cd = 10
                                elif player.staff_lvl == 3:
                                    player.staff_dmg = 2
                                elif player.staff_lvl == 4:
                                    player.staff_cd = 5
                                elif player.staff_lvl == 5:
                                    player.staff_dmg = 3
                                break

                            elif choice == '3' and player.garlic_lvl < 5:
                                player.garlic_lvl += 1
                                if player.garlic_lvl == 1:
                                    player.garlic_radius = 2
                                    player.garlic_dmg = 1
                                    player.garlic_cd = 15
                                elif player.garlic_lvl == 2:
                                    player.garlic_radius = 3
                                elif player.garlic_lvl == 3:
                                    player.garlic_cd = 10
                                elif player.garlic_lvl == 4:
                                    player.garlic_cd = 5
                                elif player.garlic_lvl == 5:
                                    player.garlic_radius = 4
                                break

            if player.hp <= 0:
                break

            matrix = get_empty_matrix()

            # аура чеснока
            if player.garlic_lvl > 0:
                for y in range(max(1, player.y - player.garlic_radius),
                               min(height - 1, player.y + player.garlic_radius + 1)):
                    for x in range(max(1, player.x - player.garlic_radius),
                                   min(widht - 1, player.x + player.garlic_radius + 1)):
                        dist = math.hypot(x - player.x, y - player.y)

                        # Рисуем только те клетки, которые лежат на границе радиуса
                        if player.garlic_radius - 1 < dist <= player.garlic_radius:
                            if matrix[y][x] == ' ':
                                matrix[y][x] = '~'

            for xp in exp_drops:
                xp.draw(matrix)
            for enemy in enemies:
                enemy.draw(matrix)
            for bullet in bullets:
                bullet.draw(matrix)
            player.draw(matrix)

            draw(matrix)

            bar_len = 10
            filled = int((player.xp / player.xp_to_next_lvl) * bar_len)
            xp_bar = '█' * filled + '░' * (bar_len - filled)

            print(
                f"\n HP: {player.hp}/{player.max_hp} | LVL {player.lvl} [{xp_bar}] | Врагов: {len(enemies)} | {frames // 30} сек   ",
                end='')

            time.sleep(0.03)

    except KeyboardInterrupt:
        pass
    finally:
        os.system('cls')
        if player.hp <= 0:
            print("\n=============================================")
            print("                  GAME OVER                  ")
            print("=============================================\n")
            print(f"Ты продержался {frames // 30} секунд!")
        else:
            print('\nВыход из игры.')


if __name__ == '__main__':
    main()