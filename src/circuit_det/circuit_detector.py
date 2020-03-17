import sys
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

import numpy as np
import cv2
#from skimage import morphology, img_as_ubyte
from util import read_inf
import traceback

class CircuitDetector:
    def __init__(self):
        self.high_temp = 80 #34.0  
        self.min_domin_area = 2
    
    #区域1是否包含区域2
    def is_region_contain(self, s1, s2):
        retVal = False
        x1_up = s1[0]
        y1_up = s1[1]
        x1_down = s1[0] + s1[2]
        y1_down = s1[1] + s1[3]
        x2_up = s2[0]
        y2_up = s2[1]
        x2_down = s2[0] + s2[2]
        y2_down = s2[1] + s2[3]
        if x1_up <= x2_up and y1_up <= y2_up and x1_down >= x2_down and y1_down >= y2_down:
            retVal = True
        #print("2 points in region s1 ", (x1_up, y1_up), " ", (x1_down, y1_down))
        #print("2 points in region s2 ", (x2_up, y2_up), " ", (x2_down, y2_down))
        #print("retVal: ", retVal)

        return retVal

    def skeleton(self):
        #ret_img = inf_img.copy()

        #_, mask_high = cv2.threshold(inf_data, self.high_temp, 255, cv2.THRESH_BINARY)
        #mask_high = mask_high.astype(np.uint8)
        #print(inf_img.shape, " ", inf_img.dtype)
        #print(mask_high.shape, " ", mask_high.dtype)
        #img_high = cv2.bitwise_and(inf_img, mask_high)
        #cv2.imwrite("ret_high.jpg", img_high)

        #提取骨干
        #_, mask_binary = cv2.threshold(mask_high, 0, 1, cv2.THRESH_BINARY)
        #skeleton_sk =morphology.skeletonize(mask_binary)
        #skeleton = img_as_ubyte(skeleton_sk)
        #cv2.imwrite("ret2.jpg", skeleton)
        pass


    #返回值：
    #分析结果，0:正常，1：异常
    #最大温度值
    #分析结果图标出异常温度点
    def detect(self, inf_img, inf_data):
        ret_stat = 0

        ret_img = inf_img.copy()

        #判断温度是否正常，标记非正常区域
        minVal, max_temp, minLoc, maxLoc = cv2.minMaxLoc(inf_data)
        if max_temp > self.high_temp:
            ret_stat = 1
        #print(ret_stat)
        _, mask_high = cv2.threshold(inf_data, self.high_temp, 255, cv2.THRESH_BINARY)
        mask_high = mask_high.astype(np.uint8)

        #用连通域识别法确定高温目标位置
        nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_high, connectivity = 8, ltype = cv2.CV_16U )
        print("the numbers of connected components is: ", nlabels) #连通域数目
        print("position and area of circumscribed rectangle: \n", stats) #连通域外接矩形位置及面积
        #print("centroids: \n", centroids) #连通域中心
        label_vec = []
        stats_t = []
        centroids_t = []
        for n in range(nlabels):
            if n == 0:
                continue #滤除背景
            if stats[n][4] <= self.min_domin_area:
                continue #滤除面积小于2的区域
            label_vec.append(n)
            stats_t.append(stats[n])
            centroids_t.append(centroids[n])
        print("num of target region: ", len(label_vec))

        #只保留外层框
        stats_re = []
        stats_temp = stats_t.copy()
        stats_temp = sorted(stats_temp, key=lambda s:s[4], reverse=True) #按照外接矩形的面积排序，从大到小
        for i in range(len(stats_temp)):
            curr_s = stats_temp[i]
            contained = False
            for j in range(i): #遍历面积更大的矩形
                s = stats_temp[j]
                if self.is_region_contain(s, curr_s): #如果当前区域没有被更大面积的矩形包含
                    contained = True
            if not contained:
                stats_re.append(curr_s)
        print("num of remain Outermost region: ", len(stats_re))

        #框出连通域
        for s in stats_re:
            x = s[0]
            y = s[1]
            w = s[2]
            h = s[3]
            cv2.rectangle(ret_img, (x, y), (x+w, y+h), (255, 255, 0))

        return ret_stat, max_temp, ret_img

    def detect_url(self, width, height, inf_img_url, inf_data_url):
        if not os.path.exists(inf_img_url):
            print("file not exist! ", inf_img_url)
        if not os.path.exists(inf_data_url):
            print("file not exist! ", inf_data_url)
    
        #inf_img = read_inf.readInfImg(inf_img_url, 384, 288)
        inf_img = read_inf.readInfImg(inf_img_url, width, height)
        #inf_data = read_inf.readInfDat(inf_data_url, 384, 288)
        inf_data = read_inf.readInfDat(inf_data_url, width, height)

        return self.detect(inf_img, inf_data)


if __name__ == "__main__":
    test_dir = os.path.join(os.path.dirname(__file__), ".test")
    inf_img_url = os.path.join(test_dir, "545454_Picture114027.dat")
    inf_data_url = os.path.join(test_dir, "545454_Thermal114027.dat")
    output_url = os.path.join(test_dir, "ret_img.jpg")
    circuit_detector = CircuitDetector()
    ret_stat, max_temp, ret_img = circuit_detector.detect_url(384, 288, inf_img_url, inf_data_url)
    print("ret_stat", ret_stat)
    print("max_temp", max_temp)
    cv2.imwrite(output_url, ret_img)