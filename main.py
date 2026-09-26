#Игра для ямпа - бесконечный рогалик в теримнале
import random
import time
import msvcrt
import os

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
    frames = 0

    try:
        while True:
            frames += 1
            if frames % 30 == 0:
                enemies.append(spawn_enemy())

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


            if player.hp <= 0:
                break


            matrix = get_empty_matrix()
            player.draw(matrix)


            for enemy in enemies:
                enemy.draw(matrix)

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