import random

NORTH = 1
EAST = 2
SOUTH = 3
WEST = 4
DIRECTIONS = [NORTH, EAST, SOUTH, WEST]

FOOD = 'food'
class Snake():
    def __init__(self, colour, name, is_ai=True):
        self.room = None
        self.colour = colour
        self.name = name
        self.score = 0
        self.is_ai = is_ai
        self.direction = EAST
    
        self.coords = []
        self.reserved_coords = []

        self.uninterrupted_distance = 0

    def generate(self):
        self.ticks_until_alive = 5
        self.direction = EAST

        slot = False
        slot_found = False
        while not slot_found:
            y = random.randint(0, self.room.height)
            for x in range(y):
                slot_found = True
                for i in range(5):
                    if not self.room.cellIsFree([x+i, y]):
                        slot_found = False

        
        self.coords = [[x+2, y], [x+1, y], [x, y]]
        self.reserved_coords = [[x+3, y], [x+4, y]]
        for coord in self.coords:
            self.room.fillCell(coord, self.colour)
        for coord in self.reserved_coords:
            self.room.fillCell(coord, 'reserved')

    def unreserve(self):
        for coord in self.reserved_coords:
            self.room.clearCell(coord)

    
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
        if self.ticks_until_alive == -1:
            next_cell = self.getNextCell()

            if self.room.cellIsFree(next_cell):
                if not self.room.cellIsFood(next_cell):
                    self.room.clearCell(self.coords[-1])
                    del self.coords[-1]
                else:
                    self.score += 1
                    self.room.addFood()

                self.room.fillCell(next_cell, self.colour)
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
            if self.room.cellIsFood(self.getNextCell(direction)):
                return direction

        # If the current row has food in it, head that way
        x, y = self.coords[0]
        row = self.room.getRow(y)
        if FOOD in row:
            # If it's to the west and the next cell is empty, send it west
            if x > row.index(FOOD) and self.room.cellIsFree(self.getNextCell(WEST)):
                return WEST
            # Otherwise, it's in the east
            elif self.room.cellIsFree(self.getNextCell(EAST)):
                return EAST

        column = self.room.getColumn(x)
        if FOOD in column:
            # If it's to the north and the next cell is empty, send it north
            if y > column.index(FOOD) and self.room.cellIsFree(self.getNextCell(NORTH)):
                return NORTH
            # Otherwise, it's in the north
            elif self.room.cellIsFree(self.getNextCell(SOUTH)):
                return SOUTH

        # If the cell ahead is empty, keep going (unless it's been going that way for a while)
        if self.room.cellIsFree(self.getNextCell()) and self.uninterrupted_distance < 10:
            self.uninterrupted_distance += 1
            return self.direction
        # If not, pick a clear adjacent cell at random
        else:
            self.uninterrupted_distance = 0
            for direction in random.sample(DIRECTIONS, 4):
                if self.room.cellIsFree(self.getNextCell(direction)):
                    return direction

        # If there's no clear cells, just keep going (and die)
        return self.direction

    def setDirection(self, direction):
        # Make sure the snake can't go back on itself
        if not self.direction == direction+2 and not self.direction == direction-2:
            self.direction = direction

    def kill(self):
        for coord in self.coords:
            self.room.fillCell(coord, ' ')
        self.generate()


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
