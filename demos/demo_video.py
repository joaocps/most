import numpy as np
import cv2

cap = cv2.VideoCapture('new_vid2.mp4')

count = 0

while cap.isOpened():
    ret, frame = cap.read()

    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # cv2.imshow('frame', frame)
    if count % 240 == 0:
        cv2.imwrite("frame" + str(count / 240) + ".png", frame)
    count += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
