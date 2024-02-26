image_file='yeast.jpeg'

def counting_cell(image_file):
    import cv2
    import numpy as np
    import math
    yeast_image = cv2.imread(image_file)
    blue, green, red= cv2.split(yeast_image)
    red[:]=0
    yeast_without_red=cv2.merge((blue, green,red))
    cv2.imshow('Image with Red Turned Black', yeast_without_red)
    cv2.imwrite('yeast_without_red.jpeg',yeast_without_red)

    hsv1 = cv2.cvtColor(yeast_without_red, cv2.COLOR_BGR2HSV)
    hsv_lower = np.array([35,0,35])
    hsv_upper = np.array([75,255,255])
    mask1 = cv2.inRange(hsv1, hsv_lower, hsv_upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10,10))
    mask1 = cv2.dilate(mask1,kernel,iterations=1)
    cv2.imshow('hsv1', mask1)
    cv2.imwrite('hsv1.jpeg',mask1)
    contours1, hierarchy1 = cv2.findContours(mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    yeast_image = cv2.imread(image_file)
    blue, green, red= cv2.split(yeast_image)
    green[:]=0
    yeast_without_green=cv2.merge((blue, green,red))

    hsv2 = cv2.cvtColor(yeast_without_green, cv2.COLOR_BGR2HSV)
    hsv_lower = np.array([0,0,35])
    hsv_upper = np.array([10,255,255])
    mask2 = cv2.inRange(hsv2, hsv_lower, hsv_upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10,10))
    dilate = cv2.dilate(mask2,kernel,iterations=1)
    cv2.imshow('hsv2', dilate)
    cv2.imwrite('hsv2.jpeg',dilate)
    contours2, hierarchy2 = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    def cell_counting(cont, img):
        minimum_area = 300 * math.pi
        average_cell_area = 1200 * math.pi
        connected_cell_area = 10000 * math.pi
        cells = 0
        for c in cont:
            area = cv2.contourArea(c)
            if area > minimum_area:
                cv2.drawContours(img, [c], -1, (255, 0, 0), 2)
                if area > connected_cell_area:
                    cells += math.ceil(area / average_cell_area)
                else:
                    cells += 1

        print('Cells: {}'.format(cells))
        return img

    counted_red=cell_counting(contours2,yeast_without_green)
    counted_green=cell_counting(contours1,yeast_without_red)
    cv2.imshow('counted_green',counted_green)
    cv2.imshow('counted_red',counted_red)

    cv2.imwrite('counted_green.jpeg',counted_green)
    cv2.imwrite('counted_red.jpeg',counted_red)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

counting_cell(image_file)