import cv2
import numpy as np
import sys
from matplotlib import pyplot as plt


class ws:
    def __init__(self):
        self.og = ""
        self.filename = ""
        self.cntr = ""
        # 1 - fogo
        # 2 - ardida 1
        # 3 - ardida 2
        # 4 - ardida 3
        self.lower_fg = [np.array([0, 79, 90]), np.array([0, 0, 0]), np.array([0, 0, 0]), np.array([0, 0, 0])]
        self.upper_fg = [np.array([3, 255, 255]), np.array([0, 40, 70]), np.array([179, 255, 35]),
                         np.array([10, 255, 70])]
        # 1 - fumo branco denso
        # 2 - vegetação "clara"
        # 3 - fumo?
        # 4 - vegetação "escura"
        # 5 - estrada terra
        self.lower_bg = [np.array([0, 0, 220]), np.array([30, 60, 70]), np.array([55, 30, 75]), np.array([35, 0, 0]),
                         np.array([20, 35, 125])]
        self.upper_bg = [np.array([179, 10, 255]), np.array([35, 255, 130]), np.array([95, 255, 255]),
                         np.array([75, 255, 255]), np.array([40, 60, 255])]
        self.fg_array = []
        self.bg_array = []
        self.fg = ""
        self.bg = ""

    def fine_tune_fg(self, lower, upper, hsv, original):
        view = original
        while 1:
            cv2.imshow(self.filename + "Area de interesse", view)
            aux = cv2.inRange(hsv, lower, upper)
            it = cv2.getTrackbarPos('Diminuir Area', self.filename + "Area de interesse")
            # aux = cv2.erode(aux, None, iterations=it)
            # aux = cv2.dilate(aux, None, iterations=it)
            element = cv2.getStructuringElement(cv2.MORPH_RECT, (2 * it + 1, 2 * it + 1),
                                                (it, it))
            aux = cv2.morphologyEx(aux, cv2.MORPH_OPEN, element)
            # aux = cv2.erode(aux, None, iterations=it)
            result = cv2.bitwise_and(original, original, mask=aux)
            view = cv2.addWeighted(original, 0.1, result, 0.9, 0)
            k = cv2.waitKey(5) & 0xFF
            if k == ord("s"):
                cv2.destroyAllWindows()
                self.fg_array.append(result)
                return
            elif k == 27:
                cv2.destroyAllWindows()
                return
            elif k == ord("q"):
                exit(1)
                # break

    def fine_tune_bg(self, lower, upper, hsv, original):
        view = original
        while 1:
            cv2.imshow(self.filename + "Area a omitir", view)
            aux = cv2.inRange(hsv, lower, upper)
            it = cv2.getTrackbarPos('Diminuir Area', self.filename + "Area a omitir")
            it_2 = cv2.getTrackbarPos('Limpar Ruído', self.filename + "Area a omitir")
            # aux = cv2.dilate(aux, None, iterations=it)
            # aux = cv2.erode(aux, None, iterations=it)

            element = cv2.getStructuringElement(cv2.MORPH_RECT, (2 * it + 1, 2 * it + 1),
                                                (it, it))
            aux = cv2.morphologyEx(aux, cv2.MORPH_OPEN, element)

            element = cv2.getStructuringElement(cv2.MORPH_RECT, (2 * it_2 + 1, 2 * it_2 + 1),
                                                (it_2, it_2))
            aux = cv2.morphologyEx(aux, cv2.MORPH_CLOSE, element)
            result = cv2.bitwise_and(original, original, mask=aux)
            view = cv2.addWeighted(original, 0.1, result, 0.9, 0)
            k = cv2.waitKey(5) & 0xFF
            if k == ord("s"):
                cv2.destroyAllWindows()
                self.bg_array.append(result)
                return
            elif k == 27:
                cv2.destroyAllWindows()
                return
            elif k == ord("q"):
                exit(1)

    def create_window(self):
        cv2.namedWindow(self.filename + "Area de interesse", cv2.WINDOW_GUI_EXPANDED)
        cv2.createTrackbar('Diminuir Area', self.filename + "Area de interesse", 0, 20, self.nothing)

    def create_window_bg(self):
        cv2.namedWindow(self.filename + "Area a omitir", cv2.WINDOW_GUI_EXPANDED)
        cv2.createTrackbar('Diminuir Area', self.filename + "Area a omitir", 0, 20, self.nothing)
        cv2.createTrackbar('Limpar Ruído', self.filename + "Area a omitir", 0, 20, self.nothing)

    def create_window_view(self):
        cv2.namedWindow(self.filename, cv2.WINDOW_KEEPRATIO)

    def nothing(self, x):
        pass

    # Carrega imagens
    def watershed(self, original):

        hsv = cv2.cvtColor(original, cv2.COLOR_BGR2HSV)

        for i in range(len(self.lower_fg)):
            self.create_window()
            self.fine_tune_fg(self.lower_fg[i], self.upper_fg[i], hsv, original)

        for i in range(len(self.lower_bg)):
            self.create_window_bg()
            self.fine_tune_bg(self.lower_bg[i], self.upper_bg[i], hsv, original)

        self.fg = self.fg_array[0]
        for j in range(len(self.fg_array)):
            if j > 0:
                self.fg = cv2.add(self.fg, self.fg_array[j])

        self.bg = self.bg_array[0]
        for j in range(len(self.bg_array)):
            if j > 0:
                self.bg = cv2.add(self.bg, self.bg_array[j])

        # passa para gray
        fg_gray = cv2.cvtColor(self.fg, cv2.COLOR_BGR2GRAY)
        bg_gray = cv2.cvtColor(self.bg, cv2.COLOR_BGR2GRAY)

        # simplificar
        # dist_transform = cv2.distanceTransform(fg_gray, cv2.DIST_L2, 5)
        _, thresh_fg = cv2.threshold(fg_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # _, thresh_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
        _, thresh_bg = cv2.threshold(bg_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # thresh_fg = np.uint8(thresh_fg)
        # retirar areas comuns que nao interresam
        mark = cv2.subtract(thresh_bg, thresh_fg)

        # encontrar area ligadas
        # _, markers = cv2.connectedComponents(thresh_fg)

        # simplificar markers
        mark32 = np.int32(cv2.addWeighted(thresh_fg, 1, thresh_bg, 0.5, 0))
        markers = mark32 + 1
        markers[mark == 255] = 0
        # print(markers)

        # watershed result debug
        # plt.subplot(111), plt.imshow(markers)
        # plt.show()

        # watershed
        markers = cv2.watershed(original, markers)

        # desenhar segmentaçao
        # original[markers == -1] = [255, 0, 0]

        # encontrar contornos
        cntr2 = []
        m = cv2.convertScaleAbs(markers)
        # plt.subplot(111), plt.imshow(markers)
        _, m = cv2.threshold(m, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cntr, h = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        cntr2, h2 = cv2.findContours(markers, cv2.RETR_FLOODFILL, cv2.CHAIN_APPROX_SIMPLE)

        # print(cntr)
        # simplificar contornos
        # hull = []
        # for i in range(len(cntr)):
        #     hull.append(cv2.convexHull(cntr[i], False))
        #
        # #
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
        cntr2.pop()
        # for i in range(len(cntr2)):
        #     print(cntr2[i][0])

        # cv2.drawContours(original, hull, -1, (0, 255, 0), 2, cv2.LINE_AA)
        # cv2.drawContours(original, appr, -1, (0, 0, 255), 2, cv2.LINE_AA)
        # cv2.drawContours(original, appr2, -1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.drawContours(original, cntr, -1, (255, 255, 255), 2, cv2.LINE_AA)
        # cv2.drawContours(original, cntr2, -1, (0, 255, 0), 2, cv2.LINE_AA)

        self.create_window_view()
        while 1:
            cv2.imshow(self.filename, original)

            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                cv2.destroyAllWindows()
                # np.save("contr", cntr)
                return original, cntr2
        # return original, hull

    def main(self, filename):
        frame = cv2.imread(filename)
        self.filename = filename
        self.og = frame
        self.og, self.cntr = self.watershed(self.og)

        # while 1:
        #     cv2.imshow('image', m)
        #
        #     k = cv2.waitKey(5) & 0xFF
        #     if k == 27:
        #         cv2.destroyAllWindows()
        #         break
        # plt.show()
        return self.og, self.cntr


# debug run
ws = ws()
ws.main(sys.argv[1])

# ws.main("frames2/frame_0.jpg")
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
