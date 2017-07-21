import sys, random
from threading import Thread

from PyQt5 import uic, QtWidgets, QtCore, QtGui, QtPrintSupport
from PyQt5.QtGui import QImage, QImageWriter, QPainter, QPen, qRgb
import sched, time

p1 = QtCore.QPoint(0, 0)
p2 = QtCore.QPoint(400, 400)

words = []
with open('categories.txt') as f:
    words = f.read().split()

class ScribbleArea(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ScribbleArea, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_StaticContents)
        self.setMinimumHeight(450)
        self.setMinimumWidth(530)
        self.modified = False
        self.scribbling = False
        self.myPenWidth = 1
        self.myPenColor = QtCore.Qt.blue
        self.image = QtGui.QImage()
        self.lastPoint = QtCore.QPoint()


    def setPenColor(self, newColor):
        self.myPenColor = newColor

    def setPenWidth(self, newWidth):
        self.myPenWidth = newWidth

    def clearImage(self):
        self.image.fill(QtGui.qRgb(255, 255, 255))
        self.modified = True
        self.update()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.lastPoint = event.pos()
            self.scribbling = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & QtCore.Qt.LeftButton) and self.scribbling:
            self.drawLineTo(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.scribbling:
            self.drawLineTo(event.pos())
            self.scribbling = False

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        dirtyRect = event.rect()
        painter.drawImage(dirtyRect, self.image, dirtyRect)

    def resizeEvent(self, event):
        if self.width() > self.image.width() or self.height() > self.image.height():
            newWidth = max(self.width() + 128, self.image.width())
            newHeight = max(self.height() + 128, self.image.height())
            self.resizeImage(self.image, QtCore.QSize(newWidth, newHeight))
            self.update()

        super(ScribbleArea, self).resizeEvent(event)

    def drawLineTo(self, endPoint):
        painter = QtGui.QPainter(self.image)
        painter.setPen(QtGui.QPen(self.myPenColor, self.myPenWidth, QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(self.lastPoint, endPoint)
        self.modified = True

        rad = self.myPenWidth / 2 + 2
        self.update(QtCore.QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
        self.lastPoint = QtCore.QPoint(endPoint)

    def resizeImage(self, image, newSize):
        if image.size() == newSize:
            return

        newImage = QtGui.QImage(newSize, QtGui.QImage.Format_RGB32)
        newImage.fill(qRgb(255, 255, 255))
        painter = QtGui.QPainter(newImage)
        painter.drawImage(QtCore.QPoint(0, 0), image)
        self.image = newImage

    def print_(self):
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)

        printDialog = QtPrintSupport.QPrintDialog(printer, self)
        if printDialog.exec_() == QtPrintSupport.QPrintDialog.Accepted:
            painter = QtGui.QPainter(printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.image.rect())
            painter.drawImage(0, 0, self.image)
            painter.end()

    def isModified(self):
        return self.modified

    def penColor(self):
        return self.myPenColor

    def penWidth(self):
        return self.myPenWidth



class Painter(QtWidgets.QMainWindow):
    def __init__(self):
        super(Painter, self).__init__()
        self.ui = uic.loadUi("DrawGame.ui", self)
        self.time = 5
        self.currentWord = ""
        self.guess = ""
        self.initUI()
        self.cw = ScribbleArea(self.ui.frame)
        self.show()

    def initUI(self):
        self.ui.color.clicked.connect(self.setNewColor)
        self.ui.clear.clicked.connect(self.clearImage)
        self.ui.startGame.clicked.connect(self.startNewRound)
        self.ui.timer.display(self.time)

    def startNewRound(self):
        self.currentWord = random.choice(words).title()
        self.ui.timer.display(self.time)
        self.clearImage()
        self.ui.category.setText(self.currentWord)
        t = Thread(target=self.countdown)
        t.start()

    # Just for testing
    def changeGuess(self, guess):
        self.guess = guess
        self.ui.kiGuess.setText("I think it is: %s" % self.guess)

    def countdown(self):
        x = self.time-1
        for i in range(x, -1, -1):
            time.sleep(1)
            self.changeGuess(random.choice(words).title())
            self.ui.timer.display(i)
        print("Ende")

    def clearImage(self):
        self.cw.clearImage()

    def setNewColor(self):
        col = QtWidgets.QColorDialog.getColor()
        if col.isValid():
            self.cw.setPenColor(col)

    def setKIGuess(self):
        print("Guess:")




def main():
    app = QtWidgets.QApplication(sys.argv)
    paint = Painter()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
