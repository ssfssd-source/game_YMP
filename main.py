#Игра для ямпа - бесконечный рогалик в теримнале
import random
import time
import msvcrt
import os
from cmath import inf
import math

#создание поля игры
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
        super().__init__(x, y, symbol = "@")
        self.hp = hp
    def move(self, key: str):
        if key == 'w' and self.y > 1:
            self.y -= 1
        if key == 's' and self.y < height - 2:
            self.y += 1
        if key == 'a' and self.x > 1:
            self.x -= 1
        if key == 'd' and self.x < widht - 2:
            self.x += 1


class Enemy(Entity):
    def __init__(self, x: int, y: int, hp: int = 1):
        super().__init__(x, y, symbol = "E")
        self.hp = hp
        self.tick = 0
        self.move_rate = 8
    def update(self, target_x: int, target_y: int):
        self.tick += 1
        if self.tick % self.move_rate != 0:
            return

        if self.x < target_x:
            self.x += 1
        elif self.x > target_x:
            self.x -= 1

        if self.y < target_y:
            self.y += 1
        elif self.y > target_y:
            self.y -= 1


class Projectile(Entity):
    def __init__(self, x: int, y: int, target_x: int, target_y: int):
        super().__init__(x, y, symbol="*")

        # Дробные координаты для точного полета
        self.rx = float(x)
        self.ry = float(y)

        dx = target_x - x
        dy = target_y - y

        dist = math.hypot(dx, dy)

        if dist != 0:
            # Теперь пуля за 1 кадр проходит ровно 1 клетку в ЛЮБОМ направлении.
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

def spawn_enemy() -> Enemy:
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        return Enemy(x = random.randint(1, widht - 2), y = 1)
    elif side == 'bottom':
        return Enemy(x=random.randint(1, widht - 2), y = height-2)
    elif side == 'left':
        return Enemy(x=1, y = random.randint(1,height-2))
    else:
        return Enemy(x = widht-2, y = random.randint(1, height - 2))

def get_closest_enemy(player_x, player_y, enemies):
    if not enemies:
        return None
    closest = None
    min_dist = float('inf')

    for enemy in enemies:
        dist = (enemy.x - player_x)**2 + (enemy.y - player_y)**2
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

#отрисовка поля
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
    frames = 0

    try:
        while True:
            frames += 1
            if frames % 30 == 0:
                enemies.append(spawn_enemy())

            if frames % 15 == 0 and len(enemies) > 0:
                target = get_closest_enemy(player.x, player.y, enemies)
                if target:
                    projectile = Projectile(player.x, player.y, target.x, target.y)
                    bullets.append(projectile)

            if msvcrt.kbhit():
                key = msvcrt.getch().decode('ascii', errors='ignore').lower()
                if key == 'q':
                    break
                player.move(key)


            for enemy in enemies.copy():
                enemy.update(player.x, player.y)


                if enemy.x == player.x and enemy.y == player.y:
                    player.hp -= 1
                    enemies.remove(enemy)

            for bullet in bullets.copy():
                bullet.update()

                if bullet.x <= 0 or bullet.x >= widht-1 or bullet.y <=0 or bullet.y >= height-1:
                    bullets.remove(bullet)
                    continue
                hit = False
                for enemy in enemies.copy():
                    if abs(bullet.x - enemy.x) <= 1 and abs(bullet.y - enemy.y) <= 1:
                        enemy.hp -= 1
                        hit = True
                        if enemy.hp <= 0:
                            enemies.remove(enemy)
                        break

                if hit:
                    bullets.remove(bullet)

            if player.hp <= 0:
                break


            matrix = get_empty_matrix()
            player.draw(matrix)


            for enemy in enemies:
                enemy.draw(matrix)

            for bullet in bullets:
                bullet.draw(matrix)

            draw(matrix)

            print(f"\n HP: {player.hp}/5 | Врагов на поле: {len(enemies)} | Время: {frames // 30} сек   ")

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