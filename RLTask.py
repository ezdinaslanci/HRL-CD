from collections import deque, defaultdict
from statistics import variance
from threading import Thread, Lock, Condition

import copy

import math
from PySide import QtGui

from PQueue import PQueue


class RLTask:

    def __init__(self, mainUI):
        self.mainUI = mainUI
        self.environmentList = []

        # RL parameters
        self.alpha = 0.2
        self.discountFactor = 0.90
        self.maxEpsilon = 0.35
        self.minEpsilon = 0.00001
        self.epsilonDecayFactor = 0.99992
        self.epsilonDecayMode = "episode"
        self.currentEpsilon = self.maxEpsilon
        self.immRewardAtGoal = 50
        self.actionDictionary = {"LEFT": "1", 'UP': "2", "RIGHT": "3", "DOWN": "4"}

        # PS parameters
        self.PQueue = PQueue()
        self.priorityThreshold = 0.0000000001
        self.numOfUpdates = 15

        # training parameters
        self.trainUntilConvergence = True
        self.numOfEpisodesForTraining = 1000

        # convergence parameters
        self.convergenceInterval = 15
        self.varianceThreshold = 0.3
        self.lastNStepsQueue = deque(maxlen=self.convergenceInterval)

        # other parameters
        self.isTraining = False

        # training threads
        self.QLThread = None
        self.PSThread = None

        # action sequence output
        self.sequenceFileName = "outputFiles/actionSequence.dat"

        # ssGrid folder
        self.ssGridFolder = "ssGrid"

        self.options = defaultdict(list)

    def setMaxEpsilon(self, maxEpsilon):
        self.maxEpsilon = maxEpsilon

    def setMinEpsilon(self, minEpsilon):
        self.minEpsilon = minEpsilon

    def setAlpha(self, alpha):
        self.alpha = alpha

    def setDiscountFactor(self, discountFactor):
        self.discountFactor = discountFactor

    def setEpsilonDecayFactor(self, epsilonDecayFactor):
        self.epsilonDecayFactor = epsilonDecayFactor

    def setEpsilonDecayMode(self, epsilonDecayMode):
        self.epsilonDecayMode = epsilonDecayMode

    def setNumOfUpdates(self, numOfUpdates):
        self.numOfUpdates = numOfUpdates

    def setPriorityThreshold(self, priorityThreshold):
        self.priorityThreshold = priorityThreshold

    def setImmRewardAtGoal(self, immRewardAtGoal):
        self.immRewardAtGoal = immRewardAtGoal

    def setConvergenceInterval(self, convergenceInterval):
        self.convergenceInterval = int(convergenceInterval)
        self.lastNStepsQueue = deque(maxlen=self.convergenceInterval)

    def setConvergenceThreshold(self, convergenceThreshold):
        self.varianceThreshold = convergenceThreshold

    def toggleTrainUntilConvergenceOption(self):
        self.trainUntilConvergence = not self.trainUntilConvergence
        self.mainUI.toggleNumOfEpisodesForTrainingSpinbox(self.trainUntilConvergence)

    def setNumOfEpisodesForTraining(self, numOfEpisodesForTraining):
        self.numOfEpisodesForTraining = numOfEpisodesForTraining

    def QLThreadStart(self):
        self.QLThread = Thread(target=self.applyQLearning)
        self.QLThread.start()

    def PSThreadStart(self):
        self.PSThread = Thread(target=self.applyPrioritizedSweeping)
        self.PSThread.start()

    def setInitiationSetThreadStart(self):
        self.initiationSetThread = Thread(target=self.setInitiationSet)
        self.initiationSetThread.start()

    def setInitiationSet(self):
        environmentNum = self.mainUI.leftStackedLayout.currentIndex()
        environment = self.environmentList[environmentNum]
        while self.isTraining:
            environment.graph.setInitiationSets(5, 0.03, 3, environment.goalCoordinates)
        return

    def applyQLearning(self):

        self.isTraining = True

        environmentNum = self.mainUI.leftStackedLayout.currentIndex()
        environment = self.environmentList[environmentNum]
        gridSize = environment.gridSize
        stateList = environment.stateList

        if environment.startCoordinates.count(None) + environment.goalCoordinates.count(None) > 0:
            QtGui.QMessageBox.critical(None, "Missing Parameters", "Please set start and goal states.")
            return

        if self.mainUI.resetLearning:
            environment.resetLearning()
            self.lastNStepsQueue.clear()
            sequenceFile = open(self.sequenceFileName, "w")
            sequenceFile.close()

        numOfEpisodes = numOfActionsInEpisode = totalNumOfActions = 0
        self.currentEpsilon = self.maxEpsilon

        if self.mainUI.generateSequence:
            actionSequence = []

        # episode loop
        while True:

            self.resetVisitInformation()

            agentCurrentCoordinates = self.environmentList[environmentNum].startCoordinates
            numOfEpisodes += 1
            numOfActionsInEpisode = 0

            # action loop
            nextState = stateList[agentCurrentCoordinates]
            while not nextState.isGoal:
                currentState = stateList[agentCurrentCoordinates]

                if not currentState.isVisitedInEpisode:
                    currentState.numberOfVisits += 1
                    currentState.isVisitedInEpisode = True

                chosenAction = currentState.getOption(self.currentEpsilon)
                destinationCoordinates = chosenAction.getDestinationCoordinates()
                destinationCoordinates = (destinationCoordinates[0] % gridSize[0], destinationCoordinates[1] % gridSize[1])
                nextState = stateList[destinationCoordinates]
                chosenAction.QValue += self.alpha * (nextState.immReward + self.discountFactor * nextState.getMaxQValue() - chosenAction.QValue)
                agentCurrentCoordinates = destinationCoordinates
                numOfActionsInEpisode += 1
                if self.mainUI.generateSequence:
                    actionSequence.append(self.actionDictionary[chosenAction.actionType])
                if self.epsilonDecayMode == "step" and self.currentEpsilon > self.minEpsilon:
                    self.currentEpsilon *= self.epsilonDecayFactor

            self.lastNStepsQueue.append(numOfActionsInEpisode)
            totalNumOfActions += numOfActionsInEpisode
            if self.epsilonDecayMode == "episode" and self.currentEpsilon > self.minEpsilon:
                self.currentEpsilon *= self.epsilonDecayFactor

            if not self.trainUntilConvergence and numOfEpisodes >= self.numOfEpisodesForTraining:
                print("QL trained for %d episodes, %d actions, optimal* path has %d actions." % (numOfEpisodes, totalNumOfActions, min(self.lastNStepsQueue)))
                self.isTraining = False
                self.mainUI.showMaxOptionsOnGrid()
                # self.mainUI.showNumberOfVisitsOnGrid()
                if self.mainUI.generateSequence:
                    sequenceFile = open(self.sequenceFileName, "a")
                    for action in actionSequence:
                        sequenceFile.write("%s\n" % action)
                    sequenceFile.close()
                break

            if self.trainUntilConvergence and len(self.lastNStepsQueue) == self.convergenceInterval and variance(self.lastNStepsQueue) <= self.varianceThreshold:
                print("QL converged in %d episodes, %d actions, optimal* path has %d actions." % (numOfEpisodes, totalNumOfActions, min(self.lastNStepsQueue)))
                self.isTraining = False
                self.mainUI.showMaxOptionsOnGrid()
                # self.mainUI.showNumberOfVisitsOnGrid()
                if self.mainUI.generateSequence:
                    sequenceFile = open(self.sequenceFileName, "a")
                    for action in actionSequence:
                        sequenceFile.write("%s\n" % action)
                    sequenceFile.close()
                break

        return

    def applyPrioritizedSweeping(self):

        # started training
        self.isTraining = True

        # clear priority queue
        self.PQueue.clear()

        # get data holders
        environmentNum = self.mainUI.leftStackedLayout.currentIndex()
        environment = self.environmentList[environmentNum]
        gridSize = environment.gridSize
        stateList = environment.stateList

        # check if goal state exists
        if environment.startCoordinates.count(None) + environment.goalCoordinates.count(None) > 0:
            QtGui.QMessageBox.critical(None, "Missing Parameters", "Please set start and goal states.")
            return

        # reset learning if specified
        if self.mainUI.resetLearning:
            environment.resetLearning()
            environment.resetMapProperties()
            self.lastNStepsQueue.clear()
            self.clearSequenceFile()

        # initialize counters
        numOfEpisodes = totalNumOfActions = 0

        # set epsilon to max
        self.currentEpsilon = self.maxEpsilon

        # create sequence holder if specified
        if self.mainUI.generateSequence:
            actionSequence = []

        # episode loop
        while True:

            # start looking for subgoals after 5 episodes
            if numOfEpisodes == 5:
                self.setInitiationSetThreadStart()

            self.resetVisitInformation()

            # place the agent on the start state
            agentCurrentCoordinates = self.environmentList[environmentNum].startCoordinates

            # increment episode number
            numOfEpisodes += 1

            # reset number of steps taken
            numOfActionsInEpisode = 0

            # reset path followed in episode
            pathFollowedInEpisode = []

            # action loop
            nextState = stateList[agentCurrentCoordinates]
            while not nextState.isGoal:

                # get the current state
                currentState = stateList[agentCurrentCoordinates]

                # update visit information
                if not currentState.isVisitedInEpisode:
                    currentState.numberOfVisits += 1
                    currentState.isVisitedInEpisode = True

                # select an option
                chosenOption = currentState.getOption(self.currentEpsilon)

                # get the destination coordinates
                destinationCoordinates = chosenOption.getDestinationCoordinates()
                destinationCoordinates = (destinationCoordinates[0] % gridSize[0], destinationCoordinates[1] % gridSize[1])

                # get the next state
                nextState = stateList[destinationCoordinates]

                # calculate priority
                priority = abs(nextState.immReward + self.discountFactor * nextState.getMaxQValue() - chosenOption.QValue)

                # insert to partial model and priority queue
                self.insertToModel(chosenOption, nextState, nextState.immReward)
                self.insertToPQueue(chosenOption, priority)

                distance = sum(abs(e - s) for s, e in zip(agentCurrentCoordinates, destinationCoordinates))
                if distance == 1 and not environment.graph.hasEdge(agentCurrentCoordinates, destinationCoordinates):
                    environment.graph.addEdge(agentCurrentCoordinates, destinationCoordinates)

                # move the agent to the next state
                agentCurrentCoordinates = destinationCoordinates

                # update partial map matrix
                environment.partialMapMatrix[agentCurrentCoordinates] = stateList[agentCurrentCoordinates].stateType

                # increment step counter
                numOfActionsInEpisode += 1

                # update path followed in episode
                pathFollowedInEpisode.append(chosenOption.optionType)

                # update sequence if specified
                if self.mainUI.generateSequence:
                    actionSequence.append(self.actionDictionary[chosenOption.actionType])

                # decrease epsilon if "step" mode is selected
                if self.epsilonDecayMode == "step" and self.currentEpsilon > self.minEpsilon:
                    self.currentEpsilon *= self.epsilonDecayFactor

                # sweep loop
                for n in range(int(self.numOfUpdates)):
                    if self.PQueue.ifEmpty():
                        break
                    bestAction = self.PQueue.pop()
                    destinationCoordinates = bestAction.getDestinationCoordinates()
                    destinationCoordinates = (destinationCoordinates[0] % gridSize[0], destinationCoordinates[1] % gridSize[1])
                    nextState = stateList[destinationCoordinates[0]][destinationCoordinates[1]]
                    bestAction.QValue += self.alpha * (nextState.immReward + self.discountFactor * nextState.getMaxQValue() - bestAction.QValue)
                    self.sweep(nextState)

            # update last n steps queue (used for convergence check)
            self.lastNStepsQueue.append(numOfActionsInEpisode)

            # increment total number of steps counter
            totalNumOfActions += numOfActionsInEpisode

            # decrease epsilon if "episode" mode is selected
            if self.epsilonDecayMode == "episode" and self.currentEpsilon > self.minEpsilon:
                self.currentEpsilon *= self.epsilonDecayFactor

            # trained for a specific number of episodes
            if not self.trainUntilConvergence and numOfEpisodes >= self.numOfEpisodesForTraining:
                print("PS trained for %d episodes, %d actions, optimal* path has %d actions." % (numOfEpisodes, totalNumOfActions, min(self.lastNStepsQueue)))
                print(pathFollowedInEpisode)
                self.isTraining = False
                self.mainUI.showMaxOptionsOnGrid()
                if self.mainUI.generateSequence:
                    self.writeSequenceToSequenceFile(actionSequence)
                break

            # trained until convergence
            if self.trainUntilConvergence and len(self.lastNStepsQueue) == self.convergenceInterval and variance(self.lastNStepsQueue) <= self.varianceThreshold:
                print("PS converged in %d episodes, %d actions, optimal* path has %d actions." % (numOfEpisodes, totalNumOfActions, min(self.lastNStepsQueue)))
                print(pathFollowedInEpisode)
                self.isTraining = False
                self.mainUI.showMaxOptionsOnGrid()
                if self.mainUI.generateSequence:
                    self.writeSequenceToSequenceFile(actionSequence)
                break

            # construct options
            self.constructOptions()

    def constructOptions(self):

        # get data holders
        environmentNum = self.mainUI.leftStackedLayout.currentIndex()
        environment = self.environmentList[environmentNum]
        stateList = environment.stateList

        # copy raw option information from graph
        rawOptions = copy.deepcopy(environment.graph.initiationSets)
        # print("env: ", list(environment.graph.initiationSets.keys()))
        # print("org: ", list(self.options.keys()))
        # print("dmy: ", list(rawOptions.keys()), "\n")

        subGoalList = list(self.options.keys())
        if len(subGoalList) > 0:
            print(subGoalList)

        # this loop updates the constructed options (add & remove)
        for subGoal in rawOptions:

            if subGoal in self.options:
                for state in rawOptions[subGoal]:
                    if state in self.options[subGoal]:
                        del self.options[subGoal][self.options[subGoal].index(state)]
                    else:
                        stateRow, stateCol = state.split("_")
                        destStateRow, destStateCol = subGoal.split("_")
                        # print("edited: added ", subGoal, "<-", state)
                        QValue = stateList[int(destStateRow), int(destStateCol)].getMaxQValue()
                        stateList[int(stateRow), int(stateCol)].addOption(subGoal, QValue=QValue)
                for leftState in self.options[subGoal]:
                    stateRow, stateCol = leftState.split("_")
                    stateList[int(stateRow), int(stateCol)].deleteOption(subGoal)
                del self.options[subGoal]

            else:
                for state in rawOptions[subGoal]:
                    stateRow, stateCol = state.split("_")
                    destStateRow, destStateCol = subGoal.split("_")
                    QValue = stateList[int(destStateRow), int(destStateCol)].getMaxQValue()
                    stateList[int(stateRow), int(stateCol)].addOption(subGoal, QValue=QValue)

        for leftSubGoal in self.options:
            for leftState in self.options[leftSubGoal]:
                stateRow, stateCol = leftState.split("_")
                stateList[int(stateRow), int(stateCol)].deleteOption(leftSubGoal)

        # update options
        self.options = rawOptions

    def resetVisitInformation(self):
        environmentNum = self.mainUI.leftStackedLayout.currentIndex()
        environment = self.environmentList[environmentNum]
        gridSize = environment.gridSize
        stateList = environment.stateList
        for row in range(0, gridSize[0]):
            for col in range(0, gridSize[1]):
                stateList[row][col].isVisitedInEpisode = False

    def clearSequenceFile(self):
        sequenceFile = open(self.sequenceFileName, "w")
        sequenceFile.close()

    def writeSequenceToSequenceFile(self, sequence):
        sequenceFile = open(self.sequenceFileName, "a")
        for action in sequence:
            sequenceFile.write("%s\n" % action)
        sequenceFile.close()

    def insertToModel(self, chosenAction, nextState, reward):
        model = self.environmentList[self.mainUI.leftStackedLayout.currentIndex()].model
        # if not (chosenAction, nextState, reward) in model:
        #     model.append((chosenAction, nextState, reward))
        if nextState not in model:
            model[nextState] = {}
            model[nextState][chosenAction] = reward

    def insertToPQueue(self, chosenAction, priority):
        if priority >= self.priorityThreshold:
            self.PQueue.push(chosenAction, priority)
            # print("---------------------------------")
            # self.PQueue.print()

    def calculatePriority(self, chosenAction, nextState):
        return abs(nextState.immReward + self.discountFactor * nextState.getMaxQValue() - chosenAction.QValue)

    def findEntryInModelHeadingState(self, coordinates):
        model = self.environmentList[self.mainUI.leftStackedLayout.currentIndex()].model
        indexList = [i for i, entry in enumerate(model) if entry[1].coordinates == coordinates]
        returnList = []
        for index in indexList:
            returnList.append(model[index])
        return returnList

    def sweep(self, state):
        model = self.environmentList[self.mainUI.leftStackedLayout.currentIndex()].model
        # indexList = [i for i, entry in enumerate(model) if entry[1] == state]
        # for index in indexList:
        #     (actionFromModel, nextStateFromModel, rewardFromModel) = model[index]
        #     priority = abs(rewardFromModel + self.discountFactor * nextStateFromModel.getMaxQValue() - actionFromModel.QValue)
        #     self.insertToPQueue(actionFromModel, priority)
        actionsLeadingToStateDict = model[state]
        for action in actionsLeadingToStateDict:
            rewardFromModel = actionsLeadingToStateDict[action]
            priority = abs(rewardFromModel + self.discountFactor * state.getMaxQValue() - action.QValue)
