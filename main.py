#Игра для ямпа - бесконечный рогалик в теримнале
import time
import msvcrt
import os

#создание поля игры
widht = 60
height = 20


class Entity:
    def __init__(self, x: int, y: int, symbol: str):
        self.x = x
        self.y = y
        self.symbol = symbol

    def draw(self, matrix: list[list[str]]):
        if 0 <= self.y < height and 0 <= self.x < widht:
            matrix[self.y][self.x] = self.symbol

class Player(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, symbol = "@")
    def move(self, key: str):
        if key == 'w' and self.y > 0:
            self.y -= 1
        if key == 's' and self.y < height - 2:
            self.y += 1
        if key == 'a' and self.x > 0:
            self.x -= 1
        if key == 'd' and self.x < widht - 2:
            self.x += 1

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
    player = Player(x=widht//2, y=height//2)
    try:
        while True:

            if msvcrt.kbhit():
                key = msvcrt.getch().decode('ascii', errors='ignore').lower()
                if key == 'q':
                    break
                player.move(key)

            matrix = get_empty_matrix()
            player.draw(matrix)
            draw(matrix)

            time.sleep(0.03)
    except KeyboardInterrupt:
        pass
    finally:
        print('\nВыход из игры.')

if __name__ == '__main__':
    main()