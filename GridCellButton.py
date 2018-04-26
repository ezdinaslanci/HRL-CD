from PySide import QtGui
from PySide.QtCore import QSignalMapper
from PySide.QtGui import QSizePolicy


class GridCellButton(QtGui.QPushButton):

    def __init__(self, stateType):
        super(GridCellButton, self).__init__()
        self.signalMapper = QSignalMapper(self)
        self.stateType = stateType
        self.setMinimumSize(5, 5)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    @property
    def stateType(self):
        return self._stateType

    @stateType.setter
    def stateType(self, stateType):
        try:
            int(stateType, 16)
        except ValueError:
            QtGui.QMessageBox.critical(_, "Error", "Invalid state type in matrix.")
            return

        self._stateType = stateType
        self.setStyleSheet("QPushButton:hover {background-color: #f0f0f0;} QPushButton {background-color: white; border: 1px groove #f0f0f0; font-family: DejaVu Sans;}")

        if stateType == "0":
            pass
        elif stateType in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]:
            self.setStyleSheet(self.styleSheet() + self.buildWallStyle(stateType))
        else:
            return

    def setStart(self, isStart):
        if isStart:
            self.setText("😎")
        else:
            self.setText("")

    def setGoal(self, isGoal):
        if isGoal:
            self.setText("⚑")
            self.setStyleSheet(self.styleSheet() + "QPushButton {color:red}")
        else:
            self.setText("")
            self.setStyleSheet(self.styleSheet() + "QPushButton {color:black}")

    def changeBackgroundColor(self, color):
        self.setStyleSheet(self.styleSheet() + "QPushButton {background-color: " + color + "}")

    @staticmethod
    def buildWallStyle(stateType):
        wallWidth = "2px"
        wallStyle = "solid"
        wallColor = "#262524"
        style = "QPushButton {"
        if stateType in ["8", "9", "A", "B", "C", "D", "E", "F"]:
            style += "border-left-width:" + wallWidth + "; border-left-style: " + wallStyle + "; border-left-color: " + wallColor + ";"
        if stateType in ["4", "5", "6", "7", "C", "D", "E", "F"]:
            style += "border-top-width:" + wallWidth + "; border-top-style: " + wallStyle + "; border-top-color: " + wallColor + ";"
        if stateType in ["2", "3", "6", "7", "A", "B", "E", "F"]:
            style += "border-right-width:" + wallWidth + "; border-right-style: " + wallStyle + "; border-right-color: " + wallColor + ";"
        if stateType in ["1", "3", "5", "7", "9", "B", "D", "F"]:
            style += "border-bottom-width:" + wallWidth + "; border-bottom-style: " + wallStyle + "; border-bottom-color: " + wallColor + ";"
        style += "}"
        return style

    def resizeEvent(self, event):
        fontSize = min(event.size().width(), event.size().height()) * 0.25
        customFont = self.font()
        customFont.setPointSize(fontSize)
        self.setFont(customFont)
