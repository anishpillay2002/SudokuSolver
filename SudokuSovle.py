from collections import Counter 
import os
import numpy as np
from itertools import product
import pandas as pd
import csv

class SudokuSolve:
    Puzzle = []
    FirstBox = []
    EliminationConditions = []
    def __init__(self, csvFilename):
        self.SudokuArray = range(1,10)
        self.ReadInputPuzzle( csvFilename)

    
    def ReadInputPuzzle(self,csvFileName):
        sPuzz = []
        with open(csvFileName,newline ='') as csvfile:
            sudokuPuzzle = csv.reader(csvfile,delimiter= ',')
            for ridx,row in enumerate(sudokuPuzzle):
                for cidx in range(0,len(row)):
                    s = {}
                    BlockId = 0
                    if ridx < 3 :
                        BlockId = 10
                    elif ridx < 6:
                        BlockId = 20
                    else:
                        BlockId = 30
                    if cidx < 3 :
                        BlockId = BlockId+ 1
                    elif cidx < 6:
                        BlockId = BlockId+ 2
                    else:
                        BlockId = BlockId+ 3
                    s['HId'] = ridx
                    s['VId'] = cidx
                    s['Value'] = 0 if len(row[cidx]) == 0 else int(row[cidx])
                    s['PossibleValues'] = []
                    s['BlockId'] = BlockId
                    sPuzz.append(s)
        self.Puzzle = pd.DataFrame(sPuzz)

    def appendCond(self, Idx1, Idx2):
        self.EliminationConditions.append(lambda x: x[Idx1] !=  x[Idx2] if (Idx1<len(x) and Idx2<len(x)) else True)

    def CheckHAxis(self, Ele, InremNums, Puzzle):
        currHID = Puzzle.iloc[Ele]['HId']
        remNums = list(Puzzle.loc[(Puzzle['HId'] == currHID) & (Puzzle.index != Ele)]['Value'])
        return(list(set(InremNums).difference(remNums)))

    def CheckVAxis(self, Ele, InremNums, Puzzle):
        currVID = Puzzle.iloc[Ele]['VId']
        remNums = list(Puzzle.loc[(Puzzle['VId'] == currVID) & (Puzzle.index != Ele)]['Value'])
        return(list(set(InremNums).difference(remNums)))
    
    def CheckBlock(self, Ele, Puzzle):
        currBlock = Puzzle.iloc[Ele]['BlockId']
        remNums = list(Puzzle.loc[(Puzzle['BlockId'] == currBlock) & (Puzzle.index != Ele)]['Value'])
        return(list(set(self.SudokuArray).difference(remNums)))

    def FindLeastSetOfValuesIdx(self, Puzzle, IgnoreIdx):
        tid = None
        for idx, s in enumerate(Puzzle):
            if len(Puzzle[idx]['PossibleValues']) > 1 and idx is not IgnoreIdx:
                if tid is None:
                    tid = idx
                elif(len(Puzzle[idx]['PossibleValues']) < len(Puzzle[tid]['PossibleValues'])):
                    tid = idx
        return tid

    def ValidatePuzzle(self, Puzzle):
        SingleVals = all(Puzzle['Value'] != 0)
        UniqueVals = True
        for numId in range(0,10):
            if not self.CheckUnique(Puzzle,numId):
                UniqueVals = False
                break
        return(SingleVals,UniqueVals)

    def CheckUnique(self,Puzzle,numId):
        flag = True
        HVals = list(Puzzle[(Puzzle['HId'] == numId) & Puzzle['Value'] != 0]['Value'])
        VVals = list(Puzzle[(Puzzle['VId'] == numId) & Puzzle['Value'] != 0]['Value'])
        if (len(set(HVals)) != len(HVals)) or (len(set(VVals)) != len(VVals)):
            flag = False
        return(flag)

    def GetPossibleValues(self, Puzzlebk = None):
        cont = 1
        # Initializing Puzzle variable
        if Puzzlebk is None:
            Puzzle = self.Puzzle
        else:
            Puzzle = Puzzlebk.copy()
        
        # Creating a backup copy for comparison
        tmpDict = Puzzle.copy()

        EmptyCellsPresent = True
        while cont == 1 and EmptyCellsPresent:
            # Getting all possible values for each cell in Sudoku
            for idx, s in Puzzle.iterrows():
                if s['Value'] == 0:
                    remNums = self.CheckBlock(idx, Puzzle)
                    remNums = self.CheckVAxis(idx, remNums, Puzzle)
                    remNums = self.CheckHAxis(idx, remNums, Puzzle)
                    if len(remNums) == 1:
                        Puzzle.loc[idx,'Value'] = remNums[0]
                        Puzzle.at[idx, 'PossibleValues'] = []
                    else:
                        Puzzle.loc[idx,'Value'] = 0
                        Puzzle.at[idx, 'PossibleValues'] = remNums
            
            # Checking if there are empty cells
            if any(Puzzle['Value'] == 0):
                EmptyCellsPresent = True
            else:
                EmptyCellsPresent = False
            
            if tmpDict.equals(Puzzle) and EmptyCellsPresent:
                # Checking cells with list of possible values
                AllPossibleValues = Puzzle[np.array(list(map(len,Puzzle.PossibleValues.values)))>1]
                # If there are cells with possible values, selecting one and solving sudoku
                if len(AllPossibleValues) > 0:
                    RecurPuzzle = Puzzle.copy()
                    currEle = AllPossibleValues.index.values[0]
                    # Selecting one value from list of possible values
                    for idx,i in enumerate(RecurPuzzle.iloc[currEle]['PossibleValues']):
                        RecurPuzzle.loc[currEle,'Value'] = i
                        RecurPuzzle.at[currEle,'PossibleValues'] = []
                        # Checking if the value selected is unique in its spot
                        if not self.CheckUnique(RecurPuzzle,currEle) and idx == len(RecurPuzzle.iloc[currEle]['PossibleValues'])-1:
                            RecurPuzzle = Puzzle.copy()
                        elif not self.CheckUnique(RecurPuzzle,currEle):
                            continue
                        else:
                            # Getting Possible values again in a recursive function till all possibilities are not tested
                            RecurPuzzlebk,MissingValueRecur = self.GetPossibleValues( RecurPuzzle)
                            if MissingValueRecur:
                                continue
                            else:
                                EmptyCellsPresent = MissingValueRecur
                                Puzzle = RecurPuzzlebk
                                break
                else:
                    Puzzle = Puzzlebk.copy()
                cont = 0
            elif tmpDict.equals(Puzzle):
                cont = 0
            else:
                tmpDict = Puzzle.copy()
        if Puzzlebk is None:
            self.Puzzle = Puzzle
        return(Puzzle,EmptyCellsPresent)

    def SolveSudoku(self):
        Puzzle = self.GetPossibleValues()
        SingleVals,UniqueVals = self.ValidatePuzzle(self.Puzzle)
        if SingleVals is True and UniqueVals is True:
            return(True,Puzzle)
        else:
            return(False,[])

    def WriteOutput(self, filename = 'output.csv', Puzzle = None):
        if Puzzle is None:
            Puzzle = self.Puzzle

        with open(filename, 'w', newline='') as csvfile:
            csvWriter = csv.writer(csvfile, delimiter=' ',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for rid in range(0,10):
                csvWriter.writerow(list(Puzzle[Puzzle['HId'] == rid]['Value']))

if __name__ == "__main__":
    csvFileName = 'SudokuPuzzle.csv'
    ab = SudokuSolve(csvFileName)
    Result,Puzzle = ab.SolveSudoku()
    if Result:
        ab.WriteOutput()


