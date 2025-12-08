from PIL import ImageGrab, Image
import pyautogui
import time
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Listener, Button, Controller as MouseController
from pynput import mouse
#from numpy import asarray
import math
from time import sleep
from random import randint
#import mss
#import mss.tools

def floor(x):
    return math.floor(x)
def mousevent():
    with mouse.Events() as events:
    # Block at most one second
        event = events.get(1.0)
        if event is None:
            print('You did not interact with the mouse within one second')
        else:
            print('Received event {}'.format(event))
            return event

time.process_time()
image = ImageGrab.grab()
enemies = []
blocks = []
bullets = []

screen = pyautogui.size()[0], pyautogui.size()[1]
print(screen)

relx = 0
rely = 0
bestblockchoice = None
bestenemychoice = None
bestbulletchoice = None
xpos = screen[0] / 2
ypos = screen[1] / 2
direction = [randint(0, 2), randint(0, 2)]
empties = 0
walls = [0, 0]
wallDetectPositions = [(0, 0)]
upgrades = [0, 0, 0, 0]
upgradeCounter = 0
upgradeTimeCounter = 0
strategies = ["sniper", "penta"]
strategy = "sniper"

mym = MouseController()
myk = KeyboardController()
playerTankColor = (0, 178, 225)
enemyTankColor = (241, 78, 84) #    After death color:  (145, 47, 50)
enemyOutlineColor = (195, 46, 50)
squareColor = (255, 232, 105)
squareOutlineColor = (193, 178, 94)
triangleColor = (252, 118, 119)
triangleOutlineColor = (189, 88, 89)
gunColor = (153, 153, 153)
pentagonColor = (118, 141, 252)
pentagonOutlineColor = (88, 105, 189)
wallColors = [(184 - i, 184 - i, 184 - i) for i in range(10)]
healthBarColor = (133, 227, 135)
mapColor = (205, 205, 205)
mapCounter = 0
upgradeColors = []#[(146, 248, 244), (148, 250, 246), (196, 250, 168), (182, 250, 148), (250, 168, 168), (250, 236, 168)]
for i in range(8):
    upgradeColors.append((144 + i, 246 + i, 242 + i))
    upgradeColors.append((178 + i, 246 + i, 144 + i))
    upgradeColors.append((248 + i, 146 + i, 146 + i))
    upgradeColors.append((248 + i, 230 + i, 146 + i))

#  Colors for items behind the scoreboard
squareAlt = (76, 69, 31)
triangleAlt = (75, 35, 35)
pentagonAlt = (35, 42, 75)

pixsize = screen[0] / 96  #  how many pixels are skipped between pixel checks
monitor = {"top": 0, "left": 0, "width": screen[0], "height": screen[1]}

def checktank():
    global image, enemies, relx, rely, bestenemychoice, xpos, ypos, bestbulletchoice
    color = image.getpixel((relx, rely))
    change = 0
    origwidth = 0
    midx = 0
    midy = 0
    while image.getpixel((relx - change, rely)) == color:
        change += 1
        if relx - change < 0:
            break
    midx = change
    origwidth = change
    change = 0
    while image.getpixel((relx + change, rely)) == color:
        change += 1
        if relx + change > screen[0]:
            break
    midx = relx + (change - midx) / 2
    origwidth += change
    change = 0
    while image.getpixel((midx, rely - change)) == color:
        change += 1
        if rely - change < 0:
            break
    midy = change
    change = 0
    while image.getpixel((midx, rely + change)) == color:
        change += 1
        if rely + change > screen[1]:
            break
    height = change + midy
    midy = rely + (change - midy) / 2
    if color == playerTankColor:
        xpos = midx
        ypos = midy
        return
    print("Height: ", height)
    isplayer = False
    isdrone = False
    if height > screen[0] / 60:
        isplayer = True
        mym.position = (midx, midy)
        enemies.append([midx, midy, height])
        print("Player!")
        print(bestenemychoice)
        if bestenemychoice == None:
            bestenemychoice = [midx, midy, height]
        elif math.sqrt((bestenemychoice[0] - xpos) ** 2 + (bestenemychoice[1] - ypos) ** 2) > math.sqrt((midx - xpos) ** 2 + (midy - ypos) ** 2):
            bestenemychoice = [midx, midy, height]
    else:
        bullets.append([midx, midy, height])
        if bestbulletchoice == None:
            bestbulletchoice = [midx, midy, height]
        elif math.sqrt((bestbulletchoice[0] - xpos) ** 2 + (bestbulletchoice[1] - ypos) ** 2) > math.sqrt((midx - xpos) ** 2 + (midy - ypos) ** 2):
            bestbulletchoice = [midx, midy, height]
    if isplayer == False and origwidth > height + screen[0] / 239:
        print("A drone! ", origwidth, ", ", height)
        isdrone = True
    return (midx, midy, height, isplayer, isdrone)

