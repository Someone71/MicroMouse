import time
global override
override = False

class Cell:
    def __init__(self, cols, rows): # constructor
        self.cols = cols
        self.rows = rows
        self.value = 99
        self.wallN = False
        self.wallS = False
        self.wallE = False
        self.wallW = False
        self.onBestPath = False

    def setOnBestPath(self): # makes something on the best path
        self.onBestPath = True
    
    def setWall(self, direction): # makes a wall at specified direction
        if direction == "N":
            self.wallN = True
        if direction == "S":
            self.wallS = True
        if direction == "E":
            self.wallE = True
        if direction == "W":
            self.wallW = True

    def updateWalls(self): # updates the walls of the cell with the walls of adjacent cells
        if self.cols < cols - 1:
            if array_2d[self.rows][self.cols + 1].wallW:
                self.wallE = True
        if self.cols > 0:
            if array_2d[self.rows][self.cols - 1].wallE:
                self.wallW = True
        if self.rows < rows - 1:
            if array_2d[self.rows + 1][self.cols].wallN:
                self.wallS = True
        if self.rows > 0:
            if array_2d[self.rows - 1][self.cols].wallS:
                self.wallN = True
    
    def setVal(self, value): # sets the value(cells from center) of the cell
        self.value = value
    
    def updateVal(self): # updates the value of the cell with the value of adjacent cells
        if self.cols < cols - 1:
            if array_2d[self.rows][self.cols + 1].value + 1 < self.value and not self.wallE:
                self.value = array_2d[self.rows][self.cols + 1].value + 1
                """
                if the cell to the right of the cell's value + 1 is less than the
                current cell's value, then it sets the current cell's value to the
                right cell's value + 1
                """
        if self.cols > 0:
            if array_2d[self.rows][self.cols - 1].value + 1 < self.value and not self.wallW:
                self.value = array_2d[self.rows][self.cols - 1].value + 1
        if self.rows < rows - 1:
            if array_2d[self.rows + 1][self.cols].value + 1 < self.value and not self.wallS:
                self.value = array_2d[self.rows + 1][self.cols].value + 1
        if self.rows > 0:
            if array_2d[self.rows - 1][self.cols].value + 1 < self.value and not self.wallN:
                self.value = array_2d[self.rows - 1][self.cols].value + 1

# setting up base values and the array itself
rows, cols = 16, 16
array_2d = [[Cell(j, i) for j in range(cols)] for i in range(rows)]
array_2d[7][7].setVal(0)
array_2d[8][7].setVal(0)
array_2d[7][8].setVal(0)
array_2d[8][8].setVal(0)


