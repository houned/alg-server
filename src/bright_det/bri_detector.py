# -*- coding: utf-8 -*- 
import sys
import os
parentdir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,parentdir)

import cv2
import numpy as np
#from util.utils import *
from util import utils
import traceback

class BriDetector:
    def __init__(self):
        self.binary_thresh = 200
        self.median_blur_boxsize = 13

        #pass

    def detect_url(self, img_url):
        if not os.path.exists(img_url):
            print("file not exist! ", img_url)
    
        img = cv2.imread(img_url)
        return self.detect(img)

    #通过二值化、中值滤波、数高亮点的方式检测
    def detect(self, img):
        ret_stat = 0
        
        retval, croped = utils.crop_watermark(img)
        ret_img = croped.copy()
        if not retval:
            return 1, -1, ret_img  #状态，亮度, 返回原图

        gray = cv2.cvtColor(croped, cv2.COLOR_RGB2GRAY)
        retval, binary = cv2.threshold(gray, self.binary_thresh, 255, cv2.THRESH_BINARY)
        laser_remove = cv2.medianBlur(binary, self.median_blur_boxsize) #除去激光
        points_num = cv2.countNonZero(laser_remove)    #高亮点数量

        if points_num < 50:
            return 1, cv2.mean(gray)[0], ret_img  #状态，亮度, 返回原图
        else:
            ret_stat = 0

        gray_light = cv2.bitwise_and(gray, laser_remove)
        light_sum = cv2.sumElems(gray_light)[0]
        brightness = light_sum / points_num

        # 最小外接矩形框，有方向角
        image, contours, hierarchy = cv2.findContours(laser_remove, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            #cnt = contours[0]
            rect = cv2.minAreaRect(cnt)
            version = cv2.__version__
            if version.split('.')[0]=="4" or version.split('.')[0]=="3":
                boxp = cv2.boxPoints(rect)
            else:
                boxp = cv2.cv.BoxPoints(rect)
            box = np.int0(boxp)
            cv2.drawContours(ret_img, [box], 0, (0, 0, 255), 2)

        return ret_stat, brightness, ret_img


if __name__ == "__main__":

    test_dir = os.path.join(os.path.dirname(__file__), ".test")
    img_url = os.path.join(test_dir, "Preview_10.10.0[00_00_05][20190920-151941-0].JPG") #开灯
    img_url_2 = os.path.join(test_dir, "Preview_10.10.0[00_00_05][20190920-151953-1].JPG") #关灯
    #output_url = os.path.join(test_dir, "ret_img.jpg")
    bri_detector = BriDetector()
    ret_stat, brightness, ret_img = bri_detector.detect_url(img_url)
    ret_stat_2, brightness_2, ret_img_2 = bri_detector.detect_url(img_url_2)
    
    print( "light in pic1 is :", brightness, ", ret_stat is :", ret_stat )
    print( "light in pic1 is :", brightness_2, ", ret_stat is :", ret_stat_2 )

    cv2.imshow("aaa", ret_img)
    cv2.waitKey()  
    cv2.imshow("aaa", ret_img_2)
    cv2.waitKey()