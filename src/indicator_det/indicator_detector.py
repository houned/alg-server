# -*- coding:utf-8 -*-
import sys
import os
from PIL import Image
parentdir = os.path.dirname(os.path.abspath(__file__))
deeplabv3_dir = os.path.join(parentdir, "pytorch_deeplab_xception")
# sys.path.insert(0, deeplabv3_dir)
sys.path.append(deeplabv3_dir)
print(sys.path)

from forward_calc_d import DeepLabNari
import os
import cv2
import numpy as np
import traceback

# 参考训练集脚本的配置
# label_color = {     #标签必须从1开始
#         'green': (1, 1, 1),
#         'blue': (2, 2, 2),
#         'red': (3, 3, 3)
#     }

class IndicatorDetector:
    def __init__(self):
        self.net = DeepLabNari()
        self.net.load()
        self.red_label = 3 #根据标签配置。图像分割的输出中，红色指示灯的标签
    
    def detect(self, img):#需要传入PIL.Image
        ret_stat = 0
        
        vis, pixel_pred = self.net.det(img) # shape (1080, 1920),即输入图片的尺寸
        if self.red_label in pixel_pred:
            ret_stat = 1
            
        img = np.array(img)
        res_img = cv2.addWeighted(img, 0.7, vis.astype(np.uint8), 0.5, 0)

        return ret_stat, res_img

    def detect_url(self, url):
        #img = cv2.imread(url)
        img = Image.open(url).convert('RGB')
        return self.detect(img)


if __name__ == "__main__":
    test_dir = os.path.join(os.path.dirname(__file__), ".test")
    img_url = os.path.join(test_dir, "indicator_1.jpg")
    output_url = os.path.join(test_dir, "ret_img.jpg")

    indicator_detector = IndicatorDetector()
    ret_stat, res_img = indicator_detector.detect_url(img_url)

    print("ret_stat", ret_stat)
    cv2.imwrite(output_url, res_img)