def printArrayVals(): # prints the array with the values of the cells accounting for if it is on the best path or not and if there are walls in a specified direction
    print("\n\n")
    for i in range (rows):
        print("[ ", end = "")
        for j in range (cols):
            if(array_2d[i][j].value < 10):
                if(array_2d[i][j].wallE and j < 15):
                    if(array_2d[i][j].wallS and i < 15):
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + "\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = "\x1B[4m" + " " + "\x1B[0m" + "|")
                        else:
                            print("\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = "\x1B[4m" + " " + "\x1B[0m" + "|")  
                    else:
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + str(array_2d[i][j].value) + "\x1B[0m", end = " |")
                        else:
                            print(array_2d[i][j].value, end = " |")
                else:
                    if(array_2d[i][j].wallS and i < 15):
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + "\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = "\x1B[4m" + " " + "\x1B[0m" + " ")
                        else:
                            print("\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = "\x1B[4m" + " " + "\x1B[0m" + " ")
                    else:
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + str(array_2d[i][j].value) + "\x1B[0m", end = "  ")
                        else:  
                            print(array_2d[i][j].value, end = "  ")
            
            else:
                if(array_2d[i][j].wallE and j < 15):
                    if(array_2d[i][j].wallS and i < 15):
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + "\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = "|")
                        else:
                            print("\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = "|")
                    else:
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + str(array_2d[i][j].value) + "\x1B[0m", end = "|")
                        else:
                            print(array_2d[i][j].value, end = "|")
                else:
                    if(array_2d[i][j].wallS and i < 15):
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + "\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = " ")
                        else:
                            print("\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = " ")
                    else:
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + str(array_2d[i][j].value) + "\x1B[0m", end = " ")
                        else:
                            print(array_2d[i][j].value, end = " ")
        print ("]")
    print("^^^")
def findDistance(self): # finds the distnce of the furthest cell in a a straight line that is on the best path and moves the mouse to that cell
    if(self.direction == "E"):
        val = 0
        for i in range (1, cols):
            if(self.col < cols - i and self.maze[self.row][self.col + i].onBestPath and not self.maze[self.row][self.col + (i - 1)].wallE):
                val += 1
            else:
                break
        if(val == 1 and diag):
            print("diag")
            diagonal(self)
        else:
            self.moveForward(val)
    if(self.direction == "W"):
        val = 0
        for i in range (1, cols):
            if(self.col > i - 1 and self.maze[self.row][self.col - i].onBestPath and not self.maze[self.row][self.col - (i - 1)].wallW):
                val += 1
            else:
                break
        if(val == 1 and diag):
            print("diag")
            diagonal(self)
        else:
            self.moveForward(val)
    if(self.direction == "N"):
        val = 0
        for i in range (1, rows):
            if(self.row > i - i and self.maze[self.row - i][self.col].onBestPath and not self.maze[self.row - (i - 1)][self.col].wallN):
                val += 1
            else:
                break
        if(val == 1 and diag):
            print("diag")
            diagonal(self)
        else:
            self.moveForward(val)
    if(self.direction == "S"):
        val = 0
        for i in range (1, rows):
            if(self.row < rows - i and self.maze[self.row + i][self.col].onBestPath and not self.maze[self.row + (i - 1)][self.col].wallS):
                val += 1
            else:
                break
        if(val == 1 and diag):
            print("diag")
            diagonal(self)
        else:
            self.moveForward(val)
def findDistanceDiag(self): # finds the distnce of the furthest cell in a a diagonal line that is on the best path and moves the mouse to that cell
    print(self.direction)
    if(self.direction == "E"):
        val = 0
        for i in range (1, cols):
            if(self.col < cols - i and self.maze[self.row][self.col + i].onBestPath and not self.maze[self.row][self.col + (i - 1)].wallE):
                val += 1
            else:
                break
        if(val == 1 and diag):
            print("diag (fake)")
            return True
        else:
            return False
    if(self.direction == "W"):
        val = 0
        for i in range (1, cols):
            if(self.col > i - 1 and self.maze[self.row][self.col - i].onBestPath and not self.maze[self.row][self.col - (i - 1)].wallW):
                val += 1
            else:
                break
        if(val == 1 and diag):
            print("diag (fake)")
            return True
        else:
            return False
    if(self.direction == "N"):
        val = 0
        for i in range (1, rows):
            if(self.row > i - i and self.maze[self.row - i][self.col].onBestPath and not self.maze[self.row - (i - 1)][self.col].wallN):
                val += 1
            else:
                break
        if(val == 1 and diag):
            print("diag (fake)")
            return True
        else:
            return False
    if(self.direction == "S"):
        val = 0
        for i in range (1, rows):
            if(self.row < rows - i and self.maze[self.row + i][self.col].onBestPath and not self.maze[self.row + (i - 1)][self.col].wallS):
                val += 1
            else:
                break
        if(val == 1 and diag):
            print("diag (fake)")
            return True
        else:
            return False
            
def diagonal(self): # moves the mouse diagonally to the end of the diagonal line
    next = True
    while(next):
        next = mouse1.followBestPath(False)
        
def updateArrayVals(): # updates the values of the cells in the array accounting for new walls
    for s in range (99):
        for i in range (rows):
            for j in range (cols):
                array_2d[i][j].updateVal()
                
def resetArrayVals(): # resets the values of the cells in the array (called in conjunction with updateArrayVals())
    global override
    for i in range (rows):
        for j in range (cols):
            array_2d[i][j].setVal(99)
        if(not override):
            array_2d[7][7].setVal(0)
            array_2d[8][7].setVal(0)
            array_2d[7][8].setVal(0)
            array_2d[8][8].setVal(0)
        else:
            array_2d[0][0].setVal(0)
            
def updateArrayWalls(): # updates the walls of the cells in the array
    for i in range (rows):
        for j in range (cols):
            array_2d[i][j].updateWalls()

def findBestPath(rowS, colS): # finds the best path from the mouse's current position to the center using the cell values(does not account for diagonal turns being slightly faster despite more distance)
    resetBestPath()
    rowsC = rowS
    colsC = colS
    currentCell = array_2d[rowsC][colsC]
    for i in range (99):
        currentCell.setOnBestPath()
        if(colsC < cols - 1):
            if(array_2d[rowsC][colsC + 1].value == currentCell.value - 1 and not currentCell.wallE):
                currentCell = array_2d[rowsC][colsC + 1]
        if(colsC > 0):
            if(array_2d[rowsC][colsC - 1].value == currentCell.value - 1 and not currentCell.wallW):
                currentCell = array_2d[rowsC][colsC - 1]
        if(rowsC < rows - 1):
            if(array_2d[rowsC + 1][colsC].value == currentCell.value - 1 and not currentCell.wallS):
                currentCell = array_2d[rowsC + 1][colsC]
        if(rowsC > 0):
            if(array_2d[rowsC - 1][colsC].value == currentCell.value - 1 and not currentCell.wallN):
                currentCell = array_2d[rowsC - 1][colsC]
        rowsC = currentCell.rows
        colsC = currentCell.cols
def resetBestPath(): # resets the best path of the cells in the array (called in conjunction with findBestPath())
    for i in range (rows):
        for j in range (cols):
            array_2d[i][j].onBestPath = False
class Mouse: # defines the class of mouse and its base values and methods
    def __init__(self, maze):
        self.direction = "E"
        self.row = 0
        self.col = 0
        self.wallN = False
        self.wallS = False
        self.wallE = False
        self.wallW = False
        self.wallF = False
        self.wallR = False
        self.wallL = False
        self.maze = maze
        self.currentCell = self.maze[self.row][self.col]
    def turn90(self): # turns the mouse 90 degrees to the right
        if(self.direction == "N"):
            self.direction = "E"
            return
        if(self.direction == "E"):
            self.direction = "S"
            return
        if(self.direction == "S"):
            self.direction = "W"
            return
        if(self.direction == "W"):
            self.direction = "N"
            return
    def turnNeg90(self): # turns the mouse 90 degrees to the left
        if(self.direction == "N"):
            self.direction = "W"
            return
        if(self.direction == "W"):
            self.direction = "S"
            return
        if(self.direction == "S"):
            self.direction = "E"
            return
        if(self.direction == "E"):
            self.direction = "N"
            return
    def moveForward(self, amount): # moves the mouse forward a specified amount of cells
        if(self.direction == "N"):
            self.row -= amount
        if(self.direction == "S"):
            self.row += amount
        if(self.direction == "E"):
            self.col += amount
        if(self.direction == "W"):
            self.col -= amount
        self.currentCell = self.maze[self.row][self.col]
    def movePosForward(self, amount): # moves the mouse's position forward a specified amount of cells (used for diagonal movement)
        if(self.direction == "N"):
            self.row -= amount
        if(self.direction == "S"):
            self.row += amount
        if(self.direction == "E"):
            self.col += amount
        if(self.direction == "W"):
            self.col -= amount
        self.currentCell = self.maze[self.row][self.col]
    def detectWalls(self): # detects the walls around the mouse
        if():
            self.wallR = True
        if():
            self.wallL = True
        if():
            self.wallF = True
    def updateWalls(self): # updates the walls of the cell the mouse is on with the walls the mouse detects
        if(self.wallF):
            self.currentCell.setWall(self.direction)
            updateArrayWalls()
            resetArrayVals()
            updateArrayVals()
        if(self.wallR):
            if(self.direction == "N"):
                self.currentCell.setWall("E")
            if(self.direction == "W"):
                self.currentCell.setWall("N")
            if(self.direction == "S"):
                self.currentCell.setWall("W")
            if(self.direction == "E"):
                self.currentCell.setWall("S")
            updateArrayWalls()
            resetArrayVals()
            updateArrayVals()
        if(self.wallL):
            if(self.direction == "N"):
                self.currentCell.setWall("W")
            if(self.direction == "W"):
                self.currentCell.setWall("S")
            if(self.direction == "S"):
                self.currentCell.setWall("E")
            if(self.direction == "E"):
                self.currentCell.setWall("N")
            updateArrayWalls()
            resetArrayVals()
            updateArrayVals()
    def followBestPath(self, real): # follows the best path from the mouse's current position to the center using the cell values(has different modes for mapping and diagonal movement)
        findBestPath(self.row, self.col)
        if(real):
            if(mapping):
                if(self.direction == "E"):
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        self.moveForward(1)
                        return
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        self.turn90()
                        self.moveForward(1)
                        return
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        self.turnNeg90()
                        self.moveForward(1)
                        return
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        self.turn90()
                        self.turn90()
                        self.moveForward(1)
                        return
                if(self.direction == "W"):
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        self.moveForward(1)
                        return
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        self.turnNeg90()
                        self.moveForward(1)
                        return
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        self.turn90()
                        self.moveForward(1)
                        return
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        self.turn90()
                        self.turn90()
                        self.moveForward(1)
                        return
                if(self.direction == "N"):
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        self.moveForward(1)
                        return
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        self.turn90()
                        self.moveForward(1)
                        return
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        self.turnNeg90()
                        self.moveForward(1)
                        return
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        self.turn90()
                        self.turn90()
                        self.moveForward(1)
                        return
                if(self.direction == "S"):
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        self.moveForward(1)
                        return
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        self.turnNeg90()
                        self.moveForward(1)
                        return
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        self.turn90()
                        self.moveForward(1)
                        return
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        self.turn90()
                        self.turn90()
                        self.moveForward(1)
                        return
            else:
                if(self.direction == "E"):
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        findDistance(self)
                        return
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        self.turn90()
                        findDistance(self)
                        return
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        self.turnNeg90()
                        findDistance(self)
                        return
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        self.turn90()
                        self.turn90()
                        findDistance(self)
                        return
                if(self.direction == "W"):
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        findDistance(self)
                        return
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        self.turnNeg90()
                        findDistance(self)
                        return
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        self.turn90()
                        findDistance(self)
                        return
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        self.turn90()
                        self.turn90()
                        findDistance(self)
                        return
                if(self.direction == "N"):
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        findDistance(self)
                        return
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        self.turn90()
                        findDistance(self)
                        return
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        self.turnNeg90()
                        findDistance(self)
                        return
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        self.turn90()
                        self.turn90()
                        findDistance(self)
                        return
                if(self.direction == "S"):
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        findDistance(self)
                        return
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        self.turnNeg90()
                        findDistance(self)
                        return
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        self.turn90()
                        findDistance(self)
                        return
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        self.turn90()
                        self.turn90()
                        findDistance(self)
                        return
        else:
            if(self.direction == "E"):
                if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                    self.turn90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                    self.turnNeg90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
            if(self.direction == "W"):
                if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                    self.turnNeg90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                    self.turn90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
            if(self.direction == "N"):
                if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                    self.turn90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                    self.turnNeg90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
            if(self.direction == "S"):
                if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                    self.turnNeg90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                    self.turn90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                    

mouse1 = Mouse(array_2d)

printArrayVals()
updateArrayVals()
printArrayVals()

array_2d[7][7].setWall("N")
array_2d[7][7].setWall("W")
array_2d[8][7].setWall("W")
array_2d[7][8].setWall("N")
array_2d[8][8].setWall("E")
array_2d[8][8].setWall("S")
array_2d[8][7].setWall("S")

for i in range (rows - 10):
    array_2d[i][i].setWall("S")
    array_2d[i][i].setWall("W")
    array_2d[i][i + 1].setWall("N")
    array_2d[i][i + 1].setWall("E")


updateArrayWalls()
resetArrayVals()
updateArrayVals()
findBestPath(mouse1.row, mouse1.col)
printArrayVals()

mapping = False
diag = True
def loop():
    global override
    for i in range (99): # main loop
        printArrayVals()
        print(mouse1.row, mouse1.col, mouse1.currentCell.value, mouse1.currentCell.rows, mouse1.currentCell.cols, mouse1.direction)
        updateArrayWalls()
        resetArrayVals()
        updateArrayVals()
        if(mouse1.currentCell.value == 0):
            time.sleep(3)
            override = True
        mouse1.followBestPath(True)
loop()

# Turn 45 implementation
# exiting diagonal turns
# turns during diagonals
