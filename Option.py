
class Option:

    def __init__(self, optionType, coordinates, QValue=0.0):
        if optionType in ["L", "U", "R", "D"] or len(optionType.split("_")) == 2:
            self.optionType = optionType
            self.coordinates = coordinates
            self.QValue = QValue
        else:
            print("UNKNOWN TYPE")

    def getDestinationCoordinates(self):
        if self.optionType == "L":
            return self.coordinates[0], self.coordinates[1] - 1
        elif self.optionType == "U":
            return self.coordinates[0] - 1, self.coordinates[1]
        elif self.optionType == "R":
            return self.coordinates[0], self.coordinates[1] + 1
        elif self.optionType == "D":
            return self.coordinates[0] + 1, self.coordinates[1]
        else:
            coordinateList = self.optionType.split("_")
            return int(coordinateList[0]), int(coordinateList[1])

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.QValue < other.QValue
        return NotImplemented
