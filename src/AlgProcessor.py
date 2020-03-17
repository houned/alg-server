# -*- coding: utf-8 -*- 
import json
import os
import cv2
import base64
import traceback
import shutil
from util.FTP import FTPHandler
from bright_det.bri_detector import BriDetector
from fire_det.fire_temp_detector import FireTempDetector
from fire_det.fire_detector import FireDetector
from socket_analysis.socket_light_detector import SocketDetector 
from circuit_det.circuit_detector import CircuitDetector
from equip_det.equip_detector import EquipDetector
#from indicator_det.detectColor import RedLightDetector # 方案一：毛进伟的方案
from indicator_det.indicator_detector import IndicatorDetector # 方案二：deeplapv3+的方案
from util.utils import *
from util.read_inf import *

DEBUG = True

def image_to_base64(img):
    retval, buffer = cv2.imencode('.bmp', img)
    return base64.b64encode(buffer).decode('ascii') 

def exception_save(img_abspath, alg_name, algos, session, pos, preset):
    try:
        out_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/abnormal_pics"
        save_name = "{}_a{}_s{}_p{}_p{}".format(alg_name, algos, session, pos, preset) + "." + img_abspath.split(".")[-1]
        out_path = os.path.join(out_dir, save_name)
        shutil.copyfile( img_abspath, out_path)
    except Exception as err:
        print("ERROR! Exception:{}".format(err))
        print("Error in indicator_analysis exception pic save")
        print("copy from {} to {}".format(img_abspath, out_path))

def debug_save(file_name, ret_img):
    output_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), "server_res"), file_name)
    cv2.imwrite(output_path, ret_img)
    return output_path


class FtpDownloader:
    def __init__(self, ip, port, user, passwd):
        self.ip = ip
        self.port = port
        self.user_name = user
        self.passwd = passwd
        self.local_path = "./"
        self.local_files = []
        self.ftp_handler = None

    def set_local_path(self, path):
        self.local_path = path

    def establish_connect(self):
        try:
            self.ftp_handler = FTPHandler(self.ip, self.port)
            self.ftp_handler.login(self.user_name, self.passwd)
        except Exception as err:
            raise Exception(str(err) + " \nError occurred while ftp downing")

    def down(self, url, local_fname):
        try:
            local_url = os.path.join(self.local_path, local_fname)
            self.ftp_handler.download_file(local_url, url)
            self.local_files.append(local_url)
        except Exception as err:
            raise Exception(str(err) + " \nError occurred while ftp downing")
        return os.path.abspath(local_url)

    def clean(self):
        #清除下载的文件
        for f in self.local_files:
            if os.path.exists(f):
                os.remove(f)
        self.local_files.clear()
        self.ftp_handler.close()    #关闭ftp

    #def __del__(self):
    #    self.ftp_handler.close()
    #    print("ftp close with FtpDownloader deconstruct")



