import os
import numpy as np
import cv2
import traceback

class SocketDetector:

    def __init__(self):
        self.lowerb = np.array([135, 100, 255]) #识别目标的色彩下限，hsv空间
        self.upperb = np.array([165, 255, 255]) #识别目标的色彩上限，hsv空间
        self.min_domin_area = 2

    #返回值：
    #分析结果，0:正常，1：异常
    #分析结果图标出两个目标高亮点
    def detect(self, img):
        img = cv2.medianBlur(img, 3) #除去椒盐噪声
        ret_img = img.copy()
        w, h, c  = img.shape

        #在hsv空间下滤波出目标
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lowerb, self.upperb)

        #用连通域确定目标位置
        nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity = 8, ltype = cv2.CV_16U )
        print("the numbers of connected components is: ", nlabels) #连通域数目
        print("position and area of circumscribed rectangle: \n", stats) #连通域外接矩形位置及面积
        print("centroids: \n", centroids) #连通域中心
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

        #打印连通域中心
        for i,c in enumerate(centroids_t):
            x = int(round(c[0]))
            y = int(round(c[1]))
            #print ("xy", x, " ", y)
            print( "center of connected components {}, Coordinates:{}".format( i, ( int(round(c[0])), int(round(c[1])) ) ) )  
            print( "center of connected components {}, color(RGB):{}, color(HSV):{}".format( i, img[y, x], hsv[y, x]) )  

        #框出连通域
        for s in stats_t:
            x = s[0]
            y = s[1]
            w = s[2]
            h = s[3]
            cv2.rectangle(ret_img, (x, y), (x+w, y+h), (0, 255, 255))

        ret_stat = 1
        if len(stats_t) == 2:
            ret_stat = 0
        else:
            ret_stat = 1

        return ret_stat, ret_img


    def detect_url(self, img_url):
        if not os.path.exists(img_url):
            print("file not exist! ", img_url)
    
        img = cv2.imread(img_url)
        return self.detect(img)

    

if __name__ == "__main__":
    test_dir = os.path.join(os.path.dirname(__file__), ".test")
    img_url = os.path.join(test_dir, "Preview_192.168.1.18_Came_20190919_172845_26696451.bmp") #开 2
    #img_url = os.path.join(test_dir, "Preview_192.168.1.18_Came_20190919_173042_26813186.bmp") #关 1
    #img_url = os.path.join(test_dir, "Preview_192.168.1.18_Came_20190919_173339_26990278.bmp") #关 1
    #img_url = os.path.join(test_dir, "Preview_192.168.1.18_Came_20190919_173452_27063443.bmp") #开 2
    #img_url = os.path.join(test_dir, "Preview_192.168.1.18_Came_20190919_173659_27190911.bmp") #开 3,中值滤波2
    #img_url = os.path.join(test_dir, "Preview_192.168.1.18_Came_20190919_173828_27279645.bmp") #关 0，原因是亮度才186
    output_url = os.path.join(test_dir, "ret_img.jpg")
    socket_detector = SocketDetector()
    ret_stat, ret_img = socket_detector.detect_url(img_url)
    print("ret_stat", ret_stat)
    cv2.imwrite(output_url, ret_img)

   