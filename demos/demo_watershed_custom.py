import cv2
import numpy as np
import sys


# from matplotlib import pyplot as plt
class ws:
    def __init__(self):
        self.og = ""
        self.filename = ""
        self.cntr = ""

        self.it_fg = 0
        self.it_bg = 0
        self.it_bg_2 = 0

        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.createTrackbar('ARDIDA', 'image', 0, 20, self.on_change)
        cv2.createTrackbar('RESTO', 'image', 0, 20, self.on_change)

    # Carrega imagens
    def watershed(self, original, it_fg=0, it_bg=0):
        hsv = cv2.cvtColor(original, cv2.COLOR_BGR2HSV)

        lower_limit_fogo = np.array([0, 90, 90])
        upper_limit_fogo = np.array([40, 255, 255])

        aux = cv2.inRange(hsv, lower_limit_fogo, upper_limit_fogo)
        fg_fogo = cv2.bitwise_and(original, original, mask=aux)

        lower_limit_ard1 = np.array([0, 0, 0])
        upper_limit_ard1 = np.array([179, 150, 110])

        aux = cv2.inRange(hsv, lower_limit_ard1, upper_limit_ard1)
        fg_ard1 = cv2.bitwise_and(original, original, mask=aux)

        lower_limit_ard2 = np.array([0, 0, 0])
        upper_limit_ard2 = np.array([179, 255, 100])

        aux = cv2.inRange(hsv, lower_limit_ard2, upper_limit_ard2)
        fg_ard2 = cv2.bitwise_and(original, original, mask=aux)

        lower_limit_other = np.array([0, 0, 110])
        upper_limit_other = np.array([179, 65, 255])

        aux = cv2.inRange(hsv, lower_limit_other, upper_limit_other)
        bg_other = cv2.bitwise_and(original, original, mask=aux)

        lower_limit_other2 = np.array([0, 0, 125])
        upper_limit_other2 = np.array([179, 40, 170])

        aux = cv2.inRange(hsv, lower_limit_other2, upper_limit_other2)
        bg_other2 = cv2.bitwise_and(original, original, mask=aux)

        lower_limit_other3 = np.array([15, 30, 0])
        upper_limit_other3 = np.array([65, 255, 255])

        aux = cv2.inRange(hsv, lower_limit_other3, upper_limit_other3)
        bg_other3 = cv2.bitwise_and(original, original, mask=aux)

        fg = cv2.add(fg_fogo, fg_ard1)
        fg = cv2.add(fg, fg_ard2)

        bg = cv2.add(bg_other, bg_other2)
        bg = cv2.add(bg, bg_other3)

        # passa para gray
        fg_gray = cv2.cvtColor(fg, cv2.COLOR_BGR2GRAY)
        bg_gray = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)

        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * it_fg + 1, 2 * it_fg + 1),
                                            (it_fg, it_fg))
        sure_fg = cv2.morphologyEx(fg_gray, cv2.MORPH_OPEN, element)

        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * it_bg + 1, 2 * it_bg + 1),
                                            (it_bg, it_bg))
        sure_bg = cv2.morphologyEx(bg_gray, cv2.MORPH_CLOSE, element)

        # tirar ruido area de interesse
        sure_fg = cv2.erode(sure_fg, None, iterations=it_fg)
        # sure_fg = cv2.dilate(sure_fg, None, iterations=it_fg)

        # tirar ruido outros
        sure_bg = cv2.erode(sure_bg, None, iterations=it_bg)
        # sure_bg = cv2.erode(sure_bg, None, iterations=it_bg_2)
        #  sure_bg = cv2.dilate(sure_bg, None, iterations=it_bg)

        # simplificar
        dist_transform = cv2.distanceTransform(sure_fg, cv2.DIST_L2, 5)
        # _, thresh_fg = cv2.threshold(fg_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, thresh_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
        _, thresh_bg = cv2.threshold(sure_bg, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        # retirar areas comuns que nao interresam
        thresh_fg = np.uint8(thresh_fg)
        mark = cv2.subtract(thresh_bg, thresh_fg)

        # encontrar area ligadas
        # _, markers = cv2.connectedComponents(thresh_fg)
        #
        # # simplificar markers
        # markers = markers + 1
        # markers[mark == 255] = 0
        mark32 = np.int32(mark)

        # watershed
        markers = cv2.watershed(original, mark32)

        # watershed result debug
        # plt.subplot(111), plt.imshow(markers)

        # desenhar segmentaçao
        original[markers == -1] = [255, 0, 0]

        # encontrar contornos
        # m = cv2.convertScaleAbs(markers)
        # _, m = cv2.threshold(m, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # cntr, h = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cntr2, h = cv2.findContours(markers, cv2.RETR_FLOODFILL, cv2.CHAIN_APPROX_SIMPLE)

        # print(cntr)
        # simplificar contornos
        # hull = []
        # for i in range(len(cntr)):
        #     hull.append(cv2.convexHull(cntr[i], False))
        #
        # appr = []
        # for i in range(len(cntr)):
        #     epsilon = 0.01 * cv2.arcLength(cntr[i], True)
        #     appr.append(cv2.approxPolyDP(cntr[i], epsilon, True))
        #
        # appr2 = []
        # for i in range(len(cntr)):
        #     epsilon = 0.01 * cv2.arcLength(cntr[i], True)
        #     ap = (cv2.approxPolyDP(cntr[i], epsilon, True))
        #     appr2.append(cv2.convexHull(ap))

        # cv2.drawContours(original, hull, -1, (0, 255, 0), 2, cv2.LINE_AA)
        # cv2.drawContours(original, appr, -1, (0, 0, 255), 2, cv2.LINE_AA)
        # cv2.drawContours(original, appr2, -1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.drawContours(original, cntr, -1, (255, 255, 0), 2, cv2.LINE_AA)
        # cv2.drawContours(original, cntr2, -1, (255, 255, 0), 2, cv2.LINE_AA)

        return original, cntr

    def on_change(self, x):
        frame = cv2.imread(self.filename)
        self.it_fg = cv2.getTrackbarPos('ARDIDA', 'image')
        self.it_bg = cv2.getTrackbarPos('RESTO', 'image')

        self.og, self.cntr = self.watershed(frame, self.it_fg, self.it_bg)

    def main(self, filename):
        frame = cv2.imread(filename)
        self.filename = filename
        self.og = frame
        while 1:
            cv2.imshow('image', self.og)

            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                cv2.destroyAllWindows()
                return self.og, self.cntr
        # break


ws = ws()
ws.main(sys.argv[1])
# ws.main("frame0.0.png")
# ws.main("img.jpg")
# c = 0
# with open('c.txt', 'w') as f:
#     for item in hull:
#         f.write("[")
#         for i in item:
#             for x in i:
#                 f.write(str(x))
#             f.write(",")
#         f.write("]\n")
# np.save("c3", hull)
# l = np.load("c3", allow_pickle=True)
#
# for item in l:
#     for i in item:
#         for x in i:
#             print(x[0], x[1])
#     print("\n")
# break

# plt.show()
