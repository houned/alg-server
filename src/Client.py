# -*- coding: utf-8 -*- 
import requests 
import json 
import cv2
import base64
import os
import numpy as np
url = 'http://127.0.0.1:9091/Algorithmic_Service' 
#url = 'http://47.92.31.25:8888/Algorithmic_Service' 

def base64_to_image(base64_code):
    buffer = base64.b64decode(base64_code.encode(encoding='utf-8'))
    np_buffer = np.frombuffer(buffer, dtype=np.uint8)
    img = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


# 发送算法请求
def det_req(algos, alg_inpara, res_pic_name):
    body = {"Session":"123-423-60-65464","Position_ID":31231,"Preset_ID":423424,"Algos":algos,"Alg_Inpara":alg_inpara} 
    headers = {'content-type': "application/json", 'Authorization': 'APP appid = 4abf1a,token = 9480295ab2e2eddb8'} 

    response = requests.post(url, data = json.dumps(body), headers = headers) 
    res = json.loads(response.text)
    alg_res = res["Alg_Res"]
    print("### session info ###")
    for key, value in res.items():
        if not key == "Alg_Res":
            print(key,":", value)
    print("### res output ###")
    for key, value in alg_res.items():
        if not key == "Image_Base64":
            print(key, ":", value)
        else:
            print("{} : {}... (has {} character)".format(key, value[:20], len(value)))

    base64_code = alg_res["Image_Base64"]
    img = base64_to_image(base64_code)
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(os.path.join(os.path.dirname(curr_dir), "client_res"), res_pic_name)
    cv2.imwrite(output_dir, img)
    print("Image_Base64 save to {}".format(output_dir))



if __name__ == "__main__":

    algos = 40
    alg_inpara = None
    res_pic_name = None

    if algos == 10:      #运行异常分析（指示灯）
        alg_inpara = {"Image_Url":"/share/algserver4bj/ftp/indicator_normal.bmp"}
        res_pic_name = "res_indicator.bmp"
    elif algos == 20:    #线路温度分析（温度）
        alg_inpara = {"Width":384, "Height":288, "Inf_Temp_Data_Url":"/share/algserver4bj/ftp/circuit.dat", "Inf_Temp_Image_Url":"/share/algserver4bj/ftp/circuit.inf", "Image_Url":"/share/algserver4bj/ftp/circuit.bmp"}
        res_pic_name = "res_circuit.bmp"
    elif algos == 30:    #照明系统分析
        alg_inpara = {"Image_Url":"/share/algserver4bj/ftp/bright_on.bmp"}
        res_pic_name = "res_bright.bmp"
    elif algos == 40:    #设备盘点
        alg_inpara = {"Image_Url":"/share/algserver4bj/ftp/equip.bmp"}
        res_pic_name = "res_equip.bmp"
    elif algos == 50:    #电源插座运行状态分析（图像识别）
        alg_inpara = {"Image_Url":"/share/algserver4bj/ftp/socket_on.bmp"}
        res_pic_name = "res_socket.bmp"
    elif algos == 60:    #烟火分析（温度+图像）
        alg_inpara = {"Image_Url":"/share/algserver4bj/ftp/fire.jpg", "Width":384, "Height":288, "Inf_Temp_Data_Url":"/share/algserver4bj/ftp/fire.dat", "Inf_Temp_Image_Url":"/share/algserver4bj/ftp/fire.inf"}
        res_pic_name = "res_fire.bmp"

    print("sent alg para")
    print("{")
    for key, value in alg_inpara.items():
        print(key, ":", value)
    print("}")
    det_req(algos, alg_inpara, res_pic_name)
