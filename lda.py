import numpy as np
import cv2
from audioplayer import AudioPlayer
from PyQt5.QtWidgets import QMessageBox

# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

cv2.startWindowThread()

# open webcam video stream
# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("GuvenlikKamerasi.mp4")

# the output will be written to output.avi
out = cv2.VideoWriter(
    'output.avi',
    cv2.VideoWriter_fourcc(*'MJPG'),
    15.,
    (640, 480))

while (True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # resizing for faster detection
    frame = cv2.resize(frame, (640, 480))
    # using a greyscale picture, also for faster detection
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # detect people in the image
    # returns the bounding boxes for the detected objects
    boxes, weights = hog.detectMultiScale(frame, winStride=(8, 8))
    # output human count
    # print(len(boxes))

    """
    if len(boxes) >= 3:
        print("Çıkın Çıkın Gidin")
        AudioPlayer("myfile.mp3").play(block=True)
    """

    boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])
    kirmizicounter = 0
    mavicounter = 0
    control = 5

    kirmizibas = (0, 0)
    kirmizison = (640, 240)

    mavibas = (0, 240)
    mavison = (641, 480)

    for (xA, yA, xB, yB) in boxes:
        # display the detected boxes in the colour picture
        cv2.rectangle(frame, (xA, yA), (xB, yB),
                      (0, 255, 0), 2)

        # Alanların bulundukları yerler.

        cv2.rectangle(frame, (0, 0), (640, 240), (0, 0, 255), 3)
        cv2.rectangle(frame, (0, 240), (640, 480), (255, 0, 0), 3)

        if xA >= 0 and yA >= 0 and xB <= 640 and yB <= 240:
            kirmizicounter += 1
            print(kirmizicounter)
        else:
            kirmizicounter -= 1
            print(kirmizicounter)

        if (xA, yA) >= mavibas and (xB, yB) <= mavison:
            mavicounter += 1
            print("mavi" + str(mavicounter))
        if (xA, yA) >= kirmizibas and (xB, yB) <= kirmizison:
            kirmizicounter += 1
            print("kirmizi" + str(kirmizicounter))

        if kirmizicounter == 0 and mavicounter == 1:
            if mavicounter == 0 and kirmizicounter == 1:
                counter -= 1
                print(counter)
        elif kirmizicounter == 1 and mavicounter == 0:
            if kirmizicounter == 0 and mavicounter == 1:
                counter += 1
                print(counter)

        """
                mavicountertemp = mavicounter
        kirmizicountertemp = kirmizicounter        
        if(xA,yA)>=mavibas and (xB,yB)<=mavison:
            mavicounter += 1
            print("mavi bolge: "+str(mavicounter))
        elif (xA,yA)>= kirmizibas and (xB,yB)<=kirmizison:
            kirmizicounter += 1
            print("kirmizi bolge: "+str(kirmizicounter))

        if kirmizicounter==kirmizicountertemp and mavicounter==mavicountertemp+1:
            if mavicounter==mavicountertemp and kirmizicounter==kirmizicountertemp+1:
                counter-=1
                print("icerdeki kisi sayisi: "+str(counter))
        elif kirmizicounter==kirmizicountertemp+1 and mavicounter==mavicountertemp:
            if kirmizicounter==kirmizicountertemp and mavicounter==mavicountertemp+1:
                counter +=1
                print("icerdeki kisi sayisi: "+str(counter))

        """

        # returns the bounding boxes for the detected objects

    # Write the output video
    out.write(frame.astype('uint8'))
    # Display the resulting frame
    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
# and release the output
out.release()
# finally, close the window
cv2.destroyAllWindows()
cv2.waitKey(1)