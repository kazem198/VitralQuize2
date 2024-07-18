import cv2
import csv
import cvzone
import time
import numpy as np
from cvzone.HandTrackingModule import HandDetector


quistions = []
posQuitons = [(200, 250), (200, 375), (800, 375), (200, 500), (800, 500)]
latacyTime = 0
nextOK = True
x, y = 0, 0

#
detector = HandDetector(staticMode=False, maxHands=2,
                        modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)
with open('./quistions.csv', 'r') as file:
    quistion = csv.reader(file)

    for i, row in enumerate(quistion):
        if i > 0:
            quistions.append(row)


correctAns = np.zeros(len(quistions), dtype=int)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1024)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)

currentQuistion = 0
currentTime = time.time()
timeAnswer = 10


class Buttons:
    def __init__(self, positon, quistion):
        self.positon = positon
        self.quistion = quistion

    def drawBtn(self, img, choise=0, color=(255, 0, 255), complite=False):

        for i, pos in enumerate(self.positon):

            if i == choise and choise != 0:
                color = (0, 0, 0)

                if complite:
                    color = (0, 255, 0)
            else:
                color = (255, 0, 255)

            img, bbox = cvzone.putTextRect(
                # Image and starting position of the rectangle
                img, str(self.quistion[i]), pos,
                scale=3, thickness=3,  # Font scale and thickness
                # Text color and Rectangle color
                colorT=(255, 255, 255), colorR=color,
                font=cv2.FONT_HERSHEY_PLAIN,  # Font type
                offset=20,  # Offset of text inside the rectangle
                border=5, colorB=(0, 255, 0)  # Border thickness and color
            )

    def posAns(self):
        indesAns = self.quistion[-1]
        return self.positon[int(indesAns)+1]

    def findPosition(self, img, points, currentQuistion, timeLeft, nextOK, currentTime):

        for i, pos in enumerate(self.positon):
            if i > 0:
                if pos[0] < points[0] < pos[0]+250 and pos[1] < points[1] < pos[1]+100:
                    self.drawBtn(img, i)
                    if (timeLeft < 5):
                        cv2.ellipse(img, (pos[0]-50, pos[1]),
                                    (25, 25), 0, 0, timeLeft*90, (255, 0, 0), 3)
                    else:

                        self.drawBtn(img, i, complite=True)
                        if nextOK:
                            if currentQuistion < len(self.quistion):
                                Ans = self.quistion[-1]
                                if int(Ans) == i-1:
                                    print(currentQuistion, 'currentQuistion')

                                    correctAns[currentQuistion] = 1
                                currentQuistion += 1
                                nextOK = False
                                currentTime = time.time()

                    # print(len(self.positon), "len(self.positon)")

                    # if int(Ans) == i-1:
                    #     try:
                    #         correctAns[currentQuistion] = 1
                    #     except:
                    #         pass
                    # print(correctAns)
                if timeAnswer-timeLeft == timeAnswer:
                    nextOK = True

        return currentQuistion, nextOK, currentTime


allquistions = []
for quistion in quistions:
    allquistions.append(Buttons(posQuitons, quistion))


while True:
    _, img = cap.read()
    img = cv2.flip(img, 1)

    hands, img = detector.findHands(img, draw=False, flipType=True)

    if currentQuistion < len(quistions):
        allquistions[currentQuistion].drawBtn(img)
        # posAns = allquistions[currentQuistion].posAns()
        timeLeft = int(time.time()-currentTime)
        if hands:

            hand1 = hands[0]

            lmList1 = hand1["lmList"]

            # length, info, img = detector.findDistance(lmList1[8][0:2], lmList1[12][0:2], img, color=(255, 0, 255),
            #   scale=10)
            # if length < 50:
            x, y = lmList1[8][0:2]
            # print(x, y)

            currentQuistion, nextOK, currentTime = allquistions[currentQuistion].findPosition(
                img, (x, y), currentQuistion, timeLeft, nextOK, currentTime
            )

        # print(currentQuistion)

        cv2.putText(img, str(timeAnswer-timeLeft), (1200, 700),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

        if (time.time()-currentTime > timeAnswer):
            if latacyTime == 0:

                latacyTime += 1

            if latacyTime > 0:
                latacyTime += 1
            if latacyTime > 15:

                currentQuistion += 1
                currentTime = time.time()
                latacyTime = 0
        # nextOK = True
    else:
        # print(posAns)
        cv2.putText(img, "game over", (500, 500),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
        result = 1-(len(correctAns)-sum(correctAns))/len(correctAns)
        cv2.putText(img, f'your score is :{result}', (500, 600),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

    cv2.imshow("img", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        cv2.destroyAllWindows()
        break
