# -*- coding:utf-8 -*-
import sys
import os
parentdir = os.path.dirname(os.path.abspath(__file__))
faster_rcnn_dir = os.path.join(parentdir, "faster_rcnn")
sys.path.insert(0, faster_rcnn_dir)

#from faster_rcnn.forward_calc import FasterRcnn
from forward_calc import FasterRcnn
import os
import cv2
import numpy as np
import traceback

class EquipDetector:
    def __init__(self):
        self.net = FasterRcnn()
        self.net.load()
    
    def detect(self, img):
        ret_stat = 0
        
        res_img, bboxes_info = self.net.det(img, "equip_detect_image")
        # bboxes_info : [[pt1_x, pt1_y, pt2_x, pt2_y, score, class_name]]
        equip_list = [b[5] for b in bboxes_info]

        return ret_stat, equip_list, res_img

    def detect_url(self, url):
        img = cv2.imread(url)
        return self.detect(img)


if __name__ == "__main__":
    test_dir = os.path.join(os.path.dirname(__file__), ".test")
    img_url = os.path.join(test_dir, "equip.bmp")
    output_url = os.path.join(test_dir, "ret_img.jpg")

    equip_detector = EquipDetector()
    ret_stat, equip_list, res_img = equip_detector.detect_url(img_url)

    print("ret_stat", ret_stat)
    cv2.imwrite(output_url, res_img)
