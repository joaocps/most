import cv2
import sys

import numpy as np


def nothing(x):
    # print("not nothing")
    pass


frame = cv2.imread(sys.argv[1])

cv2.namedWindow('image', cv2.WINDOW_NORMAL)

cv2.createTrackbar('Lower_H', 'image', 0, 179, nothing)
cv2.createTrackbar('Lower_S', 'image', 0, 255, nothing)
cv2.createTrackbar('Lower_V', 'image', 0, 255, nothing)

cv2.createTrackbar('Upper_H', 'image', 0, 179, nothing)
cv2.createTrackbar('Upper_S', 'image', 0, 255, nothing)
cv2.createTrackbar('Upper_V', 'image', 0, 255, nothing)

cv2.createTrackbar('iter', 'image', 0, 10, nothing)

hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# cv2.setTrackbarPos('Lower_H', 'image', 0)
# cv2.setTrackbarPos('Lower_S', 'image', 74)
# cv2.setTrackbarPos('Lower_V', 'image', 217)

cv2.setTrackbarPos('Upper_H', 'image', 179)
cv2.setTrackbarPos('Upper_S', 'image', 255)
cv2.setTrackbarPos('Upper_V', 'image', 255)

img = frame
while 1:
    cv2.imshow('image', img)

    # get current positions of trackbars
    h = cv2.getTrackbarPos('Lower_H', 'image')
    s = cv2.getTrackbarPos('Lower_S', 'image')
    v = cv2.getTrackbarPos('Lower_V', 'image')

    u_h = cv2.getTrackbarPos('Upper_H', 'image')
    u_s = cv2.getTrackbarPos('Upper_S', 'image')
    u_v = cv2.getTrackbarPos('Upper_V', 'image')

    it = cv2.getTrackbarPos('iter', 'image')

    lower_limit = np.array([h, s, v])
    upper_limit = np.array([u_h, u_s, u_v])

    aux = cv2.inRange(hsv, lower_limit, upper_limit)
    aux = cv2.erode(aux, None, iterations=it)
    aux = cv2.dilate(aux, None, iterations=it)
    img2 = cv2.bitwise_and(frame, frame, mask=aux)

    # original mais segmentada
    img = cv2.addWeighted(frame, 0.1, img2, 0.9, 0)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        cv2.destroyWindow('image')
