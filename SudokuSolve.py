import numpy as np
import csv

N_rows = 9
N_cols = 9

class SudokuSolve:
    Puzzle = np.zeros((9,9), dtype=int)
    SudokuArray = range(1,10)

    def __init__(self, csvFilename):
        self.ReadInputPuzzle( csvFilename)

    
    def ReadInputPuzzle(self,csvFileName):
        with open(csvFileName,newline ='') as csvfile:
            sudokuPuzzle = csv.reader(csvfile,delimiter= ',')
            for ridx,row in enumerate(sudokuPuzzle):
                for cidx in range(0,len(row)):
                    self.Puzzle[ridx][cidx] = 0 if len(row[cidx]) == 0 else int(row[cidx])

    def PresentInRow(self, row, num):
        if num in self.Puzzle[row,:]:
            return True
        else:
            return False

    def PresentInCol(self, col, num):
        if num in self.Puzzle[:,col]:
            return True
        else:
            return False

    def PresentInBlk(self, row, col, num):
        strtRow = row - row %3
        strtCol = col - col %3
        if num in self.Puzzle[strtRow:strtRow+3,strtCol:strtCol+3]:
            return True
        else:
            return False

    def CheckValidity(self, row, col, num):
        if self.PresentInBlk(row, col, num) or  self.PresentInCol(col, num)  or  self.PresentInRow(row, num) :
            return False
        else:
            return True


    def FindUnassignedElement(self):
        for row in range(0,np.size(self.Puzzle,0)):
            for col in range(0,np.size(self.Puzzle,1)):
                if self.Puzzle[row,col] == 0:
                    return True,row,col
        return False,0,0
        
    def CheckUnassigned(self,row,col):
        if self.Puzzle[row,col] == 0:
            return True
        else:
            return False 

    def SolveSudoku(self):
        [res,row,col] = self.FindUnassignedElement()
        if not res:
            return True
        
        for tryNum in self.SudokuArray:
            if self.CheckValidity(row,col,tryNum):
                self.Puzzle[row,col] = tryNum
                if self.SolveSudoku():
                    return True
                else:
                    self.Puzzle[row,col] = 0
        return False
                
    def WriteOutput(self, filename = 'output.csv', Puzzle = None):
        if Puzzle is None:
            np.savetxt(filename, self.Puzzle, delimiter=",", fmt='%d')
        else:
            np.savetxt(filename, Puzzle, delimiter=",",fmt='%d')

if __name__ == "__main__":
    csvFileName = input("Please enter the input csv filename\n")
    s = None
    while(s is None):
        try:
            with open(csvFileName) as f:
                s = f.read()
        except IOError as x:
            csvFileName = input("Invalid file. Please enter a valid input file name\n")


    ab = SudokuSolve(csvFileName)
    Result = ab.SolveSudoku()
    if Result:
        ab.WriteOutput()
        print('Result saved in output.csv')
    else:
        print("Sudoku could not be solved")


