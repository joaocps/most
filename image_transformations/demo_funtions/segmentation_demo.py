import cv2
import numpy as np


def nothing(x):
    pass


def analizeVideo(file):
    img_original = cv2.imread(file, cv2.IMREAD_COLOR)
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    # create trackbars for color change
    cv2.createTrackbar('H', 'image', 0, 360, nothing)
    cv2.createTrackbar('S', 'image', 0, 360, nothing)
    cv2.createTrackbar('V', 'image', 0, 360, nothing)

    # create switch for ON/OFF functionality
    switch = '0 : OFF \n1 : ON'
    cv2.createTrackbar(switch, 'image', 0, 1, nothing)

    hsv = cv2.cvtColor(img_original, cv2.COLOR_BGR2HSV)

    img = img_original
    cv2.setTrackbarPos('H', 'image', 0)
    cv2.setTrackbarPos('S', 'image', 74)
    cv2.setTrackbarPos('V', 'image', 217)

    while 1:
        cv2.imshow('image', img)

        # get current positions of four trackbars
        h = cv2.getTrackbarPos('H', 'image')
        s = cv2.getTrackbarPos('S', 'image')
        v = cv2.getTrackbarPos('V', 'image')
        sw = cv2.getTrackbarPos(switch, 'image')

        value = np.array([h, s, v])
        stuff = np.array([360, 360, 360])
        if sw == 0:
            img = img_original
        else:
            aux = cv2.inRange(hsv, value, stuff)
            img = cv2.bitwise_and(img_original, img_original, mask=aux)

        k = cv2.waitKey(5) & 0xFF
        if ord('s'):
            cv2.imwrite('fire_' + file, img)

        if k == 27:
            break

    cv2.destroyAllWindows()


def get_frame_from_video(vidname):
    cap = cv2.VideoCapture(vidname)
    count = 0

    while (cap.isOpened()):
        ret, frame = cap.read()
        cv2.imshow('frame', frame)

        if cv2.waitKey(1) == 13:
            filename = vidname[:-4]
            x = filename + "frame" + str(count)
            cv2.imwrite(x + ".jpg", frame)
            new_frame = x + ".jpg"
            count += 1
            analizeVideo(new_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    vidname = input("Nome do video >> ")
    get_frame_from_video(vidname)
