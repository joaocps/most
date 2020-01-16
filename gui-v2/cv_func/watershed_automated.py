import cv2
import numpy as np


class watershed_automated:
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
        # 2 - Vegetação tons castanha
        # 3 - vegetação "clara"
        # 4 - fumo?
        # 5 - vegetação "escura"
        # 6 - estrada terra
        # 7 - Estrada / fumo cinza
        self.lower_bg = [np.array([0, 0, 220]), np.array([14, 60, 60]), np.array([30, 60, 70]), np.array([55, 30, 75]),
                         np.array([35, 40, 0]),
                         np.array([20, 35, 125]), np.array([30, 0, 0])]
        self.upper_bg = [np.array([179, 10, 255]), np.array([18, 255, 140]), np.array([35, 255, 130]),
                         np.array([95, 255, 255]),
                         np.array([75, 255, 255]), np.array([40, 60, 255]), np.array([179, 10, 255])]
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
            element = cv2.getStructuringElement(cv2.MORPH_RECT, (2 * it + 1, 2 * it + 1),
                                                (it, it))
            aux = cv2.morphologyEx(aux, cv2.MORPH_OPEN, element)
            result = cv2.bitwise_and(original, original, mask=aux)
            view = cv2.addWeighted(original, 0.1, result, 0.9, 0)
            k = cv2.waitKey(5) & 0xFF
            if k == ord("s"):
                cv2.destroyAllWindows()
                self.fg_array.append(result)
                return
            elif k == ord("d"):
                cv2.destroyAllWindows()
                return
            elif k == ord("q"):
                exit(1)

    def fine_tune_bg(self, lower, upper, hsv, original):
        view = original
        while 1:
            cv2.imshow(self.filename + "Area a omitir", view)
            aux = cv2.inRange(hsv, lower, upper)
            it = cv2.getTrackbarPos('Diminuir Area', self.filename + "Area a omitir")
            it_2 = cv2.getTrackbarPos('Limpar Ruído', self.filename + "Area a omitir")

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
            elif k == ord("d"):
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

    def watershed(self, original):

        hsv = cv2.cvtColor(original, cv2.COLOR_BGR2HSV)

        for i in range(len(self.lower_fg)):
            self.create_window()
            self.fine_tune_fg(self.lower_fg[i], self.upper_fg[i], hsv, original)

        for i in range(len(self.lower_bg)):
            self.create_window_bg()
            self.fine_tune_bg(self.lower_bg[i], self.upper_bg[i], hsv, original)

        if self.fg is None or self.bg is None:
            self.fg = []
            self.bg = []
            return None, None
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

        # simplificar Binarias
        _, thresh_fg = cv2.threshold(fg_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, thresh_bg = cv2.threshold(bg_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # retirar areas comuns que nao interresam
        mark = cv2.subtract(thresh_bg, thresh_fg)

        # simplificar markers
        mark32 = np.int32(cv2.addWeighted(thresh_fg, 1, thresh_bg, 0.5, 0))
        markers = mark32 + 1
        markers[mark == 255] = 0

        # watershed
        markers = cv2.watershed(original, markers)

        # encontrar contornos
        m = cv2.convertScaleAbs(markers)
        _, m = cv2.threshold(m, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cntr, h = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        cv2.drawContours(original, cntr, -1, (255, 255, 255), 2, cv2.LINE_AA)

        self.create_window_view()
        while 1:
            cv2.imshow(self.filename, original)

            k = cv2.waitKey(5) & 0xFF
            if k == ord("s"):
                cv2.destroyAllWindows()
                self.fg = ""
                self.bg = ""
                self.fg_array = []
                self.bg_array = []
                return original, cntr

    def workflow(self, frame, filename):
        self.filename = filename
        self.og = frame
        self.og, self.cntr = self.watershed(self.og)
        return self.og, self.cntr
