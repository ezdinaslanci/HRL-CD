import numpy as np

from GraphXv2 import GraphX
from GridCellButton import GridCellButton
from State import State


class Environment:

    def __init__(self, gridSize):

        # grid size
        self.gridSize = gridSize

        # data holders
        self.stateList = np.empty(shape=self.gridSize, dtype=State)
        self.buttonList = np.empty(shape=self.gridSize, dtype=GridCellButton)
        self.mapMatrix = np.empty(shape=self.gridSize, dtype=str)
        self.mapMatrix[:] = "0"
        self.mapFileName = "unsavedMap"
        self.partialMapMatrix = np.full(shape=self.gridSize, fill_value="X", dtype=str)
        self.model = {}
        self.immRewardAtGoal = 50
        self.graph = GraphX()
        self.startCoordinates = (0, 0)
        self.goalCoordinates = (gridSize[0] - 1, gridSize[1] - 1)

        # construct stateList
        for row in range(0, self.gridSize[0]):
            for col in range(0, self.gridSize[1]):
                stateType = (col == 0) * 8 + (row == 0) * 4 + (col == self.gridSize[1] - 1) * 2 + (row == self.gridSize[0] - 1) * 1
                # stateType = 0
                stateType = format(stateType, "x").upper()
                self.stateList[row][col] = State(stateType, (row, col), self.gridSize)

        # add immediate reward
        self.stateList[gridSize[0] - 1][gridSize[1] - 1].isGoal = True

    def updateStateListFromMapMatrix(self):
        self.stateList = np.empty(shape=self.gridSize, dtype=State)
        for row in range(0, self.gridSize[0]):
            for col in range(0, self.gridSize[1]):
                self.stateList[row][col] = State(self.mapMatrix[row][col], (row, col), self.gridSize)
        self.deleteActionsHeadingWalls()
        self.stateList[self.goalCoordinates].isGoal = True

    def updateButtonListFromStateList(self):
        self.buttonList = np.empty(shape=self.gridSize, dtype=GridCellButton)
        for row in range(0, self.gridSize[0]):
            for col in range(0, self.gridSize[1]):
                self.buttonList[row][col] = GridCellButton(self.stateList[row][col].stateType)
        self.buttonList[self.startCoordinates].setStart(True)
        self.buttonList[self.goalCoordinates].setGoal(True)

    def updateMapMatrixFromStateList(self):
        self.mapMatrix = np.empty(shape=self.gridSize, dtype=str)
        for row in range(0, self.gridSize[0]):
            for col in range(0, self.gridSize[1]):
                self.mapMatrix[row, col] = self.stateList[row][col].stateType

    def toggleWall(self, mask, row, col, isNeighbour):
        currentState = bin(int(self.stateList[row][col].stateType, 16))[2:].zfill(4)
        newState = "".join([str(int(a) ^ int(b)) for a, b in zip(currentState, mask)])
        newStateHex = format(int(newState, 2), "x").upper()
        self.stateList[row][col].stateType = newStateHex
        self.mapMatrix[row][col] = newStateHex
        self.buttonList[row][col].stateType = newStateHex
        if mask == "0001":
            neighbourRow = (row + 1) % self.gridSize[0]
            neighbourCol = col
            neighbourMask = "0100"
            actionToBeToggled = "DOWN"
        elif mask == "0010":
            neighbourRow = row
            neighbourCol = (col + 1) % self.gridSize[1]
            neighbourMask = "1000"
            actionToBeToggled = "RIGHT"
        elif mask == "0100":
            neighbourRow = row - 1
            neighbourCol = col
            neighbourMask = "0001"
            actionToBeToggled = "UP"
        elif mask == "1000":
            neighbourRow = row
            neighbourCol = col - 1
            neighbourMask = "0010"
            actionToBeToggled = "LEFT"
        else:
            return
        self.stateList[row][col].toggleOption(actionToBeToggled)
        if isNeighbour:
            return
        self.toggleWall(neighbourMask, neighbourRow, neighbourCol, True)

    def toggleStartGoal(self, destType, row, col):
        if destType == "START":
            if self.startCoordinates != (None, None):
                self.buttonList[self.startCoordinates].setStart(False)
            self.startCoordinates = (row, col)
            self.buttonList[row][col].setStart(True)
        elif destType == "GOAL":
            if self.goalCoordinates != (None, None):
                self.buttonList[self.goalCoordinates].setGoal(False)
                self.stateList[self.goalCoordinates].isGoal = False
            self.goalCoordinates = (row, col)
            self.buttonList[row][col].setGoal(True)
            self.stateList[row][col].isGoal = True
            self.stateList[row][col].immReward = self.immRewardAtGoal
        else:
            return

    def setImmRewardAtGoal(self, immRewardAtGoal):
        self.immRewardAtGoal = immRewardAtGoal

    def deleteActionsHeadingWalls(self):
        for row in range(0, self.gridSize[0]):
            for col in range(0, self.gridSize[1]):
                if self.stateList[row][col].stateType in ["8", "9", "A", "B", "C", "D", "E", "F"]:
                    self.stateList[row][col].deleteOption("LEFT")
                if self.stateList[row][col].stateType in ["4", "5", "6", "7", "C", "D", "E", "F"]:
                    self.stateList[row][col].deleteOption("UP")
                if self.stateList[row][col].stateType in ["2", "3", "6", "7", "A", "B", "E", "F"]:
                    self.stateList[row][col].deleteOption("RIGHT")
                if self.stateList[row][col].stateType in ["1", "3", "5", "7", "9", "B", "D", "F"]:
                    self.stateList[row][col].deleteOption("DOWN")

    def stateInformation(self, row, col):
        print("{} | immReward: {} | stateType: {}".format(self.stateList[row][col].getQValues(), self.stateList[row][col].immReward, self.stateList[row][col].stateType))

    def resetLearning(self):
        for row in range(0, self.gridSize[0]):
            for col in range(0, self.gridSize[1]):
                self.stateList[row][col].resetState()
                self.stateList[row][col].numberOfVisits = 0

    def resetMapProperties(self):
        self.partialMapMatrix = np.full(shape=self.gridSize, fill_value="X", dtype=str)
        self.graph = GraphX()
