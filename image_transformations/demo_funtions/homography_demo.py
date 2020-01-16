import cv2
import numpy as np
#
# video_file = "new_vid2.mp4"
# video = cv2.VideoCapture(video_file)
#
# while True:
#     (grabbed, frame) = video.read()
#     if not grabbed:
#         break
#
#     cv2.circle(frame, (0, 300), 5, (0, 0, 255), -1)
#     cv2.circle(frame, (1270, 60), 5, (0, 0, 255), -1)
#     cv2.circle(frame, (0, 575), 5, (0, 0, 255), -1)
#     cv2.circle(frame, (1270, 575), 5, (0, 0, 255), -1)
#
#     pts1 = np.float32([[0, 300], [1270, 60], [0, 575], [1270, 575]])
#     pts2 = np.float32([[0, 0], [1500, 0], [0, 1000], [1500, 1000]])
#     matrix = cv2.getPerspectiveTransform(pts1, pts2)
#
#     result = cv2.warpPerspective(frame, matrix, (1500, 1000))
#
#     cv2.imshow("output1", frame)
#     cv2.imshow("output", result)
#
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# cv2.destroyAllWindows()
# video.release()

image_file = 'warp8k.tif'
image_file2 = 'img1.jpg'

image = cv2.imread(image_file)
image2 = cv2.imread(image_file2)


cv2.circle(image, (3443, 6987), 5, (0, 0, 255), -1)
cv2.circle(image, (3575, 7757), 5, (0, 0, 255), -1)
cv2.circle(image, (3929, 7514), 5, (0, 0, 255), -1)
cv2.circle(image, (3871, 7746), 5, (0, 0, 255), -1)

cv2.circle(image2, (1172, 100), 5, (0, 0, 255), -1)
cv2.circle(image2, (202, 266), 5, (0, 0, 255), -1)
cv2.circle(image2, (56, 664), 5, (0, 0, 255), -1)
cv2.circle(image2, (1145, 619), 5, (0, 0, 255), -1)

pts_src = np.array([[1172,100],[202,266],[56,664],[1145,619]])
pts_dst = np.array([[3443,6987],[3575,7757],[3871,7746],[3929,7514]])

h, status = cv2.findHomography(pts_src, pts_dst)

im_out = cv2.warpPerspective(image2, h , (image.shape[1], image.shape[0]))

cv2.namedWindow('src', cv2.WINDOW_NORMAL)
cv2.imshow('src',image2)

cv2.namedWindow('dst', cv2.WINDOW_NORMAL)
cv2.imshow('dst',image)

cv2.namedWindow('Warped Source Image', cv2.WINDOW_NORMAL)
cv2.imshow("Warped Source Image", im_out)

cv2.namedWindow('Overlay', cv2.WINDOW_NORMAL)
img = cv2.addWeighted(image,0.3, im_out,0.8,0)
cv2.imshow('Overlay',img)


cv2.waitKey(0)
cv2.destroyAllWindows()


