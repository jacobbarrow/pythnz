import os, time, random
from .snake import Snake

FOOD = 'food'
COLOURS = ['red', 'blue', 'purple', 'yellow', 'green']
NAMES = ['AI Alice', 'AI Bob', 'AI Catherine', 'AI Dylan', 'AI Eliza']
class Room():
    def __init__(self, width=20, height=20, speed=0.15, name=''):
        self.snakes = []
        self.height = height
        self.width = width
        self.board = [[' ' for _ in range(width)] for _ in range(height)]
        self.addFood()
        self.is_finished = False
        self.speed = speed
        self.name = name

    def getRow(self, index):
        return self.board[index]
    
    def getColumn(self, index):
        return [row[index] for row in self.board]
    
    def fillCell(self, coord, char):
        x, y = coord
        self.board[y][x] = char

    def clearCell(self, coord):
        x, y = coord
        self.board[y][x] = ' '

    def cellIsFree(self, coord):
        x, y = coord

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        else:
            return self.board[y][x] in [' ', FOOD]

    def addFood(self):
        empty_cell_found = False
        while not empty_cell_found:
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            if self.cellIsFree([x,y]):
                empty_cell_found = True

        self.fillCell([x, y], FOOD)

    def cellIsFood(self, coord):
        x, y = coord
        try:
            return self.board[y][x] == FOOD
        except IndexError:
            return False

    def hasNoFood(self):
        for row in self.board:
            if FOOD in row:
                return False

        return True

    def show(self):
        print('+' + '--' * (self.width-1) + '-+')
        for row in self.board:
            print('|' + ' '.join(row) + '|')

        print('+' + '--' * (self.width-1) + '-+')

    def addSnake(self, snake):
        snake.room = self
        snake.colour = COLOURS[len(self.snakes)]
        self.snakes.append(snake)
        snake.generate()

    def removeSnake(self, sid):
        for snake in self.snakes:
            if snake.sid == sid:
                snake.kill(regenerate=False)
                self.snakes.remove(snake)

    def step(self):
        for snake in self.snakes:
            if snake.ticks_until_alive == -1:
                if snake.is_ai:
                    snake.setDirection(snake.predictDirection())
                snake.move()
            elif snake.ticks_until_alive > -1:
                if snake.ticks_until_alive == 0:
                    snake.unreserve()
                snake.ticks_until_alive -=1

           
        if self.hasNoFood():
            self.addFood()

    
    def loop(self):
        while not self.is_finished:
            self.step()
            time.sleep(self.speed)

    def reset(self, num_ais=3):
        self.snakes = []
        for i in range(num_ais):
            self.addSnake(Snake(NAMES[i]))
        self.board = [[' ' for _ in range(self.width)] for _ in range(self.height)]
