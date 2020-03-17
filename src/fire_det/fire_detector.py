# -*- coding:utf-8 -*-
# Stupid python path shit.
# Instead just add darknet.py to somewhere in your python path
# OK actually that might not be a great idea, idk, work in progress
# Use at your own risk. or don't, i don't care

import sys
import cv2
import os
import time
import datetime
import numpy as np
import math
import traceback

sys.path.append(os.path.join(sys.path[0],'fire_det'))
from Yolo import Yolo3


def Caltime(baseTime, sysTime):
    sysTime = datetime.datetime.strftime(sysTime, "%Y/%m/%d")

    baseTime = time.strptime(baseTime, "%Y/%m/%d")
    sysTime = time.strptime(sysTime, "%Y/%m/%d")

    date1 = datetime.datetime(baseTime[0], baseTime[1], baseTime[2])
    date2 = datetime.datetime(sysTime[0], sysTime[1], sysTime[2])
    # print((date2-date1).days)#将天数转成int型
    return (date2 - date1).days

def drawResImg(img, rect, resInfo):
    if rect[0] < 0:
        rect[0] = 0
    if rect[1] < 0:
        rect[1] = 0
    rect_w = rect[2] - rect[0]
    if rect_w >= 200:
        label_w, label_h = 80, 50
        str_loc = (0, 33)
        str_size = 0.75
    elif rect_w >= 100:
        label_w, label_h = 70, 40
        str_loc = (0, 26)
        str_size = 0.65
    else:
        label_w, label_h = rect_w, 30
        str_loc = (0, 21)
        str_size = 0.5
    label_img = cv2.cvtColor(np.zeros((label_h, label_w), dtype=np.uint8), cv2.COLOR_GRAY2BGR)
    label_img[:, :, 2] = 255
    cv2.putText(label_img, resInfo, str_loc, cv2.FONT_HERSHEY_SIMPLEX, str_size, (0, 0, 0), 1)
    cv2.rectangle(img, (rect[0], rect[1]), (rect[2], rect[3]), (0, 0, 255), 1)
    ##将label信息覆盖到原图上
    img[rect[1]:rect[1] + label_h, rect[0]:rect[0] + label_w, :] = label_img

'''
def detector():
    curPath = os.getcwd()
    ## init Yolo3
    yolo3 = Yolo3(bytes(curPath + "/../cfg/libdarknet.so", encoding='utf-8'), 
                  bytes(curPath + "/../cfg/yolov3-voc-power.cfg", encoding='utf-8'),
                  bytes(curPath + "/../cfg/yolov3-voc-power_10000.weights", encoding='utf-8'), 
                  bytes(curPath + "/../cfg/power-voc.data", encoding='utf-8')
                 )
    originImg = cv2.imread(sys.argv[1])
    yolo3_res = yolo3.detect_cv(originImg, thresh=0.5)
    if len(yolo3_res) != 0:
        # print("yolo3 res: ", yolo3_res)
        secStageRes = []
        for res in yolo3_res:
            print(res.name)
            if res.name == b'fire':
                resStatus = "FIRE"
                drawResImg(originImg, [res.minx, res.miny, res.maxx, res.maxy], resStatus)
        [filePath, fileFullName] = os.path.split(sys.argv[1])
        [fileName, fileFormat] = fileFullName.split(".")
        cv2.imwrite(curPath + "/resImgs/" + fileName + "_result." + fileFormat, originImg)
    else:
        print("no fire...")
'''
'''
def detector_path():
    curPath = os.getcwd()
    ## init Yolo3
    yolo3 = Yolo3(bytes(curPath + "/../cfg/libdarknet.so", encoding='utf-8'), 
                  bytes(curPath + "/../cfg/yolov3-voc-power.cfg", encoding='utf-8'),
                  bytes(curPath + "/../cfg/yolov3-voc-power_10000.weights", encoding='utf-8'), 
                  bytes(curPath + "/../cfg/power-voc.data", encoding='utf-8')
                 )
    srcImgs = os.listdir(sys.argv[1])
    num = len(srcImgs)
    for i in range(int(num)):
        print("#####this is " + str(i + 1) + " image: " + srcImgs[i] + "#####")
        [fileName, fileFormat] = srcImgs[i].split(".")
        start = time.time()
        originImg = cv2.imread(sys.argv[1] + srcImgs[i])
        yolo3_res = yolo3.detect_cv(originImg, thresh=0.5)
        if len(yolo3_res) != 0:
            # print("yolo3 res: ", yolo3_res)
            # secStageRes = []
            for res in yolo3_res:
                print("name: ", res.name, " prob: ", res.prob)
                if res.name == b'fire':
                    resStatus = "FIRE"
                    drawResImg(originImg, [res.minx, res.miny, res.maxx, res.maxy], resStatus)
            cv2.imwrite(curPath + "/resImgs/" + fileName + "_result." + fileFormat, originImg)
        else:
            print("no fire!!!!!!!!!!!")
        end = time.time()
        print('detect an image spend: %s seconds' % (end - start))
'''

#火焰检测器
#使用Yolo模型检测火焰
class FireDetector:
    def __init__(self):
        ## init Yolo3
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        cfg_path = os.path.join(cur_dir, "yolov3/fireDetect/cfg")
        self.yolo3 = Yolo3(bytes(os.path.join(cfg_path, "libdarknet.so"), encoding='utf-8'),
                      bytes(os.path.join(cfg_path, "yolov3-voc-power.cfg"), encoding='utf-8'),
                      bytes(os.path.join(cfg_path, "yolov3-voc-power_10000.weights"), encoding='utf-8'),
                      bytes(os.path.join(cfg_path, "power-voc.data"), encoding='utf-8')
                     )

    def detect(self, img):
        ret_stat = 0
        yolo3_res = self.yolo3.detect_cv(img, thresh=0.5)

        ret_img = img.copy()
        if len(yolo3_res) != 0:
            # print("yolo3 res: ", yolo3_res)
            ret_stat = 1
            for res in yolo3_res:
                print(res.name)
                if res.name == b'fire':
                    resStatus = "FIRE"
                    drawResImg(ret_img, [res.minx, res.miny, res.maxx, res.maxy], resStatus)

        return ret_stat, len(yolo3_res), ret_img

    def detect_url(self, img_url):
        if not os.path.exists(img_url):
            print("file not exist! ", img_url)
        
        img = cv2.imread(img_url)
        if img is None:
            print("file read error! ", img_url)

        return self.detect(img)





if __name__ == '__main__':
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    test_dir = os.path.join(os.path.dirname(__file__), ".test")
    img_url = os.path.join(test_dir, "fire.bmp")
    #inf_img_url = os.path.join(test_dir, "fire.inf")
    #inf_data_url = os.path.join(test_dir, "fire.dat")
    output_url = os.path.join(test_dir, "ret_img.jpg")
    fire_detector = FireDetector()
    ret_stat, det_num, ret_img = fire_detector.detect_url(img_url)
    print("ret_stat", ret_stat)
    print("max_temp", det_num)
    cv2.imwrite(output_url, ret_img)