def blockIdentifier(color):
    global image, blocks, relx, rely, bestblockchoice, empties, xpos, ypos, direction, walls, upgrades, wallColors, wallDetectPositions, upgradeColors
    if color == (109, 109, 109) or color == (94, 94, 94) or color == (37, 37, 37) or color == (123, 123, 123):
        empties += 1
    shouldReturn = False
    for i in range(len(upgradeColors)):
        if color == upgradeColors[i]:
            mynum = (math.floor((i + 8) / 8) - 1)
            if upgrades[mynum] == 0:
                print("Upgrade achieved")
                print("My index: ", i)
                upgrades[mynum] = (relx, rely)
                print(upgrades)
            else:
                upgrades.append(relx, rely)
            shouldReturn = True
    if shouldReturn:
        return
    iswall = False
    for i in range(len(wallColors)):
        if color == wallColors[i]:
            iswall = True
    if iswall:
        return
        if abs(relx - xpos) > screen[0] / 16 and abs(rely - ypos) > screen[1] / 16:
            shouldReturn = False
            for i in range(len(wallDetectPositions)):
                if abs(wallDetectPositions[i][0] - relx) < screen[0] / 8 and abs(wallDetectPositions[i][1] - rely) < screen[1] / 8:
                    return
            myc = wallColors[0]
            modifier = 0
            xchange = 0
            ychange = 0
            while iswall:
                modifier -= 1
                myc = image.getpixel((relx + modifier, rely))
                iswall = False
                for i in range(len(wallColors)):
                    if myc == wallColors[i]:
                        iswall = True
            xchange = -1 * modifier
            modifier = 0
            iswall = True
            while iswall:
                modifier += 1
                myc = image.getpixel((relx + modifier, rely))
                iswall = False
                for i in range(len(wallColors)):
                    if myc == wallColors[i]:
                        iswall = True
            xchange += modifier
            modifier = 0
            myc = wallColors[0]
            iswall = True
            while iswall:
                modifier -= 1
                myc = image.getpixel((relx, rely + modifier))
                iswall = False
                for i in range(len(wallColors)):
                    if myc == wallColors[i]:
                        iswall = True
            ychange = -1 * modifier
            modifier = 0
            iswall = True
            while iswall:
                modifier += 1
                myc = image.getpixel((relx, rely + modifier))
                iswall = False
                for i in range(len(wallColors)):
                    if myc == wallColors[i]:
                        iswall = True
            ychange += modifier
            if xchange < screen[0] / 16 or ychange < screen[1] / 16:
                return
            if ychange > xchange:
                if relx > xpos:
                    walls[0] = 0
                elif relx < xpos:
                    walls[0] = 2
            else:
                if rely > ypos:
                    walls[1] = 0
                elif rely < ypos:
                    walls[1] = 2
            wallDetectPositions.append((relx, rely))
            return
    if color == squareColor or color == squareAlt or color == triangleColor or color == triangleAlt or color == pentagonColor or color == pentagonAlt:
        blockValue = None
        if color == squareColor or color == squareAlt:
            blockValue = 1
        if color == triangleColor or color == triangleAlt:
            blockValue = 3
        if color == pentagonColor or color == pentagonAlt:
            blockValue = 6
        if blockValue == None:
            print("Error detecting block")
            return
        change = 1
        midy = 0
        while image.getpixel((relx - change, rely)) == color:
            change += 1
            if relx - change < 0:
                break
        midx = change
        origwidth = change
        change = 1
        while image.getpixel((relx + change, rely)) == color:
            change += 1
            if relx + change > screen[0]:
                break
        midx = relx + (change - midx) / 2
        origwidth += change
        change = 1
        while image.getpixel((midx, rely - change)) == color:
            change += 1
            if rely - change < 0:
                break
        midy = change
        change = 1
        while image.getpixel((midx, rely + change)) == color:
            change += 1
            if rely + change > screen[1]:
                break
        height = change + midy
        midy = rely + (change - midy) / 2
        shouldadd = True
        for i in range(len(blocks)):
            if math.sqrt((blocks[i][0] - midx) ** 2 + (blocks[i][1] - midy) ** 2) < 1.5 * pixsize:
                shouldadd = False
        if shouldadd:
            blocks.append([midx, midy, blockValue])
            if bestblockchoice == None:
                bestblockchoice = [midx, midy, blockValue]
            elif math.sqrt((bestblockchoice[0] - xpos) ** 2 + (bestblockchoice[1] - ypos) ** 2) / bestblockchoice[2] > math.sqrt((midx - xpos) ** 2 + (midy - ypos) ** 2) / blockValue:
                bestblockchoice = [midx, midy, blockValue]
        return (midx, midy, blockValue)

