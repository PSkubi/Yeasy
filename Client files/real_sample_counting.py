import cv2
import math

def cell_counting():
    #get the chamber_num and get the prepared masks
    chamber_no = input("Enter the number of chamber:")
    chamber = 'chamber' + chamber_no + '.tif'
    chamber_img = cv2.imread(chamber)
    green_mask = 'chamber' + chamber_no + ' dil_green.tif'
    green_mask_img = cv2.imread(green_mask, cv2.IMREAD_GRAYSCALE)
    orange_mask = 'chamber' + chamber_no + ' dil_orange.tif'
    orange_mask_img = cv2.imread(orange_mask, cv2.IMREAD_GRAYSCALE)

    #delete the mask out of the chamber
    green_mask_img[:, 0:50] = 0
    green_mask_img[:, 550::] = 0
    green_mask_img[0:190, :] = 0
    green_mask_img[660::, :] = 0
    orange_mask_img[:, 0:50] = 0
    orange_mask_img[:, 550::] = 0
    orange_mask_img[0:200, :] = 0
    orange_mask_img[660::, :] = 0
    mask = [green_mask_img, orange_mask_img]

    #find the contour
    green_mask=mask[0]
    orange_mask=mask[1]
    contours_green, hierarchy = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_orange, hierarchy = cv2.findContours(orange_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours=[contours_green,contours_orange]
    mask_name=['green','orange']

    #define the area of cell
    average_cell_area = 290
    connected_cell_area = 600
    minimum_cell_area = 30

    #counting the cell and draw the detected contour
    for i in range(0,len(mask)):
        cells = 0
        contour_color=[(0,128,0),(0,128,255)]
        sum_area=0

        for c in contours[i]:
            area = cv2.contourArea(c)
            if area>minimum_cell_area:
                sum_area = sum_area + area
                cv2.drawContours(chamber_img, [c], -1, contour_color[i], 2)
                if area > connected_cell_area:
                    cells += math.floor(area / average_cell_area)
                else:
                    cells += 1

        print(mask_name[i]+'Cells: {}'.format(cells))
        print(mask_name[i]+'Area: {}'.format(sum_area))

    cv2.imshow('counted_chamber', chamber_img)
    cv2.imwrite('chamber'+chamber_no+' counted.tif', chamber_img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()