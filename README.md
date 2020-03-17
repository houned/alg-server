# alg-server
an server for algorithm using flask

## 工程布局

> /share/algserver4bj
>     └abnormal_pics                #引起异常的请求，其携带的图片存放在这里
>     └client_res                         #客户端接收到的处理完毕的图片
>     └data                                  #ftp下载目录，算法服务完成后自动清理
>     └server_res                        #服务器处理结果，覆盖存储
>     └src                                     #服务器代码

## 启动

启动代码在 /share/algserver4bj/src

### 启动算法服务

```
CUDA_VISIBLE_DEVICES=0 python Server.py #所有AI算法部署在一台GPU上
```

处理结果可在 /share/algserver4bj/server_res 下看到

如果请求引发异常，可以在 /share/algserver4bj/abnormal_pics 下看到

#### ftp服务器配置

算法服务接收到服务请求后，访问ftp服务器获取指定资源

需要在Server.py内配置ftp服务器用户名和密码

algProcessor = AlgProcessor("ftpusr","ftptest","172.16.90.74",21,"/share/data/")

### 服务请求

```
python Client.py
```

修改代码ID，用于请求不同算法服务

`algos = 40`

| 算法名                     | 算法ID |
| -------------------------- | ------ |
| 设备运行状况分析（指示灯） | 10     |
| 线路温度分析               | 20     |
| 照明系统分析               | 30     |
| 设备盘点                   | 40     |
| 电源插座运行状态分析       | 50     |
| 烟火分析                   | 60     |

处理结果可在 /share/algserver4bj/client_res 下看到

注意：本工程并不包含上述算法