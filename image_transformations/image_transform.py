import time

import cv2
import numpy
import numpy as np

ARRAYPOINTS_FIRE = []
ARRAYPOINTS_VERTICAL = []


def get_points(event, x, y, flags, param):

    if event == cv2.EVENT_LBUTTONDBLCLK:
        fire_image_points = (x, y)
        print(fire_image_points)
        cv2.circle(fire_image_open, (fire_image_points), 5, (0, 0, 255), -1)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(fire_image_open, str(len(ARRAYPOINTS_FIRE)), fire_image_points, font, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
        ARRAYPOINTS_FIRE.append((x, y))

        print(ARRAYPOINTS_FIRE)


def get_points_warp(event, x, y, flags, param):

    if event == cv2.EVENT_LBUTTONDBLCLK:
        vertical_image_points = (x, y)
        print(vertical_image_points)
        cv2.circle(vertical_image_open, (vertical_image_points), 5, (0, 0, 255), -1)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(vertical_image_open, str(len(ARRAYPOINTS_VERTICAL)), vertical_image_points, font, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
        ARRAYPOINTS_VERTICAL.append((x, y))

        print(ARRAYPOINTS_VERTICAL)

def convert_points_to_vertical_image(textfile,transform_matrix):

    # Use generated transform matrix to convert points between images

    points_to_convert = textfile
    tm = transform_matrix

    pts = np.array(points_to_convert, dtype="float32")
    pts = np.array([pts])

    converted_points = cv2.perspectiveTransform(pts, h)

    return converted_points

def load_points_from_file():

    # Load segmentation points from original image

    try:
        h
    except NameError:
        print("Need to transform the image first!")
        return

    points_file = input("File with points to convert > ")
    try:
        l = np.load(points_file)

        pretty_points = []
        for item in l:
            for i in item:
                for x in i:
                    pretty_points.append([x[0], x[1]])

        print(pretty_points)

        vertical_points_convertion = convert_points_to_vertical_image(pretty_points, h)

        convert_points_to_georef(vertical_points_convertion)

    except IOError:
        print("File not found, try again")
        load_points_from_file()



def convert_points_to_georef(vertical_points_convertion):

    # Linear Regression Model to convert points to GeoRef

    # georef_x_min = float(input("Minimum x value for Image Georef system > "))
    # georef_x_max = float(input("Maximum x value for Image Georef system > "))
    # georef_y_min = float(input("Minimum y value for Image Georef system > "))
    # georef_y_max = float(input("Maximum y value for Image Georef system > "))

    georef_x_min = 615202.199
    georef_x_max = 616268.574
    georef_y_min = 4583991.175
    georef_y_max = 4582453.191


    original_y_max, original_x_max, channels = vertical_image_open.shape

    # Convert x point
    m_x = (georef_x_max - georef_x_min) / original_x_max

    # Convert y point
    m_y = (georef_y_max - georef_y_min) / original_y_max

    full_converted_points = []
    for it1 in vertical_points_convertion:
        for it2 in it1:
            full_converted_points.append([(m_x * it2[0]) + georef_x_min, (m_y * it2[1]) + georef_y_min])

    np.save("converted", full_converted_points)

if __name__ == "__main__":


    # vertical_image = input("Vertical Image? >> ")
    # fire_image = input("Fire Image? >> ")

    fire_image_open = cv2.imread("Images/img1.jpg")
    clone = fire_image_open.copy()
    cv2.namedWindow("FireImage", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("FireImage", get_points)

    vertical_image_open = cv2.imread("Images/warp8k.tif")
    clone2 = vertical_image_open.copy()
    cv2.namedWindow("VerticalImage", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("VerticalImage", get_points_warp)

    while True:
        cv2.imshow("FireImage",fire_image_open)
        cv2.imshow("VerticalImage", vertical_image_open)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("r"):

            print(">> ... RESET POINTS ...")
            fire_image_open = clone.copy()
            vertical_image_open = clone2.copy()
            ARRAYPOINTS_FIRE = []
            ARRAYPOINTS_VERTICAL = []

        if key == ord("t"):
            if len(ARRAYPOINTS_FIRE) == len(ARRAYPOINTS_VERTICAL) and len(ARRAYPOINTS_VERTICAL) > 3 :

                arraypoints_fire = np.array(ARRAYPOINTS_FIRE)
                arraypoints_vertical = np.array(ARRAYPOINTS_VERTICAL)

                h, status = cv2.findHomography(arraypoints_fire,arraypoints_vertical)

                warped_image = cv2.warpPerspective(fire_image_open, h, (vertical_image_open.shape[1],vertical_image_open.shape[0]))

                cv2.namedWindow('Warped Source Image', cv2.WINDOW_NORMAL)
                cv2.imshow("Warped Source Image", warped_image)

                cv2.namedWindow('Overlay', cv2.WINDOW_NORMAL)
                overlay_image = cv2.addWeighted(vertical_image_open,0.3,warped_image,0.8,0)
                cv2.imshow('Overlay',overlay_image)


            else:
                print(">> NUMBER OF POINTS NOT EQUAL, TRY AGAIN")
                print(">> ... RESET POINTS ...")
                fire_image_open = clone.copy()
                vertical_image_open = clone2.copy()
                ARRAYPOINTS_FIRE = []
                ARRAYPOINTS_VERTICAL = []

        if key == ord("\r"):
            load_points_from_file()

        if key == ord("s"):
            cv2.imwrite("overlayed.jpg", overlay_image)

        if key == ord("q"):
            break



