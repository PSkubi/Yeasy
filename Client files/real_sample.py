import cv2
import numpy as np
def sample_read(sample,chamber_num):

    # read and display the image
    image_file = sample
    img=cv2.imread(image_file)
    img_colnum=img.shape[1]
    print('sample colnum: '+str(img_colnum))
    img_rownum=img.shape[0]
    print('sample rownum: '+str(img_rownum))

    #crop the image and split into multiple chambers
    cropped_img=img[img_rownum//2-400:img_rownum//2+450,img_colnum//2-9300:img_colnum//2+8800]
    cropped_colnum=cropped_img.shape[1]
    print('cropped sample colnum: '+str(cropped_colnum))
    cropped_rownum=cropped_img.shape[0]
    print('cropped sample rownum: '+str(cropped_rownum))
    chamber_col=cropped_colnum//chamber_num
    print('chamber colnum: '+str(chamber_col))
    print('chamber rownum: '+str(cropped_rownum))
    chamber_right_boundary=0
    chamber_index=1

    for chamber_left_boundary in range(0,cropped_colnum,chamber_col):
        if (cropped_colnum-chamber_left_boundary)<chamber_col:
            break

        chamber_right_boundary=chamber_left_boundary+chamber_col-1
        chamber=cropped_img[:,chamber_left_boundary:chamber_right_boundary]
        cv2.imwrite('chamber' + str(chamber_index) +'.tif', chamber)
        chamber_index = chamber_index + 1

    #separate two different fluorescence
    for i in range(1,chamber_num+1):
        chamber_name='chamber'+str(i)+'.tif'
        chamber_img=cv2.imread(chamber_name)
        chamber_hsv=cv2.cvtColor(chamber_img,cv2.COLOR_BGR2HSV)

        #get the orange one
        hsv_orange_lower=np.array([10, 40, 40])
        if i==24:
            hsv_orange_upper = np.array([12, 255, 255])
        else:
            hsv_orange_upper=np.array([18, 255, 255])

        orange_mask=cv2.inRange(chamber_hsv, hsv_orange_lower, hsv_orange_upper)
        cv2.imwrite('chamber'+str(i)+' orange'+'.tif',orange_mask)

        # get the green one
        if i == 30:
            hsv_green_lower = np.array([42, 40, 40])
        else:
            hsv_green_lower = np.array([36, 40, 35])
        hsv_green_upper = np.array([70, 255, 255])
        green_mask = cv2.inRange(chamber_hsv, hsv_green_lower, hsv_green_upper)
        cv2.imwrite('chamber' + str(i) + ' green' + '.tif', green_mask)

        #process the orange and green mask
        kernel=np.ones((2,2),np.uint8)

        #denoise
        orange_open=cv2.morphologyEx(orange_mask,cv2.MORPH_OPEN,kernel, iterations = 1)
        green_open=cv2.morphologyEx(green_mask,cv2.MORPH_OPEN,kernel, iterations =1)
        cv2.imwrite('chamber' + str(i) + ' open_orange' + '.tif', orange_open)
        cv2.imwrite('chamber' + str(i) + ' open_green' + '.tif', green_open)

        #find the background
        orange_dilation=cv2.dilate(orange_open,kernel,iterations=2)
        green_dilation = cv2.dilate(green_open, kernel, iterations=2)
        cv2.imwrite('chamber'+str(i)+' dil_orange'+'.tif',orange_dilation)
        cv2.imwrite('chamber' + str(i) + ' dil_green' + '.tif', green_dilation)