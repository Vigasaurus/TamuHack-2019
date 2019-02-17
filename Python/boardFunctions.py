import serial
import time
import imageio as img
import numpy as np
import statistics

firstTime = True
url = 'http://10.110.30.50:8080/shot.jpg'  # Korey
# rl = 'http://10.110.3.124:8080/shot.jpg' # Vignesh
currentBoardState = [
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
]
newColorGrid = np.array([  # fresh game
    [2, 2, 2, 2, 2, 2, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
])
# create grid point arrays
grid_arr_x = np.zeros([9, 9])
grid_arr_y = np.zeros([9, 9])


class trackDot:
    """Object used to find the position of the colored tracking dots"""

    def __init__(self, color):
        self.color = color
        self.x_list = []  # used by median
        self.y_list = []  # used by median
    #    self.x_sum = 0  # used by mean
    #    self.y_sum = 0  # used by mean
        self.pixel_count = 0

    def addPixel(self, x, y):
        self.x_list.append(x)  # used by median
        self.y_list.append(y)  # used by median
    #    self.x_sum += x  # used by mean
    #    self.y_sum += y  # used by mean
        self.pixel_count += 1

    def findMedian(self):
        return (statistics.median_high(self.x_list), statistics.median_high(self.y_list))


def DetermineChangedPiece(originalPositions, newPositions):
    oldIndex = []
    newIndex = []
    #rint(originalPositions, '\n')
    # print(newPositions)
    for i in range(0, 8):
        for j in range(0, 8):
            if ((originalPositions[i][j] == 1 or originalPositions[i][j] == 2) and newPositions[i][j] == 0):
                oldIndex = [i, j]
                #print('New == 0', i, j)
            elif (originalPositions[i][j] == 0 and newPositions[i][j] == 1):
                newIndex = [i, j]
                #print('New == 1 - Old == 0', i, j)
            elif (originalPositions[i][j] == 0 and newPositions[i][j] == 2):
                newIndex = [i, j]
                #print('New == 2 - Old == 0', i, j)
            elif (originalPositions[i][j] == 1 and newPositions[i][j] == 2):
                newIndex = [i, j]
                #print('New == 2 - Old == 1', i, j)
            elif (originalPositions[i][j] == 2 and newPositions[i][j] == 1):
                newIndex = [i, j]
                #print('New == 1 - Old == 2', i, j)
    return oldIndex, newIndex


def MovePiece(positionOne, positionTwo):
    # print(currentBoardState[positionOne[0]][positionOne[1]])
    # print(currentBoardState[positionTwo[0]][positionTwo[1]])

    currentBoardState[positionTwo[0]][positionTwo[1]
                                      ] = currentBoardState[positionOne[0]][positionOne[1]]
    currentBoardState[positionOne[0]][positionOne[1]] = ''
    return currentBoardState


def linify(p1, p2, p3, p4):
    """
    :param p1: array of size 2 representing (x, y) coordinates for the upper left point
    :param p2: array of size 2 representing (x, y) coordinates for the upper right point
    :param p3: array of size 2 representing (x, y) coordinates for the lower left point
    :param p4: array of size 2 representing (x, y) coordinates for the lower right point
    :return: array of size 9x9x2 representing all intersection points on the gameplay grid
    """

    persp_scalar_y = [1, 0.9, 0.9125, 0.9125, 0.925, 0.925, 0.9625, 0.975, 1]

    # terminal brain cancer
    top_interval_x = (p2[0] - p1[0]) / 8
    top_interval_y = (p2[1] - p1[1]) / 8
    bottom_interval_x = (p4[0] - p3[0]) / 8
    bottom_interval_y = (p4[1] - p3[1]) / 8
    left_interval_x = (p3[0] - p1[0]) / 8
    left_interval_y = (p3[1] - p1[1]) / 8
    right_interval_x = (p4[0] - p2[0]) / 8
    right_interval_y = (p4[1] - p2[1]) / 8

    # create outside line edge
    for i in range(0, 9):
        # find top grid line
        grid_arr_x[0][i] = (top_interval_x * i) + p1[0]
        grid_arr_y[0][i] = (top_interval_y * i) + p1[1]
        # find bottom grid line
        grid_arr_x[8][i] = (bottom_interval_x * i) + p3[0]
        grid_arr_y[8][i] = (bottom_interval_y * i) + p3[1]
        # find left grid line
        grid_arr_x[i][0] = (left_interval_x * i * persp_scalar_y[i]) + p1[0]
        grid_arr_y[i][0] = (left_interval_y * i) + p1[1]
        # find right grid line
        grid_arr_x[i][8] = (right_interval_x * i * persp_scalar_y[i]) + p2[0]
        grid_arr_y[i][8] = (right_interval_y * i) + p2[1]

    # fill in array
    for col in range(1, 8):
        col_interval_x = (grid_arr_x[8][col]-grid_arr_x[0][col]) / 8
        col_interval_y = (grid_arr_y[8][col]-grid_arr_y[0][col]) / 8
        for row in range(1, 8):
            grid_arr_x[row][col] = int(
                (col_interval_x * row * persp_scalar_y[row]) + grid_arr_x[0][col])
            grid_arr_y[row][col] = int(
                (col_interval_y * row) + grid_arr_y[0][col])

# draws little Xs on the corners of all the squares


def draw_intersections(image_pass):
    """
    :param image: image to draw intersection points on
    :return: image with drawn points
    """
    for row in range(0, 9):
        for col in range(0, 9):
            for i in range(-5, 6):
                try:
                    image_pass[int(grid_arr_x[row][col])][int(
                        grid_arr_y[row][col])+i] = [0, 150, 255]
                    image_pass[int(grid_arr_x[row][col]) +
                               i][int(grid_arr_y[row][col])] = [0, 150, 255]
                except IndexError:
                    print("Skipping target draw")
    img.imwrite("blue-test3.png", image_pass)


def printMarker(image, center_x, center_y, size, color=[0, 0, 0]):
    """Prints onto image to help debug"""
    modified = False
    for i in range(center_x - size, center_x + size):
        if not(i < 0 or i >= len(image)):
            image[i][center_y] = color
            modified = True
    for j in range(center_y - size, center_y + size):
        if not(j < 0 or j >= len(image[0])):
            image[center_x][j] = color
            modified = True
    if modified:
        print("Marker printed at ", center_x, ",", center_y)
    else:
        # If you are getting this error, don't.
        print(">>>WARNING<<<: Cannot print marker at ",
              center_x, ",", center_y, ", marker is offscreen")


def isColorPink(color):
    # FIXME: test
    return (color[0] > 170) and (70 < color[1] < 130) and (80 < color[2] < 170)


def isColorGreen(color):
    # FIXME: test
    return (80 < color[0] < 145) and (color[1] > 140) and (color[2] < 105)


def isColorBlue(color):
    return (color[0] < 70) and (color[0] > 20) and (color[1] < 130) and (color[1] > 70) and (color[2] < 160) and (color[2] > 100)


# find each of the red dots in a quadrant
def IWillLeaveThatUpToYourDiscretion(image_pass):
    redDots = []
    for row_range in [range(0, len(image_pass)//2), range(len(image_pass)//2, len(image_pass))]:
        # iterates through ranges of 4 quadrants
        for col_range in [range(0, len(image_pass[0])//2), range(len(image_pass[0])//2, len(image_pass[0]))]:
            redDot = trackDot([-1, -1, -1])  # not even using this feature
            for i in row_range:
                for j in col_range:  # for each pixel in image
                    if isColorBlue(image_pass[i][j]):
                        # this pixel is part of this tracking dot
                        redDot.addPixel(i, j)
                        # image_pass[i][j] = [255, 150, 150]
            if redDot.pixel_count != 0:
                # image[dot.x][dot.y] = [200,200,0]
                # printMarker(image, *redDot.findMean(), 10)
                # printMarker(image, *redDot.findMedian(), 10, color=[200,200,200])
                redDots.append(redDot.findMedian())
    # img.imwrite("blue-test1.png", image_pass)
    return redDots


def getGridColors(image):  # sorry for all args being global, but I didn't start the fire
    colormap = np.zeros([8, 8])
    for i in range(1, len(grid_arr_x)):
        for j in range(1, len(grid_arr_y)):  # iterate over bottom-right corners
            green_count = 0
            pink_count = 0
            sample_size = 0
            for offset in range(-1, 2):  # for 3 sample stratifications
                center_x = int(
                    (grid_arr_x[i-1][j-1] + grid_arr_x[i][j-1] + grid_arr_x[i-1][j] + grid_arr_x[i][j]) / 4)
                center_y = int(
                    (grid_arr_y[i-1][j-1] + grid_arr_y[i][j-1] + grid_arr_y[i-1][j] + grid_arr_y[i][j]) / 4)
                # width of sample. Too big width may pickup pieces on adjacent tiles, while too small width may miss pieces not exactly centered
                width = int(
                    abs(3 * (grid_arr_x[i-1][j-1] - grid_arr_x[i][j-1]) // -8))
                # do every 4th pixel in stratisfied sample
                for skipper in range(-width, width, 4):
                    for coords in [[center_x + offset*width, center_y + skipper],  # vertical stratification
                                   [center_x + skipper, center_y + offset*width]]:  # horizontal stratification
                        sample_size += 1
                        if isColorGreen(image[coords[0]][coords[1]]):
                            green_count += 1
                            image[coords[0]][coords[1]] = [200, 90, 120]
                        elif isColorPink(image[coords[0]][coords[1]]):
                            pink_count += 1
                            image[coords[0]][coords[1]] = [100, 140, 60]
                        else:
                            image[coords[0]][coords[1]] = [255, 255, 0]
            # TODO : Check if Pink or Green, and do something with it
            pink_count /= sample_size
            green_count /= sample_size  # convert percentage
            threshold = 0.30  # minimum percent of sample to consider color significant
            if pink_count > threshold:
                colormap[i-1][j-1] = 1
            elif green_count > threshold:
                colormap[i-1][j-1] = 2
    return colormap


def prettyPrintBoard():
    print('-' * 65)
    for i in range(8):
        print('|' + '       |' * 8)
        print('|', end='')
        for j in range(8):
            if currentBoardState[i][j] != '':
                print('   ' + currentBoardState[i][j] + '   |', end='')
            else:
                print('   ' + ' ' + '   |', end='')
        print('\n|' + '       |' * 8)
        print('-' * 65)


def initializeImageProcessing():
    global newColorGrid
    print('Processing...')
    #print("Downloading image...")
    # image = img.imread(url)
    cont = False
    while not cont:
        try:
            image = img.imread(url)
            cont = True
        except:
            print('Error Connecting to Camera - Retrying... ')

    #print("Leaving things up to your discretion (identifying corners)...")
    r1 = 0
    r2 = 0
    r3 = 0
    r4 = 0
    cont = False
    while not cont:
        try:
            r1, r2, r3, r4 = IWillLeaveThatUpToYourDiscretion(image)
            cont = True
        except:
            print(
                'Camera does not have all corners in frame, please reposition board. Retrying...')
    #print("Line-ifying (really grid-itizing)...")
    linify(r1, r2, r3, r4)
    #print("Rendering grid overlay...")
    draw_intersections(image)

    # repeated
    oldColorGrid = newColorGrid
    newColorGrid = getGridColors(image)
    newColorGrid = np.rot90(newColorGrid, 3)
    #print('Old:', oldColorGrid)
    #print('New:', newColorGrid)
    oldIndex, newIndex = DetermineChangedPiece(oldColorGrid, newColorGrid)
    #print('Changed Indices:', oldIndex, newIndex)
    #print('New Board State:', MovePiece(oldIndex, newIndex))
    MovePiece(oldIndex, newIndex)
    # print(grid_arr_x)
    # print(grid_arr_y)
    #print("Saving image...")
    prettyPrintBoard()
    img.imwrite("output.png", image)
    print("Ready for next turn!")


arduino = serial.Serial('com5')

time.sleep(2)

while True:
    input()
    arduino.write(1)
    if (not firstTime):
        initializeImageProcessing()
    firstTime = False
