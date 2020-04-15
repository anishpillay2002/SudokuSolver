from SudokuSovle import SudokuSolve
import pandas as pd
import csv

csvFileName = 'SudokuPuzzle.csv'
sudokuPuzz = None

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
SPuzzDF = pd.DataFrame(sPuzz)


import time
start = time.process_time()
ab= SudokuSolve(SPuzzDF)
ab.SolveSudoku()
print(time.process_time() - start)

with open('output.csv', 'w', newline='') as csvfile:
    csvWriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    currRow = []
    for rid in range(0,10):
        csvWriter.writerow(list(ab.Puzzle[ab.Puzzle['HId'] == rid]['Value']))

    # for idx, s in enumerate(ab.Puzzle):
    #     if (idx != 0 and ab.Puzzle[idx]['HId'] != ab.Puzzle[idx-1]['HId']):
    #         csvWriter.writerow(currRow)
    #         currRow = []
    #     currRow.append(ab.Puzzle[idx]['Value'])
    # csvWriter.writerow(currRow) 
        
