from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))
import time

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
PAUSE = 0.25

#
# This is the class you have to complete.
#

class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.
    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        t1 = time.time()
        # SORT THE POINTS BY INCREASING X-VALUE
        sortPoints = sorted(points, key=lambda point: point.x())
        t2 = time.time()
        t3 = time.time()
        # this is a dummy polygon of the first 3 unsorted points
        # polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]
        # TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
        polygon = self._divide_conquer(sortPoints, pause, view)
        t4 = time.time()
        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        fullHull = [QLineF(polygon[i], polygon[(i + 1) % len(polygon)])
                    for i in range(len(polygon))]
        self.showHull(fullHull, RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))

    # Divide and conquer function
    # The whole function would have O(n log(n))
    # where n is the number of points in the set, and h is the number of points in the hull
    def _divide_conquer(self, points, pause, view):
        # set the number of points
        numPoints = len(points)
        # when there is only 1 points there is no point of doing it
        if numPoints == 1:
            return points

        # dividing the whole point into two section L and R
        leftHull = self._divide_conquer(points[:numPoints // 2], pause, view)

        rightHull = self._divide_conquer(points[numPoints // 2:], pause, view)

        # If only 1 points on each side merge left and right
        # O(1)
        if len(leftHull) == 1 and len(rightHull) == 1:
            leftHull.extend(rightHull)
            return leftHull

        # Find the right most for left hull
        # At this point the time and space would be o(n) where n is the point
        leftStartPoint = leftHull.index(max(leftHull, key=lambda leftPoint: leftPoint.x()))
        # Find the left most for the right hull
        rightStartPoint = rightHull.index(min(rightHull, key=lambda rightPoint: rightPoint.x()))

        # Find the upper tangent
        # O(n) time for finding the upper tangent
        i = leftStartPoint
        j = rightStartPoint
        leftUpper = True
        rightUpper = True
        slope = (rightHull[j].y() - leftHull[i].y()) /\
                (rightHull[j].x() - leftHull[i].x())
        # go though the point one by one
        while leftUpper or rightUpper:
            leftUpper = False
            rightUpper = False
            while True:
                newSlope = (rightHull[j].y() - leftHull[(i - 1) % len(leftHull)].y()) / (
                        rightHull[j].x() - leftHull[(i - 1) % len(leftHull)].x())
                # compare the slope
                if newSlope < slope:
                    leftUpper = True
                    slope = newSlope
                    i = (i - 1) % len(leftHull)
                else:
                    break
            # for the right side same thing
            while True:
                newSlope = (rightHull[(j + 1) % len(rightHull)].y() - leftHull[i].y()) / (
                        rightHull[(j + 1) % len(rightHull)].x() - leftHull[i].x())
                if newSlope > slope:
                    right = True
                    slope = newSlope
                    j = (j + 1) % len(rightHull)
                else:
                    break
        upper = (i, j)

        # Find the lower tangent
        # Same process with the upper tangent
        # Same with the upper tangent
        # The time would be O(n^2)
        i = leftStartPoint
        j = rightStartPoint
        leftLower = True
        rightLower = True
        slope = (rightHull[j].y() - leftHull[i].y()) / \
                (rightHull[j].x() - leftHull[i].x())
        while leftLower or rightLower:
            leftLower = False
            rightLower = False
            while True:
                # same the upper tangent but in another way
                newSlope = (rightHull[j].y() - leftHull[(i + 1) % len(leftHull)].y()) / (
                        rightHull[j].x() - leftHull[(i + 1) % len(leftHull)].x())
                if newSlope > slope:
                    leftLower = True
                    slope = newSlope
                    i = (i + 1) % len(leftHull)
                else:
                    break
            while True:
                newSlope = (rightHull[(j - 1) % len(rightHull)].y() - leftHull[i].y()) / (
                        rightHull[(j - 1) % len(rightHull)].x() - leftHull[i].x())
                if newSlope < slope:
                    rightLower = True
                    slope = newSlope
                    j = (j - 1) % len(rightHull)
                else:
                    break
        lower = (i, j)

        # Show status in recursion process if it is clicked
        if pause:
            self._show_recursion(leftHull, rightHull, upper, lower)

        # Join the upper and lower tangent together
        # This would also be O(n)
        final = []
        k = lower[0]
        final.append(leftHull[k])

        # Join the upper
        while k != upper[0]:
            k = (k + 1) % len(leftHull)
            final.append(leftHull[k])
        k = upper[1]
        final.append(rightHull[k])

        # Join the lower
        while k != lower[1]:
            k = (k + 1) % len(rightHull)
            final.append(rightHull[k])

        return final

    # Recursion function
    # I use the QlineF so it is easier to keep track of thing and doing the calculation
    # O(n)
    def _show_recursion(self, leftHull, rightHull, upper, lower):
        leftPrint = [QLineF(leftHull[i], leftHull[(i + 1) % len(leftHull)])
                     for i in range(len(leftHull))]
        rightPrint = [QLineF(rightHull[i], rightHull[(i + 1) % len(rightHull)])
                      for i in range(len(rightHull))]
        upperPrint = QLineF(leftHull[upper[0]], rightHull[upper[1]])
        lowerPrint = QLineF(leftHull[lower[0]], rightHull[lower[1]])

        # draw those line and deleteing line
        self.showHull(leftPrint, RED)
        self.showHull(rightPrint, RED)
        self.showTangent([upperPrint, lowerPrint], BLUE)
        self.eraseHull(leftPrint)
        self.eraseHull(rightPrint)
        self.eraseTangent([upperPrint, lowerPrint])
