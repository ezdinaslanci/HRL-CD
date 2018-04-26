import random

from Option import Option


class State:

    def __init__(self, stateType, coordinates, gridSize):

        # state parameters
        self._stateType = stateType
        self.coordinates = coordinates
        self.gridSize = gridSize
        self.immReward = 0
        self.policies = {"mu": {}}
        self.numberOfVisits = 0
        self.isVisitedInEpisode = False
        self.isGoal = False

        # generate initial action set
        self.generateMicroOptions("mu")

    @property
    def stateType(self):
        return self._stateType

    @stateType.setter
    def stateType(self, stateType):
        if stateType in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]:
            self._stateType = stateType

    @property
    def isGoal(self):
        return self._isGoal

    @isGoal.setter
    def isGoal(self, isGoal):
        if isGoal:
            self.immReward = 50
            self._isGoal = True
        else:
            self.immReward = 0
            self._isGoal = False

    @property
    def immReward(self):
        return self._immReward

    @immReward.setter
    def immReward(self, immReward):
        self._immReward = immReward

    def generateMicroOptions(self, policy="mu"):
        if policy in self.policies:
            if self.stateType not in ["8", "9", "A", "B", "C", "D", "E", "F"]:
                self.policies[policy]["L"] = Option("L", self.coordinates)
            if self.stateType not in ["4", "5", "6", "7", "C", "D", "E", "F"]:
                self.policies[policy]["U"] = Option("U", self.coordinates)
            if self.stateType not in ["2", "3", "6", "7", "A", "B", "E", "F"]:
                self.policies[policy]["R"] = Option("R", self.coordinates)
            if self.stateType not in ["1", "3", "5", "7", "9", "B", "D", "F"]:
                self.policies[policy]["D"] = Option("D", self.coordinates)

    def resetState(self):
        del self.policies
        self.policies = {"mu": {}}
        self.generateMicroOptions("mu")

    def addOption(self, optionType, policy="mu", QValue=0.0):
        if optionType not in self.policies[policy]:
            self.policies[policy][optionType] = Option(optionType, self.coordinates, QValue)
            if optionType not in ["L", "U", "R", "D"] and optionType not in self.policies.keys():
                self.policies[optionType] = {}
                self.generateMicroOptions(optionType)

    def deleteOption(self, optionType, policy="mu"):
        if optionType in self.policies[policy]:
            del self.policies[policy][optionType]
            if optionType not in ["L", "U", "R", "D"] and optionType in self.policies.keys():
                del self.policies[optionType]

    def toggleOption(self, optionType, policy="mu"):
        if optionType not in self.policies[policy]:
            self.policies[policy][optionType] = Option(optionType, self.coordinates)
            if optionType not in ["L", "U", "R", "D"] and optionType not in self.policies.keys():
                self.policies[optionType] = {}
                self.generateMicroOptions(optionType)
        else:
            del self.policies[policy][optionType]
            if optionType not in ["L", "U", "R", "D"] and optionType in self.policies.keys():
                del self.policies[optionType]

    def getBestOption(self, policy="mu"):
        if len(self.policies[policy]) > 0:
            return self.policies[policy][max(self.policies[policy], key=self.policies[policy].get)]
        else:
            return None

    def getOption(self, epsilon, policy="mu"):
        bestOption = self.getBestOption(policy)
        if bestOption.QValue == 0:
            return self.policies[policy][random.choice(list(self.policies[policy].keys()))]
        elif random.uniform(0, 1) <= epsilon:
            return self.policies[policy][random.choice(list(self.policies[policy].keys()))]
        else:
            return bestOption

    def getMaxQValue(self, policy="mu"):
        return self.getBestOption(policy).QValue + self.immReward

    # def getFairOption(self, epsilon):
    #     maxOption = max(self.policies, key=attrgetter('QValue'))
    #     maxOptionList = []
    #     nonMaxOptionList = []
    #     for option in self.policies:
    #         if option.QValue == maxOption.QValue:
    #             maxOptionList.append(option)
    #         else:
    #             nonMaxOptionList.append(option)
    #     if nonMaxOptionList and random.uniform(0, 1) <= epsilon:
    #         return random.choice(nonMaxOptionList)
    #     else:
    #         return random.choice(maxOptionList)

    def getQValues(self, policy="mu"):
        QValues = {}
        for optionType in self.policies[policy]:
            option = self.policies[policy][optionType]
            QValues[option.optionType] = float("%.3f" % option.QValue)
        return QValues
