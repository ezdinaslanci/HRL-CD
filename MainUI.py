#!/usr/bin/python
# -*- coding: utf-8 -*-

import glob
import sys
import os.path
import atexit

import numpy as np

from PySide import QtCore, QtGui
from PySide.QtCore import QSize

from GraphXv2 import GraphX

from RLTask import RLTask
from Environment import Environment
from State import State
from GridCellButton import GridCellButton
from ScientificDoubleSpinBox import ScientificDoubleSpinBox


class MainUI(QtGui.QMainWindow):

    def __init__(self):
        super(MainUI, self).__init__()

        # default settings
        self.generateSequence = False
        self.resetLearning = True

        # initiate RLTask
        self.RLTask = RLTask(self)

        # clear action sequence file
        sequenceFile = open(self.RLTask.sequenceFileName, "w")
        sequenceFile.close()

        # create ssGrid folder if not exists
        if not os.path.exists(self.RLTask.ssGridFolder):
            os.makedirs(self.RLTask.ssGridFolder)

        # frames
        self.leftFrame = QtGui.QFrame()
        self.rightFrame = QtGui.QFrame()
        self.bottomFrame = QtGui.QFrame()
        self.statusFrame = QtGui.QFrame()

        # stacked layout for multiple environments
        self.leftStackedLayout = QtGui.QStackedLayout()

        # other ui elements
        self.bottomGrid = QtGui.QHBoxLayout()
        self.bottomGrid.setContentsMargins(0, 0, 0, 0)
        self.mapNameLabel = QtGui.QLabel("")
        self.menuBar = self.menuBar()

        # initiate GUI
        self.initUI()

    def initUI(self):

        # central widget for QMainWindow, big boss
        centralWidget = QtGui.QWidget()
        self.setCentralWidget(centralWidget)

        # menu items
        loadMap = QtGui.QAction(QtGui.QIcon("images/open-bw.ico"), "Load Map", self)
        loadMap.setShortcut("Ctrl+O")
        loadMap.triggered.connect(self.loadMapFile)
        saveMap = QtGui.QAction(QtGui.QIcon("images/save-bw.png"), "Save Map", self)
        saveMap.setShortcut("Ctrl+S")
        saveMap.triggered.connect(self.saveMapFile)
        saveACopy = QtGui.QAction(QtGui.QIcon("images/saveACopy-bw.png"), "Save a Copy", self)
        saveACopy.triggered.connect(self.saveACopyFile)
        printMapMatrix = QtGui.QAction(QtGui.QIcon("images/matrix.png"), "Print Map Matrix", self)
        printMapMatrix.triggered.connect(self.printMapMatrix)
        printPartialMapMatrix = QtGui.QAction(QtGui.QIcon("images/matrix.png"), "Print Partial Map Matrix", self)
        printPartialMapMatrix.triggered.connect(self.printPartialMapMatrix)
        changeGridSize = QtGui.QAction(QtGui.QIcon("images/resize-bw.png"), "Grid Size", self)
        changeGridSize.setShortcut("Ctrl+G")
        changeGridSize.triggered.connect(self.changeGridSize)
        addNewEnv = QtGui.QAction(QtGui.QIcon("images/plus-bw.png"), "Add New", self)
        addNewEnv.setShortcut("Ctrl+N")
        addNewEnv.triggered.connect(self.addNewEnvironment)
        updateGridSS = QtGui.QAction(QtGui.QIcon("images/refresh-bw.png"), "Update SS", self)
        updateGridSS.triggered.connect(self.updateGridSS)
        reDrawGrid = QtGui.QAction(QtGui.QIcon("images/refresh-bw.png"), "Redraw Grid", self)
        reDrawGrid.triggered.connect(self.reDrawEnvironment)
        showMaxActions = QtGui.QAction(QtGui.QIcon("images/arrows2-bw.png"), "Show Max Actions", self)
        showMaxActions.triggered.connect(self.showMaxOptionsOnGrid)
        showNumberOfVisits = QtGui.QAction(QtGui.QIcon("images/hash.png"), "Show Number of Visits", self)
        showNumberOfVisits.triggered.connect(self.showNumberOfVisitsOnGrid)
        showOptionsOnGrid = QtGui.QAction(QtGui.QIcon("images/hash.png"), "Show Options", self)
        showOptionsOnGrid.triggered.connect(self.showOptionsOnGrid)
        drawGraphFromPartialModel = QtGui.QAction(QtGui.QIcon(""), "Draw Graph from Partial Model", self)
        drawGraphFromPartialModel.triggered.connect(self.drawGraphFromPartialModel)
        startQL = QtGui.QAction(QtGui.QIcon(""), "Start QL", self)
        startQL.setShortcut("Ctrl+Q")
        startQL.triggered.connect(self.RLTask.QLThreadStart)
        startPS = QtGui.QAction(QtGui.QIcon(""), "Start PS", self)
        startPS.setShortcut("Ctrl+P")
        startPS.triggered.connect(self.RLTask.PSThreadStart)
        mapOps = self.menuBar.addMenu("&Map Operations")
        mapOps.addAction(loadMap)
        mapOps.addAction(saveMap)
        mapOps.addAction(saveACopy)
        mapOps.addAction(printMapMatrix)
        mapOps.addAction(printPartialMapMatrix)
        gridOps = self.menuBar.addMenu("&Grid Operations")
        gridOps.addAction(changeGridSize)
        gridOps.addAction(addNewEnv)
        gridOps.addAction(updateGridSS)
        gridOps.addAction(reDrawGrid)
        gridOps.addAction(showMaxActions)
        gridOps.addAction(showNumberOfVisits)
        gridOps.addAction(showOptionsOnGrid)
        gridOps.addAction(drawGraphFromPartialModel)
        trainingOps = self.menuBar.addMenu("&Training")
        trainingOps.addAction(startQL)
        trainingOps.addAction(startPS)

        # frame customization & layouts
        self.leftFrame.setStyleSheet("QFrame { background-color: wheat; border: 1px groove #f0f0f0 }")
        self.rightFrame.setStyleSheet("QFrame { background-color: transparent }")
        self.bottomFrame.setStyleSheet("QFrame { border-top: 1px solid #d1d1d1; border-bottom: 1px solid #d1d1d1; } QLabel { border: none; }")
        # self.statusFrame.setStyleSheet("QFrame { background-color: #d3d3d3; } QLabel { border: none; }")

        # leftFrame layout
        self.leftFrame.setLayout(self.leftStackedLayout)
        # self.leftFrame.setMaximumWidth(819)

        # rightFrame widgets
        rightFrameWidgetWidth = 100
        alphaLabel = QtGui.QLabel("alpha: ")
        alphaSpinBox = QtGui.QDoubleSpinBox()
        alphaSpinBox.setRange(0, 1)
        alphaSpinBox.setSingleStep(0.01)
        alphaSpinBox.setValue(self.RLTask.alpha)
        alphaSpinBox.setFixedWidth(rightFrameWidgetWidth)
        alphaSpinBox.valueChanged.connect(lambda: self.RLTask.setAlpha(alphaSpinBox.value()))

        # discount factor parameter
        discountFactorLabel = QtGui.QLabel("discount factor: ")
        discountFactorSpinBox = QtGui.QDoubleSpinBox()
        discountFactorSpinBox.setRange(0, 1)
        discountFactorSpinBox.setSingleStep(0.01)
        discountFactorSpinBox.setValue(self.RLTask.discountFactor)
        discountFactorSpinBox.setFixedWidth(rightFrameWidgetWidth)
        discountFactorSpinBox.valueChanged.connect(lambda: self.RLTask.setDiscountFactor(discountFactorSpinBox.value()))

        # max epsilon parameter
        maxEpsilonLabel = QtGui.QLabel("max epsilon: ")
        maxEpsilonSpinBox = QtGui.QDoubleSpinBox()
        maxEpsilonSpinBox.setRange(0, 1)
        maxEpsilonSpinBox.setSingleStep(0.01)
        maxEpsilonSpinBox.setValue(self.RLTask.maxEpsilon)
        maxEpsilonSpinBox.setFixedWidth(rightFrameWidgetWidth)
        maxEpsilonSpinBox.valueChanged.connect(lambda: self.RLTask.setMaxEpsilon(maxEpsilonSpinBox.value()))

        # min epsilon parameter
        minEpsilonLabel = QtGui.QLabel("min epsilon: ")
        minEpsilonSpinBox = QtGui.QDoubleSpinBox()
        minEpsilonSpinBox.setRange(0, 1)
        minEpsilonSpinBox.setSingleStep(0.00001)
        minEpsilonSpinBox.setDecimals(5)
        minEpsilonSpinBox.setValue(self.RLTask.minEpsilon)
        minEpsilonSpinBox.setFixedWidth(rightFrameWidgetWidth)
        minEpsilonSpinBox.valueChanged.connect(lambda: self.RLTask.setMinEpsilon(minEpsilonSpinBox.value()))

        # epsilon decay factor parameter
        epsilonDecayFactorLabel = QtGui.QLabel("epsilon decay factor: ")
        epsilonDecayFactorSpinBox = QtGui.QDoubleSpinBox()
        epsilonDecayFactorSpinBox.setRange(0, 1)
        epsilonDecayFactorSpinBox.setSingleStep(0.00001)
        epsilonDecayFactorSpinBox.setDecimals(5)
        epsilonDecayFactorSpinBox.setValue(self.RLTask.epsilonDecayFactor)
        epsilonDecayFactorSpinBox.setFixedWidth(rightFrameWidgetWidth)
        epsilonDecayFactorSpinBox.valueChanged.connect(lambda: self.RLTask.setEpsilonDecayFactor(epsilonDecayFactorSpinBox.value()))

        # epsilon decay mode parameter
        epsilonDecayModeLabel = QtGui.QLabel("epsilon decay mode: ")
        epsilonDecayModeSpinBox = QtGui.QComboBox()
        epsilonDecayModeSpinBox.addItem("step")
        epsilonDecayModeSpinBox.addItem("episode")
        epsilonDecayModeSpinBox.setCurrentIndex(1)
        epsilonDecayModeSpinBox.setFixedWidth(rightFrameWidgetWidth)
        epsilonDecayModeSpinBox.currentIndexChanged.connect(lambda: self.RLTask.setEpsilonDecayMode(epsilonDecayModeSpinBox.currentText()))

        # number of updates parameter
        numOfUpdatesLabel = QtGui.QLabel("number of updates (PS): ")
        numOfUpdatesSpinBox = QtGui.QDoubleSpinBox()
        numOfUpdatesSpinBox.setRange(1, 50)
        numOfUpdatesSpinBox.setSingleStep(1)
        numOfUpdatesSpinBox.setDecimals(0)
        numOfUpdatesSpinBox.setValue(self.RLTask.numOfUpdates)
        numOfUpdatesSpinBox.setFixedWidth(rightFrameWidgetWidth)
        numOfUpdatesSpinBox.valueChanged.connect(lambda: self.RLTask.setNumOfUpdates(numOfUpdatesSpinBox.value()))

        # priority threshold paramater
        priorityThresholdLabel = QtGui.QLabel("priority threshold (PS): ")
        priorityThresholdSpinBox = ScientificDoubleSpinBox()
        priorityThresholdSpinBox.setRange(0, 50)
        priorityThresholdSpinBox.setValue(self.RLTask.priorityThreshold)
        priorityThresholdSpinBox.setFixedWidth(rightFrameWidgetWidth)
        priorityThresholdSpinBox.valueChanged.connect(lambda: self.RLTask.setPriorityThreshold(priorityThresholdSpinBox.value()))

        # immediate reward at goal parameter
        immRewardAtGoalLabel = QtGui.QLabel("immediate reward at goal: ")
        immRewardAtGoalSpinBox = QtGui.QDoubleSpinBox()
        immRewardAtGoalSpinBox.setRange(1, 10000)
        immRewardAtGoalSpinBox.setSingleStep(1)
        immRewardAtGoalSpinBox.setDecimals(0)
        immRewardAtGoalSpinBox.setValue(self.RLTask.immRewardAtGoal)
        immRewardAtGoalSpinBox.setFixedWidth(rightFrameWidgetWidth)
        immRewardAtGoalSpinBox.valueChanged.connect(lambda: self.setImmRewardAtGoal(immRewardAtGoalSpinBox.value()))

        # RL parameters group
        RLParameterBox = QtGui.QGroupBox("RL Parameters")
        RLParameterBoxLayout = QtGui.QGridLayout()
        RLParameterBoxLayout.addWidget(alphaLabel, 0, 0)
        RLParameterBoxLayout.addWidget(alphaSpinBox, 0, 1)
        RLParameterBoxLayout.addWidget(discountFactorLabel, 1, 0)
        RLParameterBoxLayout.addWidget(discountFactorSpinBox, 1, 1)
        RLParameterBoxLayout.addWidget(maxEpsilonLabel, 2, 0)
        RLParameterBoxLayout.addWidget(maxEpsilonSpinBox, 2, 1)
        RLParameterBoxLayout.addWidget(minEpsilonLabel, 3, 0)
        RLParameterBoxLayout.addWidget(minEpsilonSpinBox, 3, 1)
        RLParameterBoxLayout.addWidget(epsilonDecayFactorLabel, 4, 0)
        RLParameterBoxLayout.addWidget(epsilonDecayFactorSpinBox, 4, 1)
        RLParameterBoxLayout.addWidget(epsilonDecayModeLabel, 5, 0)
        RLParameterBoxLayout.addWidget(epsilonDecayModeSpinBox, 5, 1)
        RLParameterBoxLayout.addWidget(numOfUpdatesLabel, 6, 0)
        RLParameterBoxLayout.addWidget(numOfUpdatesSpinBox, 6, 1)
        RLParameterBoxLayout.addWidget(priorityThresholdLabel, 7, 0)
        RLParameterBoxLayout.addWidget(priorityThresholdSpinBox, 7, 1)
        RLParameterBoxLayout.addWidget(immRewardAtGoalLabel, 8, 0)
        RLParameterBoxLayout.addWidget(immRewardAtGoalSpinBox, 8, 1)
        RLParameterBox.setLayout(RLParameterBoxLayout)

        # convergence method
        trainUntilConvergenceCheckBox = QtGui.QCheckBox("train until convergence", self)
        trainUntilConvergenceCheckBox.toggle()
        trainUntilConvergenceCheckBox.stateChanged.connect(self.RLTask.toggleTrainUntilConvergenceOption)

        # number of episodes for training, valid if "train until convergence" is not selected
        numOfEpisodesForTrainingLabel = QtGui.QLabel("train for (episodes) ")
        self.numOfEpisodesForTrainingSpinBox = QtGui.QDoubleSpinBox()
        self.numOfEpisodesForTrainingSpinBox.setRange(1, 100000)
        self.numOfEpisodesForTrainingSpinBox.setSingleStep(1)
        self.numOfEpisodesForTrainingSpinBox.setDecimals(0)
        self.numOfEpisodesForTrainingSpinBox.setValue(self.RLTask.numOfEpisodesForTraining)
        self.numOfEpisodesForTrainingSpinBox.setFixedWidth(rightFrameWidgetWidth)
        self.numOfEpisodesForTrainingSpinBox.setDisabled(True)
        self.numOfEpisodesForTrainingSpinBox.valueChanged.connect(lambda: self.RLTask.setNumOfEpisodesForTraining(self.numOfEpisodesForTrainingSpinBox.value()))

        # convergence interval, valid if "train until convergence" is selected, basically this is the last N episodes to look at
        convergenceIntervalLabel = QtGui.QLabel("convergence interval: ")
        convergenceIntervalSpinBox = QtGui.QDoubleSpinBox()
        convergenceIntervalSpinBox.setRange(5, 100)
        convergenceIntervalSpinBox.setSingleStep(1)
        convergenceIntervalSpinBox.setDecimals(0)
        convergenceIntervalSpinBox.setValue(self.RLTask.convergenceInterval)
        convergenceIntervalSpinBox.setFixedWidth(rightFrameWidgetWidth)
        convergenceIntervalSpinBox.valueChanged.connect(lambda: self.RLTask.setConvergenceInterval(convergenceIntervalSpinBox.value()))

        # variance threshold for the number of steps in last N episodes
        varianceThresholdLabel = QtGui.QLabel("variance threshold: ")
        varianceThresholdSpinBox = QtGui.QDoubleSpinBox()
        varianceThresholdSpinBox.setRange(0, 10)
        varianceThresholdSpinBox.setSingleStep(0.01)
        varianceThresholdSpinBox.setDecimals(2)
        varianceThresholdSpinBox.setValue(self.RLTask.varianceThreshold)
        varianceThresholdSpinBox.setFixedWidth(rightFrameWidgetWidth)
        varianceThresholdSpinBox.valueChanged.connect(lambda: self.RLTask.setConvergenceThreshold(varianceThresholdSpinBox.value()))

        # RL training options group
        RLTrainingBox = QtGui.QGroupBox("Training")
        RLTrainingBoxLayout = QtGui.QGridLayout()
        RLTrainingBoxLayout.addWidget(trainUntilConvergenceCheckBox, 0, 0)
        RLTrainingBoxLayout.addWidget(numOfEpisodesForTrainingLabel, 1, 0)
        RLTrainingBoxLayout.addWidget(self.numOfEpisodesForTrainingSpinBox, 1, 1)
        RLTrainingBoxLayout.addWidget(convergenceIntervalLabel, 2, 0)
        RLTrainingBoxLayout.addWidget(convergenceIntervalSpinBox, 2, 1)
        RLTrainingBoxLayout.addWidget(varianceThresholdLabel, 3, 0)
        RLTrainingBoxLayout.addWidget(varianceThresholdSpinBox, 3, 1)
        RLTrainingBox.setLayout(RLTrainingBoxLayout)

        # generate action sequence checkbox
        generateSequenceFileCheckBox = QtGui.QCheckBox("generate action sequence file", self)
        generateSequenceFileCheckBox.stateChanged.connect(self.toggleGenerateSequenceOption)

        # if selected, resets learning initially
        resetLearningCheckBox = QtGui.QCheckBox("reset learning initially", self)
        resetLearningCheckBox.toggle()
        resetLearningCheckBox.stateChanged.connect(self.toggleResetLearningOption)

        # other options group
        otherOptionsBox = QtGui.QGroupBox("Other Options")
        otherOptionsBoxLayout = QtGui.QGridLayout()
        otherOptionsBoxLayout.addWidget(generateSequenceFileCheckBox, 0, 1)
        otherOptionsBoxLayout.addWidget(resetLearningCheckBox, 1, 1)
        otherOptionsBoxLayout.setRowStretch(2, 1)
        otherOptionsBox.setLayout(otherOptionsBoxLayout)

        # rightFrame layout
        rightGrid = QtGui.QGridLayout()
        rightGrid.addWidget(RLParameterBox, 0, 1)
        rightGrid.addWidget(RLTrainingBox, 1, 1)
        rightGrid.addWidget(otherOptionsBox, 2, 1)
        rightGrid.setRowStretch(0, 0)
        rightGrid.setRowStretch(1, 0)
        rightGrid.setRowStretch(2, 0)
        rightGrid.setRowStretch(2, 1)
        rightGrid.setColumnStretch(0, 1)
        rightGrid.setColumnStretch(1, 0)
        self.rightFrame.setLayout(rightGrid)

        # bottomFrame layout
        self.bottomGrid.setAlignment(QtCore.Qt.AlignLeft)
        self.bottomGrid.setContentsMargins(0, 10, 0, 10)
        self.bottomFrame.setLayout(self.bottomGrid)

        # statusFrame layout
        statusGrid = QtGui.QHBoxLayout()
        statusGrid.setContentsMargins(0, 0, 0, 0)
        statusGrid.addWidget(self.mapNameLabel)
        self.statusFrame.setLayout(statusGrid)

        # main window layout
        mainGrid = QtGui.QGridLayout()
        mainGrid.setColumnStretch(0, 1)
        mainGrid.setColumnStretch(1, 0)
        mainGrid.setRowStretch(0, 1)
        mainGrid.setRowStretch(1, 0)
        mainGrid.setRowStretch(2, 0)
        mainGrid.setColumnMinimumWidth(1, 215)
        mainGrid.setRowMinimumHeight(1, 100)
        mainGrid.setRowMinimumHeight(1, 25)
        mainGrid.setSpacing(10)
        mainGrid.setContentsMargins(10, 10, 10, 10)
        centralWidget.setLayout(mainGrid)
        mainGrid.addWidget(self.leftFrame, 0, 0)
        mainGrid.addWidget(self.rightFrame, 0, 1)
        mainGrid.addWidget(self.bottomFrame, 1, 0, 1, 2)
        mainGrid.addWidget(self.statusFrame, 2, 0, 1, 2)

        # create the first environment
        self.addNewEnvironment()

        # main window parameters
        self.setGeometry(100, 100, 810, 1)
        self.setWindowTitle("HRL-CD Experiment Software")
        # self.setWindowIcon(QtGui.QIcon("images/wall-brick.png"))
        self.show()
        self.leftFrame.setMaximumWidth(self.leftFrame.height())

    def resizeEvent(self, event):
        self.leftFrame.setMaximumWidth(self.leftFrame.height())

    def updateGridSS(self):
        QtGui.QPixmap.grabWidget(self.leftStackedLayout.currentWidget()).save("ssGrid/env{0}.png".format(self.leftStackedLayout.currentIndex() + 1), "png")
        self.bottomGrid.itemAt(self.leftStackedLayout.currentIndex()).widget().setIcon(QtGui.QIcon("ssGrid/env{0}.png".format(self.leftStackedLayout.currentIndex() + 1)))
        self.bottomGrid.itemAt(self.leftStackedLayout.currentIndex()).widget().setIconSize(QSize(96, 96))

    def toggleGenerateSequenceOption(self):
        self.generateSequence = not self.generateSequence

    def toggleResetLearningOption(self):
        self.resetLearning = not self.resetLearning

    def toggleNumOfEpisodesForTrainingSpinbox(self, state):
        self.numOfEpisodesForTrainingSpinBox.setDisabled(state)

    def setImmRewardAtGoal(self, immRewardAtGoal):
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        environment.stateList[environment.goalCoordinates].immReward = immRewardAtGoal
        environment.setImmRewardAtGoal(immRewardAtGoal)

    def showMaxOptionsOnGrid(self):
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        buttonList = environment.buttonList
        stateList = environment.stateList
        gridSize = environment.gridSize
        for row in range(0, gridSize[0]):
            for col in range(0, gridSize[1]):
                if (row, col) == environment.startCoordinates:
                    buttonList[row][col].setText("😎")
                elif stateList[row][col].isGoal:
                    buttonList[row][col].setText("⚑")
                else:
                    maxOption = stateList[row][col].getBestOption()
                    if maxOption is None:
                        continue
                    elif maxOption.QValue == 0:
                        buttonList[row][col].setText("")
                    else:
                        if (row, col) != environment.startCoordinates and (row, col) != environment.goalCoordinates:
                            maxOptionType = maxOption.optionType
                            if maxOptionType == "U":
                                buttonList[row][col].setText("↑")
                            elif maxOptionType == "R":
                                buttonList[row][col].setText("→")
                            elif maxOptionType == "D":
                                buttonList[row][col].setText("↓")
                            elif maxOptionType == "L":
                                buttonList[row][col].setText("←")
                            else:
                                buttonList[row][col].setText(maxOptionType)

    def showNumberOfVisitsOnGrid(self):
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        environment.updateMapMatrixFromStateList()
        buttonList = environment.buttonList
        stateList = environment.stateList
        mapMatrix = environment.mapMatrix
        gridSize = environment.gridSize
        for row in range(0, gridSize[0]):
            for col in range(0, gridSize[1]):
                buttonList[row][col].setText(str(stateList[row][col].numberOfVisits))

    def showOptionsOnGrid(self):
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        environment.updateMapMatrixFromStateList()
        buttonList = environment.buttonList
        stateList = environment.stateList
        mapMatrix = environment.mapMatrix
        gridSize = environment.gridSize
        gr = GraphX()
        gr.createMapToGraph(mapMatrix)
        gr.setInitiationSets(5, 0.03, 3, environment.goalCoordinates)
        initSets = gr.initiationSets
        # print(initSets)
        colorList = ["lightblue", "red", "green", "gray", "wheat", "aqua", "lightgreen", "orange"]
        colorInd = 0

        subGoals = []
        for key, value in initSets.items():
        #     # print(key)
            subGoals.append(key)
            subGoalRow, subGoalCol = key.split("_")
            buttonList[int(subGoalRow)][int(subGoalCol)].setText(key)

        key = initSets["19_19"]
        print(key)
        for item in initSets["19_19"]:
            stateRow, stateCol = item.split("_")
            buttonList[int(stateRow)][int(stateCol)].changeBackgroundColor(colorList[colorInd])
        colorInd += 1

    def drawGraphFromPartialModel(self):
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        environment.graph.drawGraph()

    def printMapMatrix(self):
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        environment.updateMapMatrixFromStateList()
        print(environment.mapMatrix)

    def printPartialMapMatrix(self):
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        environment.updateMapMatrixFromStateList()
        print(environment.partialMapMatrix)
        gr = GraphX(environment.partialMapMatrix)
        bc = gr.betcen
        print(bc)

    def loadMapFile(self):

        # get file name
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Select Map File", "mapFiles/", "GWMAPs (*.gwmap)")

        # if file exists
        if os.path.isfile(fileName[0]):

            # open file
            mapFile = open(fileName[0], "r")

            # get start and goal coordinates
            startCoordinates = mapFile.readline().strip().split()
            goalCoordinates = mapFile.readline().strip().split()
            coordinateList = [startCoordinates, goalCoordinates]

            # check cardinality and non-negativity
            if len(startCoordinates) != 2 or len(goalCoordinates) != 2:
                QtGui.QMessageBox.critical(self, "Error", "Start or goal coordinates are not valid.")
                return
            if not (all(cd[0].isdecimal() for cd in coordinateList) and all(cd[1].isdecimal() for cd in coordinateList)):
                QtGui.QMessageBox.critical(self, "Error", "Start and goal coordinates must be non-negative integers.")
                return
            if any(int(cd[0]) < 0 for cd in coordinateList) or any(int(cd[1]) < 0 for cd in coordinateList):
                QtGui.QMessageBox.critical(self, "Error", "Start and goal coordinates must be non-negative.")
                return

            # get current environment
            environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]

            # read matrix
            environment.mapMatrix = np.genfromtxt(fileName[0], dtype="str", skip_header=3)
            environment.gridSize = environment.mapMatrix.shape

            # check if start and goal states are inside the grid
            if any(int(cd[0]) >= environment.gridSize[0] for cd in coordinateList) or any(int(cd[1]) >= environment.gridSize[1] for cd in coordinateList):
                QtGui.QMessageBox.critical(self, "Error", "Start and goal must be inside the grid.")
                return

            # update mapFileName and start & goal coordinates
            environment.mapFileName = fileName[0]
            environment.startCoordinates = (int(startCoordinates[0]), int(startCoordinates[1]))
            environment.goalCoordinates = (int(goalCoordinates[0]), int(goalCoordinates[1]))

            # close file
            mapFile.close()

            # update stateList
            environment.updateStateListFromMapMatrix()

            # redraw grid
            self.reDrawEnvironment()

            # reset partial map matrix
            environment.resetMapProperties()

            # update ss
            self.bottomGrid.itemAt(self.leftStackedLayout.currentIndex()).widget().animateClick()

    def saveMapFile(self):

        # get current environment
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]

        # if current map file does not exist
        if not os.path.isfile(environment.mapFileName):

            # get new file name
            fileName = QtGui.QFileDialog.getSaveFileName(self, "Save file", "mapFiles/", "*.gwmap")

            # valid file name
            if fileName[0]:
                fileNameToSave = fileName[0]

            # null file name
            else:
                return

        # if current map file exists
        else:
            fileNameToSave = environment.mapFileName

        # build header lines
        headerString = str(environment.startCoordinates[0]) + " " + str(environment.startCoordinates[1]) + "\n" + str(environment.goalCoordinates[0]) + " " + str(environment.goalCoordinates[1]) + "\n"

        # save it!
        np.savetxt(fileNameToSave, environment.mapMatrix, header=headerString, comments="", fmt="%c")

        # update necessary fields
        environment.mapFileName = fileNameToSave
        self.mapNameLabel.setText(fileNameToSave)

        # show success message
        QtGui.QMessageBox.information(self, "Information", "Map successfully saved.")

    def saveACopyFile(self):

        # get current environment
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]

        # get a new filename
        fileName = QtGui.QFileDialog.getSaveFileName(self, "Save file", "mapFiles/", "*.gwmap")

        # valid file name
        if fileName[0]:

            # build header lines
            headerString = str(environment.startCoordinates[0]) + " " + str(environment.startCoordinates[1]) + "\n" + str(environment.goalCoordinates[0]) + " " + str(environment.goalCoordinates[1]) + "\n"

            # save it!
            np.savetxt(fileName[0], np.matrix(environment.mapMatrix), header=headerString, comments="", fmt="%s")

            # update map name label
            self.mapNameLabel.setText(fileName[0])

            # show success message
            QtGui.QMessageBox.information(self, "Information", "Map successfully saved.")

        # null file name
        else:
            return

    def reDrawEnvironment(self):
        self.clearEnvironment()
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        environment.updateButtonListFromStateList()
        stateList = environment.stateList
        buttonList = environment.buttonList
        gridSize = environment.gridSize
        self.mapNameLabel.setText(environment.mapFileName)
        for row in range(0, gridSize[0]):
            for col in range(0, gridSize[1]):
                currentButton = buttonList[row][col]

                addWallToLeft = QtGui.QAction(self)
                addWallToLeft.setText("Wall to Left")
                addWallToLeft.setCheckable(True)
                addWallToLeft.triggered.connect(lambda row=row, col=col: environment.toggleWall("1000", row, col, False))
                if stateList[row][col].stateType in ["8", "9", "A", "B", "C", "D", "E", "F"]:
                    addWallToLeft.setChecked(True)

                addWallToUp = QtGui.QAction(self)
                addWallToUp.setText("Wall to Top")
                addWallToUp.setCheckable(True)
                addWallToUp.triggered.connect(lambda row=row, col=col: environment.toggleWall("0100", row, col, False))
                if stateList[row][col].stateType in ["4", "5", "6", "7", "C", "D", "E", "F"]:
                    addWallToUp.setChecked(True)

                addWallToRight = QtGui.QAction(self)
                addWallToRight.setText("Wall to Right")
                addWallToRight.setCheckable(True)
                addWallToRight.triggered.connect(lambda row=row, col=col: environment.toggleWall("0010", row, col, False))
                if stateList[row][col].stateType in ["2", "3", "6", "7", "A", "B", "E", "F"]:
                    addWallToRight.setChecked(True)

                addWallToDown = QtGui.QAction(self)
                addWallToDown.setText("Wall to Bottom")
                addWallToDown.setCheckable(True)
                addWallToDown.triggered.connect(lambda row=row, col=col: environment.toggleWall("0001", row, col, False))
                if stateList[row][col].stateType in ["1", "3", "5", "7", "9", "B", "D", "F"]:
                    addWallToDown.setChecked(True)

                convertToStart = QtGui.QAction(self)
                convertToStart.setText("START")
                convertToStart.setIcon(QtGui.QIcon("images/start-bw.png"))
                convertToStart.triggered.connect(lambda row=row, col=col: environment.toggleStartGoal("START", row, col))

                convertToGoal = QtGui.QAction(self)
                convertToGoal.setText("GOAL")
                convertToGoal.setIcon(QtGui.QIcon("images/goal-bw.png"))
                convertToGoal.triggered.connect(lambda row=row, col=col: environment.toggleStartGoal("GOAL", row, col))

                printMaxAction = QtGui.QAction(self)
                printMaxAction.setText("State Information")
                printMaxAction.triggered.connect(lambda row=row, col=col: environment.stateInformation(row, col))

                separator1 = QtGui.QAction(self)
                separator1.setSeparator(True)
                separator2 = QtGui.QAction(self)
                separator2.setSeparator(True)

                currentButton.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
                currentButton.addAction(addWallToLeft)
                currentButton.addAction(addWallToUp)
                currentButton.addAction(addWallToRight)
                currentButton.addAction(addWallToDown)
                currentButton.addAction(separator1)
                currentButton.addAction(convertToStart)
                currentButton.addAction(convertToGoal)
                currentButton.addAction(separator2)
                currentButton.addAction(printMaxAction)

                currentButton.clicked.connect(lambda row=row, col=col: environment.stateInformation(row, col))
                self.leftStackedLayout.currentWidget().layout().addWidget(currentButton, row, col)

    def changeGridSize(self):
        text, ok = QtGui.QInputDialog.getText(self, "Change Grid Size", "Enter new size \"row*col\":")
        if ok:
            if str(text).count("*") == 1:
                newSize = str(text).strip().split("*", 2)
                if newSize[0].isdigit() and newSize[1].isdigit():
                    newSize = (int(newSize[0]), int(newSize[1]))
                    self.clearEnvironment()
                    self.RLTask.environmentList[self.leftStackedLayout.currentIndex()] = Environment(newSize)
                    self.reDrawEnvironment()
                    self.bottomGrid.itemAt(self.leftStackedLayout.currentIndex()).widget().animateClick()
                else:
                    QtGui.QMessageBox.critical(None, "Exception", "Sizes should be positive integers.", QtGui.QMessageBox.Abort)
            else:
                QtGui.QMessageBox.critical(None, "Exception", "Wrong input format.", QtGui.QMessageBox.Abort)

    def addNewEnvironment(self):
        self.RLTask.environmentList.append(Environment((5, 5)))
        envWid = QtGui.QWidget()
        leftGrid = QtGui.QGridLayout()
        leftGrid.setSpacing(0)
        leftGrid.setContentsMargins(0, 0, 0, 0)
        envWid.setLayout(leftGrid)
        self.leftStackedLayout.addWidget(envWid)
        envButton = QtGui.QPushButton()
        envButton.setFixedSize(100, 100)
        envButton.clicked.connect(lambda num=self.leftStackedLayout.count() - 1: self.changeEnvironment(num))
        self.bottomGrid.addWidget(envButton)
        self.leftStackedLayout.setCurrentIndex(self.leftStackedLayout.count() - 1)
        self.reDrawEnvironment()
        envButton.animateClick()

    def changeEnvironment(self, num):
        self.leftStackedLayout.setCurrentIndex(num)
        self.mapNameLabel.setText(self.RLTask.environmentList[self.leftStackedLayout.currentIndex()].mapFileName)
        for i in range(0, self.leftStackedLayout.count()):
            if i == num:
                self.bottomGrid.itemAt(i).widget().setStyleSheet("QPushButton { border: 2px dashed black}")
            else:
                self.bottomGrid.itemAt(i).widget().setStyleSheet("QPushButton { border: 2px solid black}")
        self.menuBar.findChildren(QtGui.QMenu)[1].actions()[2].trigger()

    def clearEnvironment(self):
        layoutToClear = self.leftStackedLayout.currentWidget().layout()
        for i in reversed(range(layoutToClear.count())):
            widgetToRemove = layoutToClear.itemAt(i).widget()
            layoutToClear.removeWidget(widgetToRemove)
            widgetToRemove.setParent(None)


def cleanSSFolder():
    files = glob.glob("ssGrid/*.png")
    for f in files:
        os.remove(f)


def main():
    app = QtGui.QApplication(sys.argv)
    app.setStyle("gtk")
    QtGui.QFontDatabase.addApplicationFont("resources/DejaVuSans.ttf")
    mainUI = MainUI()
    atexit.register(cleanSSFolder)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
