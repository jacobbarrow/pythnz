import os, time, random

NORTH = 1
EAST = 2
SOUTH = 3
WEST = 4
DIRECTIONS = [NORTH, EAST, SOUTH, WEST]

FOOD = 'food'

class Snake():
    def __init__(self, x, y, colour, name, game, is_ai=True):
        self.game = game
        self.colour = colour
        self.name = name
        self.score = 0
        self.is_alive = True
        self.direction = NORTH
        self.uninterrupted_distance = 0
        self.is_ai = is_ai
    
        self.coords = [[x, y], [x, y+1], [x, y+2]]

        for coord in self.coords:
            game.fillCell(coord, self.colour)

    
    def getNextCell(self, direction=None):
        if direction == None:
            direction = self.direction

        x, y = self.coords[0]
        if direction == NORTH:
            y -= 1
        elif direction == SOUTH:
            y += 1
        elif direction == EAST:
            x += 1
        else:
            x -= 1
        
        return [x,y ]

    def move(self):
        if self.is_alive:
            next_cell = self.getNextCell()

            if self.game.cellIsFree(next_cell):
                if not self.game.cellIsFood(next_cell):
                    self.game.clearCell(self.coords[-1])
                    del self.coords[-1]
                else:
                    self.score += 1
                    self.game.addFood()

                self.game.fillCell(next_cell, self.colour)
                self.coords.insert(0, next_cell)
                return True
            else:
                self.kill()
                return False
        else:
            return False
    
    def predictDirection(self):
        # If an adjacent cell has food, head towards it
        for direction in DIRECTIONS:
            if self.game.cellIsFood(self.getNextCell(direction)):
                return direction

        # If the current row has food in it, head that way
        x, y = self.coords[0]
        row = self.game.getRow(y)
        if FOOD in row:
            # If it's to the west and the next cell is empty, send it west
            if x > row.index(FOOD) and self.game.cellIsFree(self.getNextCell(WEST)):
                return WEST
            # Otherwise, it's in the east
            elif self.game.cellIsFree(self.getNextCell(EAST)):
                return EAST

        column = self.game.getColumn(x)
        if FOOD in column:
            # If it's to the north and the next cell is empty, send it north
            if y > column.index(FOOD) and self.game.cellIsFree(self.getNextCell(NORTH)):
                return NORTH
            # Otherwise, it's in the north
            elif self.game.cellIsFree(self.getNextCell(SOUTH)):
                return SOUTH

        # If the cell ahead is empty, keep going (unless it's been going that way for a while)
        if self.game.cellIsFree(self.getNextCell()) and self.uninterrupted_distance < 10:
            self.uninterrupted_distance += 1
            return self.direction
        # If not, pick a clear adjacent cell at random
        else:
            self.uninterrupted_distance = 0
            for direction in random.sample(DIRECTIONS, 4):
                if self.game.cellIsFree(self.getNextCell(direction)):
                    return direction

        # If there's no clear cells, just keep going (and die)
        return self.direction

    def setDirection(self, direction):
        if not (self.direction == NORTH and direction == SOUTH):
            self.direction = direction

    def kill(self):
        # Add another bit of food to the board
        self.game.addFood()

        for coord in self.coords:
            self.game.fillCell(coord, ' ')
        self.is_alive = False        

    def __str__(self):
        string = ''
        for coord in self.coords:
            string += str(coord[0]) + ',' + str(coord[1])
            string += ' '
        return string

    def __eq__(self, other):
        return self.score == other.score

    def __lt__(self, other):
        return self.score < other.score


class Game():
    def __init__(self, width, height):
        self.live_snakes = []
        self.dead_snakes = []
        self.height = height
        self.width = width
        self.board = [[' ' for _ in range(width)] for _ in range(height)]
        self.addFood()
        self.is_finished = False

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
        self.live_snakes.append(snake)

    def step(self):
        for snake in self.live_snakes:
            if snake.is_ai:
                snake.setDirection(snake.predictDirection())
            snake.move()
        
            if not snake.is_alive:
                self.live_snakes.remove(snake)
                self.dead_snakes.append(snake)

        if self.hasNoFood():
            self.addFood()

        if len(self.live_snakes) == 0:
            self.is_finished = True
    
    def loop(self, delay=0.15):
        while not self.is_finished:
            self.step()
            time.sleep(delay)


if __name__ == '__main__':
    FOOD = 'x'
    g = Game(width=34, height=15)

    g.addSnake(Snake(8, 1, 'a', 'Amy', g))
    g.addSnake(Snake(8, 3, 'b', 'Bob', g))
    g.addSnake(Snake(8, 5, 'c', 'Charlie', g))
    g.addSnake(Snake(8, 7, 'd', 'David', g))
    g.addSnake(Snake(8, 9, 'e', 'Ellen', g))

    while not g.is_finished:
        # Clear the old frame
        os.system('clear')
        # Display the new one
        g.show()

        snakes_alive = 0
        g.step()

        


        print('Live Snakes:')
        for snake in g.live_snakes:
            print(snake.name + ': ' + str(snake.score))

        print('Dead Snakes:')
        for snake in g.dead_snakes:
            print(snake.name + ': ' + str(snake.score))


        time.sleep(.1) # Any lower than .15 and it gets a bit tempermental
