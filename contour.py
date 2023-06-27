import numpy as np
import cv2
import person
import time
import pymongo
from pymongo import MongoClient
import datetime
import imutils

cnt_up = 0
cnt_down = 0

# cap = cv2.VideoCapture(0)
srcMain = 'rtsp://192.168.43.1:8080/h264_pcm.sdp'
cap = cv2.VideoCapture("D:\Downloads\Videos\London Walk from Oxford Street to Carnaby Street.mp4")
# cap = cv2.VideoCapture('rtsp://192.168.43.1:8080/h264_pcm.sdp')
client = MongoClient('localhost', 3001)
db = client.people
collection = db.count
for i in range(19):
    print
    i, cap.get(i)

w = cap.get(3)
h = cap.get(4)
frameArea = h * w
areaTH = frameArea / 50

line_up = int(2 * (h / 5))
line_down = int(3 * (h / 5))

up_limit = int(1 * (h / 5))
down_limit = int(4 * (h / 5))

line_down_color = (0, 0, 0)
line_up_color = (0, 0, 0)
pt1 = [0, line_down];
pt2 = [w, line_down];
pts_L1 = np.array([pt1, pt2], np.int32)
pts_L1 = pts_L1.reshape((-1, 1, 2))
pt3 = [0, line_up];
pt4 = [w, line_up];
pts_L2 = np.array([pt3, pt4], np.int32)
pts_L2 = pts_L2.reshape((-1, 1, 2))

pt5 = [0, up_limit];
pt6 = [w, up_limit];
pts_L3 = np.array([pt5, pt6], np.int32)
pts_L3 = pts_L3.reshape((-1, 1, 2))
pt7 = [0, down_limit];
pt8 = [w, down_limit];
pts_L4 = np.array([pt7, pt8], np.int32)
pts_L4 = pts_L4.reshape((-1, 1, 2))

fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=False)

kernelOp = np.ones((3, 3), np.uint8)
kernelOp2 = np.ones((5, 5), np.uint8)
kernelCl = np.ones((11, 11), np.uint8)

font = cv2.FONT_HERSHEY_SIMPLEX
persons = []
max_p_age = 5
pid = 1

while (cap.isOpened()):

    ret, frame = cap.read()
    for i in persons:
        i.age_one()
    fgmask = fgbg.apply(frame)
    fgmask2 = fgbg.apply(frame)

    try:
        ret, imBin = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
        ret, imBin2 = cv2.threshold(fgmask2, 200, 255, cv2.THRESH_BINARY)

        mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernelOp)
        mask2 = cv2.morphologyEx(imBin2, cv2.MORPH_OPEN, kernelOp)

        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernelCl)
        mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernelCl)
    except:
        print('EOF')
        print
        'UP:', cnt_up
        print
        'DOWN:', cnt_down
        break
    _, contours0, hierarchy = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours0:
        area = cv2.contourArea(cnt)
        if area > areaTH:
            M = cv2.moments(cnt)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            x, y, w, h = cv2.boundingRect(cnt)

            new = True
            if cy in range(up_limit, down_limit):
                for i in persons:
                    if abs(cx - i.getX()) <= w and abs(cy - i.getY()) <= h:
                        new = False
                        i.updateCoords(cx, cy)
                        if i.going_UP(line_down, line_up) == True:
                            cnt_up += 1;
                        elif i.going_DOWN(line_down, line_up) == True:
                            cnt_down += 1;
                            break
                        inside = cnt_down - cnt_up
                        # collection.insert_one({'No_of_people':inside,'created_at':datetime.datetime.utcnow()})
                    if i.getState() == '1':
                        if i.getDir() == 'down' and i.getY() > down_limit:
                            i.setDone()
                        elif i.getDir() == 'up' and i.getY() < up_limit:
                            i.setDone()
                    if i.timedOut():
                        index = persons.index(i)
                        persons.pop(index)
                        del i
                if new == True:
                    p = person.MyPerson(pid, cx, cy, max_p_age)
                    persons.append(p)
                    pid += 1

            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            img = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # cv2.drawContours(frame, cnt, -1, (0,255,0), 3)

    str_up = 'Enter: ' + str(cnt_up)
    str_down = 'Exit: ' + str(cnt_down)
    frame = cv2.polylines(frame, [pts_L1], False, line_down_color, thickness=2)
    frame = cv2.polylines(frame, [pts_L2], False, line_up_color, thickness=2)

    cv2.putText(frame, str_up, (250, 40), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, str_down, (250, 70), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    cv2.imshow('Frame1', frame)
    # cv2.imshow('Frame',fgmask)

    # cv2.imshow('Mask',mask)
    k = cv2.waitKey(30) & 0xff
    if k == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()