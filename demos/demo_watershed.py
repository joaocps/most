import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

# TODO gui com sliders lower e higher

while 1:
    # img = cv.imread('img.jpg')
    # original = cv.imread('img.jpg')
    img = cv.imread('frame0.0.png')
    original = cv.imread('frame0.0.png')
    img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    aux = cv.inRange(img, np.array([0, 50, 215]), np.array([127, 255, 255]))

    # morph error workaround (obsolete (?))
    img = cv.bitwise_and(img, img, mask=aux)
    cv.imwrite('lim.jpg', img)
    img = cv.imread('lim.jpg')
    img = cv.cvtColor(img, cv.COLOR_HSV2BGR)
    # end

    # theshold
    # optional graysacle (?)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
    # thresh = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)

    # noise removal
    kernel = np.ones((3, 3), np.uint8)
    opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=1)

    # sure background area
    # mudar para imagem limitada pela vegetação
    sure_bg = cv.dilate(opening, kernel, iterations=2)

    # Finding sure foreground area
    dist_transform = cv.distanceTransform(opening, cv.DIST_L2, 5)
    _, sure_fg = cv.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)

    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv.subtract(sure_bg, sure_fg)

    # Marker labelling
    ret, markers = cv.connectedComponents(sure_fg)

    # Add one to all labels so that sure background is not 0, but 1
    markers = markers + 1

    # Now, mark the region of unknown with zero
    markers[unknown == 255] = 0

    # watershed segmentation
    markers = cv.watershed(original, markers)
    original[markers == -1] = [255, 0, 0]
    # print()

    # output markers debug
    plt.subplot(111), plt.imshow(markers)

    # convert to contour test
    # markers = original[markers == np.minimum(markers, -1)]

    m = cv.convertScaleAbs(markers)
    _, m = cv.threshold(m, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    cntr, h = cv.findContours(m, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cv.drawContours(original, cntr, -1, (255, 255, 255), 3)

    cv.imshow('ws', original)
    # cv.imshow('bg', sure_bg)
    # cv.imshow('fg', sure_fg)

    k = cv.waitKey(5) & 0xFF
    if k == 27:
        break

# results
# img_final = cv.addWeighted(original, 0.3, img, 0.7, 0)
# cv.imwrite('dt.jpg', dist_transform)
# cv.imwrite('sure_bg.jpg', sure_bg)
# cv.imwrite('sure_fg.jpg', sure_fg)
# cv.imwrite('final.jpg', img_final)
# min_val, max_val, min_loc, max_loc = cv.minMaxLoc(gray, mask=m)

plt.show()