def keytype(key):
    myk.press(key)
    sleep(0.03)
    myk.release(key)
    sleep(0.03)

def determinewhattodo():
    global enemies, blocks, direction, mouse, bestblockchoice, bestenemychoice, walls, upgrades, upgradeCounter, upgradeTimeCounter, strategy
    horizkeys = ["a", " ", "d"]
    vertkeys = ["w", " ", "s"]
    if upgrades[0] != 0 or upgrades[1] != 0 or upgrades[2] != 0 or upgrades[3] != 0:
        upgradeTimeCounter += 1
        topleft = [screen[0], screen[1]]
        topright = [0, screen[1]]
        bottomleft = [screen[0], 0]
        bottomright = [0, 0]
        for i in range(len(upgrades)):
            if upgrades[i] != 0:
                myup = upgrades[i]
                if myup[0] < topleft[0]:
                    topleft[0] = myup[0]
                if myup[1] < topleft[1]:
                    topleft[1] = myup[1]
                if myup[0] > topright[0]:
                    topright[0] = myup[0]
                if myup[1] < topright[1]:
                    topright[1] = myup[1]
                if myup[0] < bottomleft[0]:
                    bottomleft[0] = myup[0]
                if myup[1] > bottomleft[1]:
                    bottomleft[1] = myup[1]
                if myup[0] > bottomright[0]:
                    bottomright[0] = myup[0]
                if myup[1] > bottomright[1]:
                    bottomright[1] = myup[1]
        if upgradeCounter == 0 or True and upgradeTimeCounter > 30:
            if strategy == "penta":
                mym.position = topleft
            elif strategy == "sniper":
                mym.position = topright
            print("Strat: ", strategy)
            print("Top right: ", topright)
            print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
            mym.press(Button.left)
            sleep(0.025)
            mym.release(Button.left)
            sleep(0.025)
            upgrades = [0, 0, 0, 0]
            upgradeTimeCounter = 0
            upgradeCounter += 1
        else:
            pass
    if bestenemychoice == None and bestbulletchoice == None:
        if bestblockchoice != None:
            mym.position = (bestblockchoice[0], bestblockchoice[1])
            releasemovement()
            if abs(bestblockchoice[0] - xpos) > screen[0] / 3:
                if bestblockchoice[0] > xpos:
                    myk.press("d")
                else:
                    myk.press("a")
            if abs(bestblockchoice[1] - ypos) > screen[1] / 3:
                if bestblockchoice[1] > ypos:
                    myk.press("s")
                else:
                    myk.press("w")
            myk.press(Key.space)
        else:
            releaseall()
            if direction[0] != 1:
                myk.press(horizkeys[direction[0]])
            if direction[1] != 1:
                myk.press(vertkeys[direction[1]])
    else:
        epos = (screen[0] / 2, screen[1] / 2)
        if bestenemychoice != None:
            epos = (bestenemychoice[0], bestenemychoice[1])
        else:
            epos = (bestbulletchoice[0], bestbulletchoice[1])
        mym.position = epos
        releaseall()
        myk.press(Key.space)
        #if abs(epos[0] - xpos) > abs(epos[1] - ypos):
        #    if epos[0] > xpos:
        #        myk.press("a")
        #    else:
        #        myk.press("d")
        #else:
        #    if epos[1] > ypos:
        #        myk.press("w")
        #    else:
        #        myk.press("s")
        if epos[0] > xpos:
            myk.press("a")
        else:
            myk.press("d")
        if epos[1] > ypos:
            myk.press("w")
        else:
            myk.press("s")
    for x in range(screen[0]):
        try:
            wallpix = image.getpixel((xpos - screen[0] / 2 + x, ypos))
            for i in range(len(wallColors)):
                if wallpix == wallColors[i]:
                    if abs(walls[0]) < x - screen[0] / 2:
                        walls[0] = x - screen[0] / 2
        except:
            pass
    for y in range(screen[1]):
        try:
            wallpix = image.getpixel((xpos, ypos - screen[1] / 2 + y))
            for i in range(len(wallColors)):
                if wallpix == wallColors[i]:
                    if abs(walls[1]) < y - screen[1] / 2:
                        walls[1] = y - screen[1] / 2
        except:
            pass
    if walls[0] != 0 or walls[1] != 0:
        print("Wall movement")
        if walls[0] != 0:
            if walls[0] > 0:
                myk.press("a")
                print("Wall right")
            else:
                myk.press("d")
                print("Wall left")
        if walls[1] != 0:
            if walls[1] > 0:
                myk.press("w")
                print("Wall bottom")
            else:
                myk.press("s")
                print("Wall top")

