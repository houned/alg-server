# -*- coding: utf-8 -*- 
import cv2
import numpy as np

#读取红外图片，保存为jpg
def transInfImg(inf_img_url, jpg_img_url, width, height):
    with open(inf_img_url, 'rb') as f:
        bstream = f.read()

    img = np.reshape(np.frombuffer(bstream, np.uint8), (height, width))
    cv2.imwrite(jpg_img_url, img)

#读取红外图片，转换为numpy图像
def readInfImg(inf_img_url, width, height):
    with open(inf_img_url, 'rb') as f:
        bstream = f.read()

    img = np.reshape(np.frombuffer(bstream, np.uint8), (height, width))
    return img

#读取红外数据，转换为numpy图像
def readInfDat(inf_dat_url, width, height):
    with open(inf_dat_url, 'rb') as f:
        bstream = f.read()

    img = np.reshape(np.frombuffer(bstream, np.float64), (height, width))
    return img

if __name__ == '__main__':
    #红外图片
    inf_img_url = r'f:\Work\Projects\20190801_BeiJingProj\Data-Collection\20190919\rewangxian\545454_Picture114027.dat'
    #红外图片转存为jpg
    jpg_img_url = r'f:\Work\Projects\20190801_BeiJingProj\Data-Collection\20190919\rewangxian\545454_Picture114027.jpg'
    #红外数据
    inf_dat_url = r'f:\Work\Projects\20190801_BeiJingProj\Data-Collection\20190918\2\154654s_Thermal163352.dat'
    #数据类型是usigned char; 两种尺寸(640*512)(已确认不支持),或(384*288),标配温度范围-20~150
    transInfImg(inf_img_url, jpg_img_url, 384, 288)
    inf_dat = readInfDat(inf_dat_url, 384, 288)
    print("highest temperature is ", cv2.minMaxLoc(inf_dat)[1], ", lowest temperature is ", cv2.minMaxLoc(inf_dat)[0])