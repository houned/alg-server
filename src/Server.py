# -*- coding: utf-8 -*-
import os
#os.environ["CUDA_VISIBLE_DEVICES"] = '1'
from flask import Flask
from flask import request
import json
import traceback
import cv2
import argparse
from AlgProcessor import AlgProcessor

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

#创建算法处理器
algProcessor = AlgProcessor("ftpusr","ftptest","localhost",21,"/share/algserver4bj/data")
#algProcessor = AlgProcessor("ftpusr","ftptest","172.16.90.74",21,"/share/algserver4bj/data")
#algProcessor = AlgProcessor("test","test","localhost",21,"/home/zuot/Work/20190815-Beijing_computer_room_inspection/algsever4bj/data/")
#algProcessor = AlgProcessor("test","test","localhost",21,"f:\\Work\\Projects\\20190801_BeiJingProj\\algserver4bj\\data")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', default='0.0.0.0', type=str)
    parser.add_argument('--port', dest='port', default=9091, type=int)
    #parser.add_argument('--gpu', dest='gpu', default='0', type=str)    #"CUDA_VISIBLE_DEVICES"必须写在import Flask之前才有效
    args = parser.parse_args()
    return args

'''
算法服务接口信息查看
'''
@app.route('/')
def Server_Info():
    ip = request.remote_addr
    print("remote ip:", ip)
    info = '<h1>This Server is for algserver4bj project <h1/>'
    info += '<h3>Server_Info:	http://0.0.0.0:9091/ <h3/><br/>'
    info += '<h3>Client_Info:	{} <h3/><br/>'.format(ip)
    return info

#@app.route('/Func_Device_Status_Voice', methods=['GET', 'POST'])
@app.route('/Algorithmic_Service', methods=['GET', 'POST'])
def algorithmic_service():
    print()
    print("### Service request received ###")
    ip = request.remote_addr
    print("remote ip:", ip)
    
    try:
        in_paras = request.get_data().decode('utf-8')
        print(in_paras)
        in_paras = json.loads(in_paras)
        #会话参数解析
        session = in_paras["Session"]       #会话ID
        pos = in_paras["Position_ID"]       #机器人所在位置ID
        preset = in_paras["Preset_ID"]      #摄像头所在的Position_ID
        algos = in_paras["Algos"]           #算法类型
        alg_para = in_paras["Alg_Inpara"]   #算法入参
    except Exception as err:
        print("ERROR! Exception:{}".format(err))
        traceback.print_exc()
        ret_stat = -1
        alg_res = {"Desc":"Error parsing session parameters", "Status":ret_stat}
    else:
        try:
            res_data={}
            #根据算法类型，执行不同算法
            if algos == 10:		#运行异常分析
            	alg_res = algProcessor.indicator_analysis(alg_para, algos, session, pos, preset)
            elif algos == 20:		#线路温度分析（温度）
                alg_res = algProcessor.circuit_temp(alg_para, algos, session, pos, preset)
            elif algos == 30:		#照明系统分析
                alg_res = algProcessor.bright_sys(alg_para, algos, session, pos, preset)
            elif algos == 40:     #设备盘点
                alg_res = algProcessor.equipment_inventory(alg_para, algos, session, pos, preset) 
            elif algos == 50:		#电源插座运行状态分析（图像识别）
                alg_res = algProcessor.socket_analysis(alg_para, algos, session, pos, preset)
            elif algos == 60:		#烟火分析（温度+图像）
                alg_res = algProcessor.fire_warning(alg_para, algos, session, pos, preset)
            else:
                raise Exception("Error, not support algos number")
        except Exception as err:
            print("ERROR! Exception: {}".format(err))
            #traceback.print_exc()
            ret_stat = -1
            alg_res = {"Desc":str(err), "Status":ret_stat}

    #分析结果返回
    res_data = {"Session":session, "Position_ID":pos, "Preset_ID":preset, "Algos":algos, "Alg_Res":alg_res}
    print("### Service Complete ###")
    return json.dumps(res_data)

if __name__ == '__main__':    
    print("select gpu {}".format(os.environ["CUDA_VISIBLE_DEVICES"]))
    args = parse_args()
    app.run(str(args.host), args.port)
