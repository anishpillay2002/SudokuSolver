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

    def GetPossibleValues(self, Puzzlebk):
        cont = 1
        Puzzle = Puzzlebk.copy()
        tmpDict = Puzzle.copy()
        MissingValue = True
        while cont == 1 and MissingValue:
            for idx, s in Puzzle.iterrows():
                if s['Value'] == 0:
                    remNums = self.CheckBlock(idx, Puzzle)
                    remNums = self.CheckVAxis(idx, remNums, Puzzle)
                    remNums = self.CheckHAxis(idx, remNums, Puzzle)
                    if len(remNums) == 1:
                        Puzzle.loc[idx,'Value'] = remNums[0]
                    else:
                        Puzzle.at[idx, 'PossibleValues'] = remNums

            self.WriteOutput('inter.csv', Puzzle)
            if any(Puzzle['Value'] == 0):
                MissingValue = True
            else:
                MissingValue = False
            
            if tmpDict.equals(Puzzle) and MissingValue:
                # AllPossibleValues = Puzzle[np.array(list(map(len,Puzzle.PossibleValues.values)))>1]
                # RecurPuzzle = Puzzle.copy()
                # currEle = AllPossibleValues.index.values[0]
                # for i in RecurPuzzle.iloc[currEle]['PossibleValues']:
                #     RecurPuzzle.loc[currEle,'Value'] = i
                #     RecurPuzzlebk,MissingValueRecur = self.GetPossibleValues( RecurPuzzle)
                #     if MissingValueRecur:
                #         continue
                #     else:
                #         MissingValue = MissingValueRecur
                #         Puzzle = RecurPuzzlebk
                cont = 0
            elif tmpDict.equals(Puzzle):
                cont = 0
            else:
                tmpDict = Puzzle.copy()
        
        return(Puzzle,MissingValue)
    
    def WriteOutput(self, filename = 'output.csv', Puzzle = None):
        if Puzzle is None:
            Puzzle = self.Puzzle

        with open(filename, 'w', newline='') as csvfile:
            csvWriter = csv.writer(csvfile, delimiter=' ',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for rid in range(0,10):
                csvWriter.writerow(list(Puzzle[Puzzle['HId'] == rid]['Value']))

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
                    s['ConfidenceNum'] = 10 if s['Value'] != 0 else 0
                    sPuzz.append(s)
        self.Puzzle = pd.DataFrame(sPuzz)

    def SolveSudoku(self):
        self.GetPossibleValues(self.Puzzle)
        self.WriteOutput()
        SingleVals,UniqueVals = self.ValidatePuzzle(self.Puzzle)
        if SingleVals is True and UniqueVals is True:
            PuzzleSolved = True
            return
        Puzzle = self.Puzzle.copy()
        AllPossibleValues = Puzzle[np.array(list(map(len,Puzzle.PossibleValues.values)))>1]
        AllPossibleValues.loc[:,'len'] = np.array(list(map(len,AllPossibleValues.PossibleValues.values)))
        ItrVals = AllPossibleValues.groupby('len').size().iloc[0]
        AllPossibleValues = AllPossibleValues.sort_values(by='len', ascending=True).drop(columns='len')
        AllPossibleValuesCopy = AllPossibleValues.copy().reset_index(drop=True)
        uniqBlkIds = np.unique(AllPossibleValues['BlockId'])
        for numId in range(0,9):
            HVals = AllPossibleValuesCopy[(AllPossibleValuesCopy['HId'] == numId)].index.tolist() 
            VVals = AllPossibleValuesCopy[(AllPossibleValuesCopy['VId'] == numId)].index.tolist()
            BlkVals = AllPossibleValuesCopy[(AllPossibleValuesCopy['BlockId'] == uniqBlkIds[numId])].index.tolist()
            if len(HVals) > 1:
                Idx1 = HVals[0]
                for hidx in range(1,len(HVals)):
                    self.appendCond(Idx1,HVals[hidx])
            if len(VVals) > 1:
                Idx1 = VVals[0]
                for vidx in range(1,len(VVals)):
                    self.appendCond(Idx1,VVals[vidx])
            if len(BlkVals) > 1:
                Idx1 = BlkVals[0]
                for vidx in range(1,len(BlkVals)):
                    self.appendCond(Idx1,BlkVals[vidx])

        PossibilityIdx = list(AllPossibleValues['PossibleValues'].index)
        PossibilityVals = list(AllPossibleValues['PossibleValues'])
        ItrVals = 15
        PuzzleSolved =False
        BackupPuzzle = Puzzle.copy()
        IterationTried = 1
        while(ItrVals < len(PossibilityIdx)) or PuzzleSolved is False:
            Puzzle = BackupPuzzle.copy()
            PossibilityIdxItr = PossibilityIdx[0:ItrVals]
            PossibilityValsItr = PossibilityVals[0:ItrVals]
            prodItr = product(*PossibilityValsItr)
            
            for idx,Itr in enumerate(prodItr):
                Itr1 = list(Itr)
                if all( [ f(Itr1) for f in self.EliminationConditions ] ):
                    Puzzle.loc[PossibilityIdxItr,'Value'] = Itr1
                    SingleVals,UniqueVals = self.ValidatePuzzle(Puzzle)
                    if UniqueVals:
                        Puzzle,MissingValues = self.GetPossibleValues(Puzzle)
                        IterationTried += 1
                        print(IterationTried)
                        if not MissingValues:
                            self.Puzzle = Puzzle
                            PuzzleSolved = True
                            break
                        # SingleVals,UniqueVals = self.ValidatePuzzle(Puzzle)
                        # if SingleVals is True and UniqueVals is True:
                        #     self.Puzzle = Puzzle
                        #     PuzzleSolved = True
                        #     break
            ItrVals +=3
        print(idx)
        print(PuzzleSolved)
        # IgnoreIdx = -1
        # ItrIdx = 1
        # while(ItrIdx < 1000):
        #     tid = self.FindLeastSetOfValuesIdx( Puzzle, IgnoreIdx)
        #     prevPuzzle = Puzzle.copy()
        #     if tid is None:
        #         return(True)
        #     ConfidenceNum = ConfidenceNum - 1
        #     for vid in range(0,len(Puzzle[tid]['PossibleValues'])):
        #         Puzzle[tid]['Value'] = Puzzle[tid]['PossibleValues'][vid]
        #         Puzzle = self.GetPossibleValues(Puzzle,ConfidenceNum)
        #         SingleVals,UniqueVals = self.ValidatePuzzle(Puzzle)
        #         ItrIdx += 1
        #         if SingleVals is True and UniqueVals is True:
        #             # Puzzle Complete
        #             self.Puzzle = Puzzle
        #             return(True)
        #         elif SingleVals is True and UniqueVals is False and vid is len(Puzzle[tid]['PossibleValues']):
        #             # One Step Back
        #             ConfidenceNum = Confidence + 1
        #             Puzzle = prevPuzzle.copy()
        #             IgnoreIdx = tid
        #             continue
        #         elif SingleVals is True and UniqueVals is False:
        #             # Try next Value in iteration
        #             Puzzle = prevPuzzle.copy()
        #             continue
        #         elif SingleVals is False and UniqueVals is True:
        #             # Next set of try
        #             IgnoreIdx = tid
        #             break
        # a= 1



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
            # for idx, s in enumerate(self.Puzzle):
            #     if self.Puzzle[idx][HId] == numId:
            HVals = list(Puzzle[(Puzzle['HId'] == numId) & Puzzle['Value'] != 0]['Value'])
            VVals = list(Puzzle[(Puzzle['VId'] == numId) & Puzzle['Value'] != 0]['Value'])
            # HVals = [d['Value'] for d in Puzzle if(d['HId'] == numId and d['Value'] != 0)]
            # VVals = [d['Value'] for d in Puzzle if(d['VId'] == numId and d['Value'] != 0)]
            if self.CheckUnique(HVals) or self.CheckUnique(VVals):
                UniqueVals = False
                break
        return(SingleVals,UniqueVals)

    def CheckUnique(self,ValList):
        flag =0
        if len(set(ValList)) != len(ValList):
            flag = 1
        return(flag)


if __name__ == "__main__":
    csvFileName = 'SudokuPuzzle.csv'
    ab = SudokuSolve(csvFileName)
    ab.SolveSudoku()
    ab.WriteOutput()


