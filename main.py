#Игра для ямпа - бесконечный рогалик в теримнале
import time

#создание поля игры
wight = 60
hight = 20

def make_empty_matrix():
    return [[" " for _ in range(wight)] for _ in range(hight)]

#отрисовка поля
def draw(matrix):
    frame = '\n'.join([''.join(row) for row in matrix])

    print('\033[H' + frame, end='')

def main():
    print('\033[2J', end = '')

    while True:
        matrix = make_empty_matrix()

        matrix[10][30] = '@'

        draw(matrix)

        time.sleep(0.03)

if __name__ == '__main__':
    main()