class AlgProcessor:
    def __init__(self,FTP_UserName,FTP_Passwd,FTP_IP,FTP_Port,Data_Path):
        #self.FTP_UserName = FTP_UserName
        #self.FTP_Passwd = FTP_Passwd
        #self.FTP_IP = FTP_IP
        #self.FTP_Port = FTP_Port
        #self.Data_Path = Data_Path
        if os.path.exists(Data_Path)== False:
            os.mkdir(Data_Path)		
        self.ftp_downloader = FtpDownloader(FTP_IP, FTP_Port, FTP_UserName, FTP_Passwd)
        self.ftp_downloader.set_local_path(Data_Path)
        print("\n### equip detector loding....")
        self.equip_detector = EquipDetector()
        print("\n### fire detector loding....")
        self.fire_detector = FireDetector()
        print("\n### indicator detector loding....")
        self.indicator_detector = IndicatorDetector()

    """
    设备运行异常分析（指示灯）
    Algos == 10
    """
    def indicator_analysis(self, alg_para, algos, session, pos, preset):
        try:
            #算法参数解析
            Image_Url = alg_para["Image_Url"]
        except Exception as err:
            print("ERROR! Exception:{}".format(err))
            traceback.print_exc()
            raise Exception("Error parsing alg input parameters")
        else:
            #算法执行
            try:
                #FTP下载
                self.ftp_downloader.establish_connect()
                img_abspath = self.ftp_downloader.down(Image_Url, session+".bmp")

                #算法执行
                # 方案一：毛进伟的方案
                # reddetector = RedLightDetector() # 放到构造函数里去
                # ret_stat, bboxes, ret_img = reddetector.detectColor(img_abspath) #bboxes = (x, y, w, h, l, s)
                # base64_code = image_to_base64(ret_img)
                # 方案二：deeplapv3+的方案  
                ret_stat, ret_img = self.indicator_detector.detect_url(img_abspath)
                base64_code = image_to_base64(ret_img)

                #调试
                if DEBUG:
                    print("ret_stat", ret_stat)
                    output_dir = debug_save("res_indicator.bmp", ret_img)
                    #output_dir = debug_save(session + "_" + "res_indicator.bmp", ret_img)
                    print("save res_image to", output_dir)
                
                #清除下载的文件
                self.ftp_downloader.clean()

                #响应
                alg_res = {"Status":ret_stat, "Image_Base64":base64_code}    #Light_Value范围0-1
                alg_res["Desc"] = "Normal" if not ret_stat else "Abnormal"
            except Exception as err:
                print("ERROR! Exception:{}".format(err))
                traceback.print_exc()
                exception_save(img_abspath, "indicator", algos, session, pos, preset)
                raise Exception(err)

        return alg_res

    """
    线路温度分析（温度）
    Algos == 20
    """
    def circuit_temp(self, alg_para, algos, session, pos, preset):
        try:
            #算法参数解析
            Width = alg_para["Width"]; Height = alg_para["Height"]
            Inf_Temp_Data_Url = alg_para["Inf_Temp_Data_Url"]
            Inf_Temp_Image_Url = alg_para["Inf_Temp_Image_Url"]
            Image_Url = alg_para["Image_Url"]
        except Exception as err:
            print("ERROR! Exception:{}".format(err))
            traceback.print_exc()
            raise Exception("Error parsing alg input parameters")
        else:
            #算法执行
            try:
                #FTP下载
                self.ftp_downloader.establish_connect()
                img_abspath = self.ftp_downloader.down(Image_Url, session+".bmp")
                dat_abspath = self.ftp_downloader.down(Inf_Temp_Data_Url, session+".dat")
                infimg_abspath = self.ftp_downloader.down(Inf_Temp_Image_Url, session+".inf")

                #算法执行
                circuit_detector = CircuitDetector()
                ret_stat, max_temp, ret_img = circuit_detector.detect_url(Width, Height, infimg_abspath, dat_abspath)
                base64_code = image_to_base64(ret_img)

                #调试
                if DEBUG:
                    print("ret_stat", ret_stat)
                    print("max_temp", max_temp)
                    output_dir = debug_save("res_circuit.bmp", ret_img)
                    #output_dir = debug_save(session + "_" + "res_circuit.bmp", ret_img)
                    print("save res_image to", output_dir)

                #清除下载的文件
                self.ftp_downloader.clean()

                #响应
                alg_res = {"Status":ret_stat, "Temp_Value":max_temp, "Image_Base64":base64_code}  
                alg_res["Desc"] = "Normal" if not ret_stat else "Abnormal"
            except Exception as err:
                print("ERROR! Exception:{}".format(err))
                traceback.print_exc()
                exception_save(img_abspath, "circuit", algos, session, pos, preset)
                raise Exception(err)

        return alg_res

    """
    照明系统分析（图像）
    Algos == 30
    """
    def bright_sys(self, alg_para, algos, session, pos, preset):
        try:
            #算法参数解析
            Image_Url = alg_para["Image_Url"]
        except Exception as err:
            print("ERROR! Exception:{}".format(err))
            traceback.print_exc()
            raise Exception("Error parsing alg input parameters")
        else:
            #算法执行
            try:
                #FTP下载
                self.ftp_downloader.establish_connect()
                img_abspath = self.ftp_downloader.down(Image_Url, session+".bmp")

                #算法执行
                #img = read_one_frame(downln_path, 0)
                bri_detector = BriDetector()
                ret_stat, brightness, ret_img = bri_detector.detect_url(img_abspath)
                base64_code = image_to_base64(ret_img)

                #调试
                if DEBUG:
                    print("ret_stat", ret_stat)
                    print("brightness", brightness)
                    output_dir = debug_save("res_bright.bmp", ret_img)
                    #output_dir = debug_save(session + "_" + "res_bright.bmp", ret_img)
                    print("save res_image to", output_dir)

                #清除下载的文件
                self.ftp_downloader.clean()

                #响应
                alg_res = {"Status":ret_stat, "Light_Value":brightness / 255.0, "Image_Base64":base64_code}    #Light_Value范围0-1
                alg_res["Desc"] = "Normal" if not ret_stat else "Abnormal"
            except Exception as err:
                print("ERROR! Exception:{}".format(err))
                traceback.print_exc()
                exception_save(img_abspath, "bright", algos, session, pos, preset)
                raise Exception(err)

        return alg_res

    """
    设备盘点
    Algos == 40
    """
    def equipment_inventory(self, alg_para, algos, session, pos, preset):
        try:
            #算法参数解析
            Image_Url = alg_para["Image_Url"]
        except Exception as err:
            print("ERROR! Exception:{}".format(err))
            traceback.print_exc()
            raise Exception("Error parsing alg input parameters")
        else:
            #算法执行
            try:
                #FTP下载
                self.ftp_downloader.establish_connect()
                img_abspath = self.ftp_downloader.down(Image_Url, session+".bmp")

                #算法执行
                #equip_detector = EquipDetector()
                ret_stat, equip_list, ret_img = self.equip_detector.detect_url(img_abspath)
                base64_code = image_to_base64(ret_img)

                #调试
                if DEBUG:
                    print("ret_stat", ret_stat)
                    print("equip_list", equip_list)
                    output_dir = debug_save("res_equip.bmp", ret_img)
                    #output_dir = debug_save(session + "_" + "res_equip.bmp", ret_img)
                    print("save res_image to", output_dir)


                #清除下载的文件
                self.ftp_downloader.clean()

                #响应
                alg_res = {"Status":ret_stat, "Equip_List":equip_list, "Image_Base64":base64_code}
                alg_res["Desc"] = "Normal" if not ret_stat else "Abnormal"
            except Exception as err:
                print("ERROR! Exception:{}".format(err))
                traceback.print_exc()
                exception_save(img_abspath, "equipment", algos, session, pos, preset)
                raise Exception(err)

        return alg_res


    """
    电源插座运行状态分析（图像）
    Algos == 50
    """
    def socket_analysis(self, alg_para, algos, session, pos, preset):
        try:
            #算法参数解析
            Image_Url = alg_para["Image_Url"]
        except Exception as err:
            print("ERROR! Exception:{}".format(err))
            traceback.print_exc()
            raise Exception("Error parsing alg input parameters")
        else:
            #算法执行
            try:
                ##FTP下载
                self.ftp_downloader.establish_connect()
                img_abspath = self.ftp_downloader.down(Image_Url, session+".bmp")

                #算法执行
                socket_detector = SocketDetector()
                ret_stat, ret_img = socket_detector.detect_url(img_abspath)
                base64_code = image_to_base64(ret_img)

                #调试
                if DEBUG:
                    print("ret_stat", ret_stat)
                    output_dir = debug_save("res_socket.bmp", ret_img)
                    #output_dir = debug_save(session + "_" + "res_socket.bmp", ret_img)
                    print("save res_image to", output_dir)

                #清除下载的文件
                self.ftp_downloader.clean()

                #响应
                alg_res = {"Status":ret_stat, "Image_Base64":base64_code}
                alg_res["Desc"] = "Normal" if not ret_stat else "Abnormal"

            except Exception as err:
                print("ERROR! Exception:{}".format(err))
                traceback.print_exc()
                exception_save(img_abspath, "socket", algos, session, pos, preset)
                raise Exception(err)

        return alg_res

    """
    烟火分析（图像）
    Algos == 60
    """
    def fire_warning(self, alg_para, algos, session, pos, preset):
        try:
            #算法参数解析
            Image_Url = alg_para["Image_Url"]
            Width = alg_para["Width"]; Height = alg_para["Height"]
            Inf_Temp_Data_Url = alg_para["Inf_Temp_Data_Url"]
            Inf_Temp_Image_Url = alg_para["Inf_Temp_Image_Url"]
        except Exception as err:
            print("ERROR! Exception:{}".format(err))
            traceback.print_exc()
            raise Exception("Error parsing alg input parameters")
        else:
            #算法执行
            try:
                #FTP下载
                self.ftp_downloader.establish_connect()
                img_abspath = self.ftp_downloader.down(Image_Url, session+".bmp")
                dat_abspath = self.ftp_downloader.down(Inf_Temp_Data_Url, session+".dat")
                infimg_abspath = self.ftp_downloader.down(Inf_Temp_Image_Url, session+".inf")

                #算法执行
                #fire_detector = FireDetector()
                ret_stat, det_num, ret_img = self.fire_detector.detect_url(img_abspath)
                fire_temp_detector = FireTempDetector()
                ret_stat_2, max_temp = fire_temp_detector.detect_url(Width, Height, infimg_abspath, dat_abspath)

                status = 0
                if ret_stat == -1 or ret_stat_2 == -1:
                    status = -1
                elif ret_stat == 1 and ret_stat_2 == 1:
                #if ret_stat == 1:
                    status = 1
                base64_code = image_to_base64(ret_img)

                #调试
                if DEBUG:
                    print("ret_stat of fire_detector", ret_stat)
                    print("det_num", det_num)
                    print("ret_stat of fire_temp_detector", ret_stat_2)
                    print("max_temp", max_temp)
                    output_dir = debug_save("res_fire.bmp", ret_img)
                    #output_dir = debug_save(session + "_" + "res_fire.bmp", ret_img)
                    print("save res_image to", output_dir)

                #清除下载的文件
                self.ftp_downloader.clean()	

                #响应
                alg_res = {"Status":status, "Temp_Value":max_temp, "Image_Base64":base64_code}
                alg_res["Desc"] = "Normal" if not status else "Abnormal"
                
            except Exception as err:
                print("ERROR! Exception:{}".format(err))
                traceback.print_exc()
                exception_save(img_abspath, "fire", algos, session, pos, preset)
                raise Exception(err)

        return alg_res

