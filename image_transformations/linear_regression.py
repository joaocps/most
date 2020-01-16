import cv2

class linear_regression(object):

    def __init__(self, georef_x_max, georef_x_min, georef_y_max, georef_y_min):
        # GeoReferencial Points
        self.georef_x_max = georef_x_max
        self.georef_x_min = georef_x_min
        self.georef_y_max = georef_y_max
        self.georef_y_min = georef_y_min

        # Original Image Points
        self.original_x_min = 0
        self.original_x_max = None
        self.original_y_min = 0
        self.original_y_max = None

    def lets_test(self):

        img = cv2.imread('Images/warp8k.tif')
        self.original_y_max, self.original_x_max, channels = img.shape

        print(self.original_y_max)
        print(self.georef_x_max)
        print(self.original_x_max)

        # TODO: Implement linear regression -> lat(x) = mx+n
        # Lat(0) = georef_x_min = n
        # Lat(original_x_max) = m * original_x_max + georef_x_min
        # georef_x_max = m * original_x_max + georef_x_min
        # m = (georef_x_max - georef_x_min) / original_x_max

        # Convert x point
        m_x = (self.georef_x_max - self.georef_x_min) / self.original_x_max
        x_point_to_convert = float(input("(X) Point to convert to georef > "))
        result_x = (m_x * x_point_to_convert) + self.georef_x_min

        print("(X) New Point > ", result_x)

        # Convert y point

        m_y = (self.georef_y_max - self.georef_y_min) / self.original_y_max
        y_point_to_convert = float(input("(Y) Point to convert to georef > "))
        result_y = (m_y * y_point_to_convert) + self.georef_y_min

        print("(Y) New Point > ", result_y)




if __name__ == '__main__':
    linear_regression(616268.574,615202.199,4583991.175,4582453.191).lets_test()
