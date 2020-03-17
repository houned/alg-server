import os
import sys
import cv2
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from util import read_inf
import traceback

#红外火焰检测器
#根据红外温度判断着火情况
#class InfFireDetector:
class FireTempDetector:
    def __init__(self):
        self.threshold = 150
    
    def detect(self, inf_img, inf_dat):
        min_val, max_temp, min_indx, max_indx = cv2.minMaxLoc(inf_dat)

        ret_stat = 0
        if max_temp >= self.threshold:
            ret_stat = 1

        return ret_stat, max_temp

    def detect_url(self, width, height, inf_img_url, inf_dat_url):
        inf_img = read_inf.readInfImg(inf_img_url, width, height)
        inf_dat = read_inf.readInfDat(inf_dat_url, width, height)
        
        return self.detect(inf_img, inf_dat)



if __name__ == '__main__':
        
    test_dir = os.path.join(os.path.dirname(__file__), ".test")
    inf_img_url = os.path.join(test_dir, "fire.inf")
    inf_data_url = os.path.join(test_dir, "fire.dat")
    #output_url = os.path.join(test_dir, "ret_img.jpg")
    fire_temp_detector = FireTempDetector()
    ret_stat, max_temp = fire_temp_detector.detect_url(384, 288, inf_img_url, inf_data_url)
    print("ret_stat", ret_stat)
    print("max_temp", max_temp)
    #cv2.imwrite(output_url, ret_img)