def testImage():
    global image, mym
    print(image.getpixel(mym.position))
    print(mym.position)
    myclick = mousevent()
    try:
        if myclick.button == Button.left and myclick.x < 1000 and myclick.y < 1000:
            #image.show()
            #image.save()
            #image.close()
            pass
    except:
        pass

def releaseall():
    horizkeys = ["a", "d"]
    vertkeys = ["w", "s"]
    myk.release(horizkeys[0])
    myk.release(horizkeys[1])
    myk.release(vertkeys[0])
    myk.release(vertkeys[1])
    myk.release(Key.space)

def releasemovement():
    horizkeys = ["a", "d"]
    vertkeys = ["w", "s"]
    myk.release(horizkeys[0])
    myk.release(horizkeys[1])
    myk.release(vertkeys[0])
    myk.release(vertkeys[1])

def setupupgrades():
    myk.press("u")
    keytype("6")
    keytype("5")
    keytype("4")
    keytype("4")
    keytype("4")
    keytype("8")
    keytype("8")
    keytype("7")
    keytype("7")
    for i in range(4):
        keytype("6")
        keytype("5")
    for i in range(3):
        keytype("7")
        keytype("8")
    keytype("8")
    keytype("8")
    keytype("4")
    keytype("4")
    for i in range(2):
        keytype("6")
        keytype("5")
        keytype("4")
    myk.release("u")

print("starting")
sleep(5)
start = time.time()
fps = 0
othertimer = time.time()

setupupgrades()

while True:
    if time.time() - othertimer >= 1:
        print("FPS: ", fps)
        fps = 0
        othertimer = time.time()
    fps += 1
    image = ImageGrab.grab()
    print("Test pixel: ", image.getpixel((128, 253)))
    #sct_img = mss.mss().grab(monitor)
    #image = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    #print(image.getpixel(mym.position))
    enemies = []
    blocks = []
    bestblockchoice = None
    bestenemychoice = None
    bestbulletchoice = None
    empties = 0
    mapCounter = 0
    walls = [0, 0]
    wallDetectPositions = [(0, 0)]
    for x in range(floor(screen[0] / pixsize)):
        relx = floor(x * pixsize)
        for y in range(floor(screen[1] / pixsize)):
            rely = floor(y * pixsize)
            color = image.getpixel((relx, rely))
            if color == mapColor:
                mapCounter += 1
                continue
            try:
                if color == enemyTankColor or color == playerTankColor:
                    checktank()
                else:
                    blockIdentifier(color)
            except:
                pass
    endgame = False
    if empties > screen[0] / 96:# or mapCounter < (screen[0] * screen[1] / 128 / pixsize):
        print("Screen: ", screen[0] * screen[1] / 128 / pixsize)
        print("Map counter: ", mapCounter)
        releaseall()
        endgame = True
    while empties > 20:
        print("empty")
        print(empties)
        releaseall()
        image = ImageGrab.grab()
        #sct_img = mss.mss().grab(monitor)
        #image = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        empties = 0
        for x in range(floor(screen[0] / pixsize)):
            relx = x * pixsize
            for y in range(floor(screen[1] / pixsize)):
                rely = y * pixsize
                color = image.getpixel((relx, rely))
                try:
                    blockIdentifier(color)
                except:
                    pass
    if endgame:
        setupupgrades()
    determinewhattodo()
    #testImage()
    if time.time() - start > 10:
        start = time.time()
        direction = [randint(0, 2), randint(0, 2)]
        if direction[0] == 1 and direction[1] == 1:
            direction[randint(0, 1)] = randint(-1, 0) * 2 + 2
        horizkeys = ["a", "d"]
        vertkeys = ["w", "s"]
        myk.release(horizkeys[0])
        myk.release(horizkeys[1])
        myk.release(vertkeys[0])
        myk.release(vertkeys[1])



















