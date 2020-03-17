# -*- coding: utf-8 -*- 
import os
import cv2
import numpy as np

# 逐帧读取，返回指定帧
def read_one_frame(video_url, fNum):
    if (not os.path.exists(video_url)):
        print("file not exists! ", video_url)
        return None

    cap = cv2.VideoCapture(video_url)
    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")
    
    cnt = 0
    res = None
    # Read until video is completed
    while(cap.isOpened() and cnt <= fNum):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
            if cnt == fNum:
                res = frame.copy()
        else: 
            break
        cnt += 1
    cap.release()
    return res

# 逐帧读取，保存在目录 “Filename_FileExtension”
def save_multi_frames(video_url):
    if (not os.path.exists(video_url)):
        print("file not exists! ", video_url)
        return None

    (fpath, basename) = os.path.split(video_url)
    (fname, fextension) = os.path.splitext(basename)
    outpath = fpath + "/" + fname + "_" + fextension[1:]
    if (not os.path.exists(outpath)):
        os.makedirs(outpath)

    cap = cv2.VideoCapture(video_url)
    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")

    cnt = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            cv2.imwrite(os.path.join(outpath, str(cnt) + ".jpg"), frame)
        else:
            break
        cnt += 1
    cap.release()
    return

#验证1080p图像的shape
def isShape1080(image):
    shape = image.shape
    ret = True
    if shape[0] != 1080 or shape[1] != 1920:
        ret = False
        print("Error image shape: ", shape)
    return ret

#裁切掉1080P图像的水印
def crop_watermark(image):
    if isShape1080(image):
        croped = image[65:1080, :]
        return True, croped
    else:
        return False, image



if __name__ == "__main__":
    img = read_one_frame(r"f:\Work\Projects\20190801_BeiJingProj\algserver4bj\data\test.mp4", 0)
    cv2.imshow("image", img)
    cv2.waitKey()

    save_multi_frames(r"f:\Work\Projects\20190801_BeiJingProj\algserver4bj\data\test.mp4")