import cv2
import os
import numpy as np
import datetime


class FireCv:

    def __init__(self):
        return

    def nothing(self, x):
        pass

    def divide_video(self, o, folder, path, ext, time, video, timestamp):
        """ open video and save frame with a gap of x seconds (time) """
        count = 0
        time_inter = time * 24
        cap = video

        d = timestamp.split()
        timestamp_format = datetime.datetime(int(d[0]), int(d[1]), int(d[2]), int(d[3]), int(d[4]), int(d[5]))
        if o == 'win':
            f_path = path + "\\" + folder + "_" + str(time) + "\\"
            if os.path.exists(os.path.normpath(f_path)) is False:
                os.mkdir(f_path)
        else:
            f_path = path + "/" + folder + "_" + str(time) + "/"
            if os.path.exists(f_path) is False:
                os.mkdir(f_path)

        while cap.isOpened():
            # dividir em frame
            ret, frame = cap.read()

            # guarda imagem
            if count % time_inter == 0:
                if count is not 0:
                    timestamp_format = timestamp_format + datetime.timedelta(seconds=int(time))
                cv2.imwrite(f_path + "frame_" + str(int(count / time)) + ext, frame)
                f = open(f_path + "frame" + str(int(count / time)) + ".txt", "w")
                f.write(str(timestamp_format))

            count += 1
            if ret is False:
                cap.release()
                return True

        cap.release()
        return False

    def analize_frame(self, frame):
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)

        cv2.createTrackbar('Lower_H', 'image', 0, 179, self.nothing)
        cv2.createTrackbar('Lower_S', 'image', 0, 255, self.nothing)
        cv2.createTrackbar('Lower_V', 'image', 0, 255, self.nothing)

        cv2.createTrackbar('Upper_H', 'image', 0, 179, self.nothing)
        cv2.createTrackbar('Upper_S', 'image', 0, 255, self.nothing)
        cv2.createTrackbar('Upper_V', 'image', 0, 255, self.nothing)

        cv2.createTrackbar('iter', 'image', 0, 10, self.nothing)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

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
            img = cv2.addWeighted(frame, 0.3, img2, 0.7, 0)

            k = cv2.waitKey(5) & 0xFF
            if k == ord("s"):
                cv2.destroyWindow('image')
                return img2

    def watershed(self, original, fg, bg):
        cv2.namedWindow('ws', cv2.WINDOW_NORMAL)
        fg_all = fg[0]
        for x in range(len(fg)):
            if x > 0:
                fg_all = cv2.add(fg_all, fg[x])

        bg_all = bg[0]
        for j in range(len(bg)):
            if j > 0:
                bg_all = cv2.add(bg_all, bg[j])

        # passa para gray
        fg_gray = cv2.cvtColor(fg_all, cv2.COLOR_BGR2GRAY)
        bg_gray = cv2.cvtColor(bg_all, cv2.COLOR_BGR2GRAY)

        # simplificar
        _, thresh_fg = cv2.threshold(fg_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, thresh_bg = cv2.threshold(bg_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # retirar areas comuns que nao interresam
        mark = cv2.subtract(thresh_bg, thresh_fg)

        # encontrar area ligadas
        #_, markers = cv2.connectedComponents(thresh_fg)
        mark32 = np.int32(cv2.addWeighted(thresh_fg, 1, thresh_bg, 0.5, 0))

        # simplificar markers
        markers = mark32+ 1
        markers[mark == 255] = 0

        # watershed
        markers = cv2.watershed(original, markers)

        # encontrar contornos
        m = cv2.convertScaleAbs(markers)
        _, m = cv2.threshold(m, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cntr, h = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cv2.drawContours(original, cntr, -1, (255, 255, 255), 2)
        while 1:
            cv2.imshow('ws', original)
            k = cv2.waitKey(5) & 0xFF
            if k == ord("s"):
                cv2.destroyWindow('ws')
                return cntr, original
