import cv2
import numpy as np

while 1:
    original = cv2.imread('img.jpg')
    hsv = cv2.cvtColor(original, cv2.COLOR_BGR2HSV)
    hue = cv2.inRange(original, np.array([0, 90, 215]), np.array([179, 255, 255]))
    # hue, s, _ = cv2.split(hsv)

    _, dst = cv2.threshold(hue, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    fg = cv2.erode(dst, None, iterations=3)
    bg = cv2.dilate(dst, None, iterations=1)
    _, bg = cv2.threshold(bg, 1, 128, 1)
    mark = cv2.add(fg, bg)
    mark32 = np.int32(mark)
    cv2.watershed(original, mark32)
    original[mark32 == -1] = [255, 0, 0]
    cv2.imshow('ws', original)

    # m = cv2.convertScaleAbs(mark32)
    # , m = cv2.threshold(m, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # cntr, h = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # ???
    # print(len(cntr))
    # print cntr[0].shape
    # cntr[1].dtype=np.float32
    # ret=cv2.contourArea(np.array(cntr[1]))
    # print ret
    # cntr[0].dtype=np.uint8

    # cv2.drawContours(original, cntr, -1, (255, 255, 255), 3)
    # cv2.imshow("mask_fg", fg)
    # cv2.imshow("mask_bg", bg)
    # cv2.imshow("mark", m)
    # cv2.imshow("original", original)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

