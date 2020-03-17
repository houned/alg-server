# -*- coding: utf-8 -*- 
from ctypes import *
import math
import random

def sample(probs):
    s = sum(probs)
    probs = [a/s for a in probs]
    r = random.uniform(0, 1)
    for i in range(len(probs)):
        r = r - probs[i]
        if r <= 0:
            return i
    return len(probs)-1

def c_array(ctype, values):
    arr = (ctype*len(values))()
    arr[:] = values
    return arr

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

class ODBox:
    def __init__(self,name,prob,minx,miny,maxx,maxy):
        self.name = name
        self.prob = prob
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy 

class Darknet:
    def __init__(self,libpath):
        self.lib = CDLL(libpath, RTLD_GLOBAL)
        self.lib.network_width.argtypes = [c_void_p]
        self.lib.network_width.restype = c_int
        self.lib.network_height.argtypes = [c_void_p]
        self.lib.network_height.restype = c_int

        self.predict = self.lib.network_predict
        self.predict.argtypes = [c_void_p, POINTER(c_float)]
        self.predict.restype = POINTER(c_float)

        self.set_gpu = self.lib.cuda_set_device
        self.set_gpu.argtypes = [c_int]

        self.make_image = self.lib.make_image
        self.make_image.argtypes = [c_int, c_int, c_int]
        self.make_image.restype = IMAGE

        self.get_network_boxes = self.lib.get_network_boxes
        self.get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int)]
        self.get_network_boxes.restype = POINTER(DETECTION)

        self.make_network_boxes = self.lib.make_network_boxes
        self.make_network_boxes.argtypes = [c_void_p]
        self.make_network_boxes.restype = POINTER(DETECTION)

        self.free_detections = self.lib.free_detections
        self.free_detections.argtypes = [POINTER(DETECTION), c_int]

        self.free_ptrs = self.lib.free_ptrs
        self.free_ptrs.argtypes = [POINTER(c_void_p), c_int]

        self.network_predict = self.lib.network_predict
        self.network_predict.argtypes = [c_void_p, POINTER(c_float)]

        self.reset_rnn = self.lib.reset_rnn
        self.reset_rnn.argtypes = [c_void_p]

        self.load_net = self.lib.load_network
        self.load_net.argtypes = [c_char_p, c_char_p, c_int]
        self.load_net.restype = c_void_p

        self.do_nms_obj = self.lib.do_nms_obj
        self.do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

        self.do_nms_sort = self.lib.do_nms_sort
        self.do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

        self.free_image = self.lib.free_image
        self.free_image.argtypes = [IMAGE]

        self.letterbox_image = self.lib.letterbox_image
        self.letterbox_image.argtypes = [IMAGE, c_int, c_int]
        self.letterbox_image.restype = IMAGE

        self.load_meta = self.lib.get_metadata
        self.lib.get_metadata.argtypes = [c_char_p]
        self.lib.get_metadata.restype = METADATA

        self.load_image = self.lib.load_image_color
        self.load_image.argtypes = [c_char_p, c_int, c_int]
        self.load_image.restype = IMAGE

        self.rgbgr_image = self.lib.rgbgr_image
        self.rgbgr_image.argtypes = [IMAGE]

        self.predict_image = self.lib.network_predict_image
        self.predict_image.argtypes = [c_void_p, IMAGE]
        self.predict_image.restype = POINTER(c_float)

    def classify(net, meta, im):
        out = predict_image(net, im)
        res = []
        for i in range(meta.classes):
            res.append((meta.names[i], out[i]))
        res = sorted(res, key=lambda x: -x[1])
        return res


    def detect(self,net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
        im = self.load_image(image, 0, 0)
        num = c_int(0)
        pnum = pointer(num)
        self.predict_image(net, im)
        dets = self.get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
        num = pnum[0]
        if (nms): self.do_nms_obj(dets, num, meta.classes, nms);

        res = []
        for j in range(num):
            for i in range(meta.classes):
                if dets[j].prob[i] > 0:
                    b = dets[j].bbox
                    w_2 = int(b.w/2)
                    h_2 = int(b.h/2)
                    minx = int(b.x)-w_2
                    miny = int(b.y)-h_2
                    maxx = int(b.x)+w_2
                    maxy = int(b.y)+h_2
                    res.append((meta.names[i], dets[j].prob[i], (minx, miny, maxx, maxy)))
        res = sorted(res, key=lambda x: -x[1])
        self.free_image(im)
        self.free_detections(dets, num)
        r = []
        for od in res:
            oDBox = ODBox(od[0],od[1],od[2][0],od[2][1],od[2][2],od[2][3])
            r.append(oDBox)
        return r

    #by wuchao
    def array_to_image(self,arr):
        arr = arr.transpose(2,0,1)
        c = arr.shape[0]
        h = arr.shape[1]
        w = arr.shape[2]
        arr = (arr/255.0).flatten()
        data = c_array(c_float, arr)
        im = IMAGE(w,h,c,data)
        return im
    #by wuchao
    def detect_np(self,net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
        im = self.array_to_image(image)
        num = c_int(0)
        pnum = pointer(num)
        self.predict_image(net, im)
        dets = self.get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
        num = pnum[0]
        if (nms): self.do_nms_obj(dets, num, meta.classes, nms)
        res = []
        for j in range(num):
            for i in range(meta.classes):
                if dets[j].prob[i] > 0:
                    b = dets[j].bbox
                    w_2 = int(b.w/2)
                    h_2 = int(b.h/2)
                    minx = int(b.x)-w_2
                    miny = int(b.y)-h_2
                    maxx = int(b.x)+w_2
                    maxy = int(b.y)+h_2
                    res.append((meta.names[i], dets[j].prob[i], (minx, miny, maxx, maxy)))
        res = sorted(res, key=lambda x: -x[1])
        self.free_detections(dets, num)
        r = []
        for od in res:
            oDBox = ODBox(od[0],od[1],od[2][0],od[2][1],od[2][2],od[2][3])
            r.append(oDBox)
        return r

    #by wuchao
    def detect_cv(self,net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
        im = self.array_to_image(image)
        self.rgbgr_image(im)
        num = c_int(0)
        pnum = pointer(num)
        self.predict_image(net, im)
        dets = self.get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
        num = pnum[0]
        if (nms): self.do_nms_obj(dets, num, meta.classes, nms)
        res = []
        for j in range(num):
            for i in range(meta.classes):
                if dets[j].prob[i] > 0:
                    b = dets[j].bbox
                    w_2 = int(b.w/2)
                    h_2 = int(b.h/2)
                    minx = int(b.x)-w_2
                    miny = int(b.y)-h_2
                    maxx = int(b.x)+w_2
                    maxy = int(b.y)+h_2
                    res.append((meta.names[i], dets[j].prob[i], (minx, miny, maxx, maxy)))
        res = sorted(res, key=lambda x: -x[1])
        self.free_detections(dets, num)
        r = []
        for od in res:
            oDBox = ODBox(od[0],od[1],od[2][0],od[2][1],od[2][2],od[2][3])
            r.append(oDBox)
        return r
class Yolo3:
    def __init__(self,libPath,cfgPath,weigthsPath,metaPath):
        self.darknet = Darknet(libPath)
        self.net = self.darknet.load_net(cfgPath,weigthsPath,0)
        self.meta = self.darknet.load_meta(metaPath)
    def detect_path(self,imagePath,thresh):
        print("detect...")
        return self.darknet.detect(self.net,self.meta,imagePath,thresh=0.5)
    def detect_np(self,img,thresh):
        print("detect...")
        return self.darknet.detect_np(self.net,self.meta,img,thresh=0.5)
    def detect_cv(self,img,thresh):
        print("detect...")
        return self.darknet.detect_cv(self.net,self.meta,img,thresh=thresh)
if __name__ == "__main__":
    #net = load_net("cfg/densenet201.cfg", "/home/pjreddie/trained/densenet201.weights", 0)
    #im = load_image("data/wolf.jpg", 0, 0)
    #meta = load_meta("cfg/imagenet1k.data")
    #r = classify(net, meta, im)
    #print r[:10]
    # net = load_net("/home/wuchao/files/Darknet/darknet/python/cfg/yolov3-voc-power_test.cfg", "/home/wuchao/files/Darknet/darknet/python/cfg/yolov3-voc-power.backup", 0)
    # meta = load_meta("/home/wuchao/files/Darknet/darknet/python/cfg/power-voc.data")
    # r = detect(net, meta, "/home/wuchao/files/Darknet/darknet/python/data/a.jpg")
    print("")
    

