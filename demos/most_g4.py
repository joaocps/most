import cv2
import numpy as np


def nothing(x):
    pass


def divide_video(videoname):
    count = 0
    cap = cv2.VideoCapture(videoname)

    while cap.isOpened():
        # dividir em frame
        ret, frame = cap.read()

        # guarda imagem
        if count % 240 == 0:
            anal_frame = analize_frame(frame)
            cv2.imwrite("frame" + str(count / 240) + ".jpg", anal_frame)
        count += 1

    cap.release()


def analize_frame(frame):
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)

    cv2.createTrackbar('Lower_H', 'image', 0, 179, nothing)
    cv2.createTrackbar('Lower_S', 'image', 0, 255, nothing)
    cv2.createTrackbar('Lower_V', 'image', 0, 255, nothing)

    cv2.createTrackbar('Upper_H', 'image', 0, 179, nothing)
    cv2.createTrackbar('Upper_S', 'image', 0, 255, nothing)
    cv2.createTrackbar('Upper_V', 'image', 0, 255, nothing)

    cv2.createTrackbar('iter', 'image', 0, 10, nothing)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    cv2.setTrackbarPos('Lower_H', 'image', 0)
    cv2.setTrackbarPos('Lower_S', 'image', 74)
    cv2.setTrackbarPos('Lower_V', 'image', 217)

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
        if k == 27:
            cv2.destroyWindow('image')
            filename = input("guardar como(deixar vazio para descartar): ")
            if filename != "":
                cv2.imwrite(filename + ".jpg", img2)
            return img
    # return img


def watershed(original, fg, bg):
    # TODO juntar todos os fg e bg
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
    _, markers = cv2.connectedComponents(thresh_fg)

    # simplificar markers
    markers = markers + 1
    markers[mark == 255] = 0

    # watershed
    markers = cv2.watershed(original, markers)

    # encontrar contornos
    m = cv2.convertScaleAbs(markers)
    _, m = cv2.threshold(m, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cntr, h = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # simplificar contornos
    hull = []
    for i in range(len(cntr)):
        hull.append(cv2.convexHull(cntr[i], False))
    cv2.drawContours(original, hull, -1, (255, 255, 255), 2)
    while 1:
        cv2.imshow('ws', original)
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            cv2.destroyWindow('ws')
            filename = input("guardar como(deixar vazio para descartar): ")
            if filename != "":
                cv2.imwrite(filename + ".jpg", original)
            return


if __name__ == "__main__":
    while 1:
        op = input("1 - video\n2 - Imagem\n3 - Segmetação\n0 - sair\nopção: ")
        if op == '1':
            vidname = input("Nome do video >> ")
            divide_video(vidname)
        elif op == '2':
            image = input("Nome da imagem >> ")
            im = cv2.imread(image)
            analize_frame(im)
        elif op == '3':
            f_ori = input("Imagem original >> ")
            ori = cv2.imread(f_ori)
            aux = int(input("Número de ficheiros de áreas de relevante/outras >> "))
            i = 0
            fg_a = []
            bg_a = []
            while i < aux:
                f_fg = input("Ficheiro area de relevante >> ")
                f_bg = input("Ficheiro area NÂO relevante >> ")
                fg_a.append(cv2.imread(f_fg))
                bg_a.append(cv2.imread(f_bg))
                i += 1
            watershed(ori, fg_a, bg_a)
        elif op == '0':
            break

cv2.destroyAllWindows()
