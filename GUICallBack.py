import win32api,win32gui,win32con,win32process
import pygame
import ctypes
import time
import datetime
import calendar
import re
import os
import threading
import random
from SheetGUI import *

#数据记录字典
DataDict={}
TodayDict={}
#上次获取到的前台窗口信息
LastTime=0
LastHwnd=0
LastText=''
LastPath=''
#超时提醒状态信息
RemindStatus=False
RemindThread=None
RemindPath=""
RemindTime=0
RemindType=""
ExitFlag=False
#超时提醒显示窗口时退出热键显示窗口线程
ShowFlag=False
#按钮样式变量
BtnStatus=[]
for i in range(8):
    BtnStatus.append(False)
#按钮左上角坐标
#1080,661
BtnPos=[[65,243],[65,357],[65,473],[302,243],[302,357],[302,473],[987,52],[1018,42]]
#加载按钮
BtnPng=[]
for i in range(1,7):
    BtnPng.append(pygame.image.load("Images/Hover"+str(i)+".png"))
#加载控制按钮
BtnPng.append(pygame.image.load("Images/Min.png"))
BtnPng.append(pygame.image.load("Images/Close.png"))
#加载鼠标光标
CurArrow=pygame.image.load("Images/Arrow.cur")
CurHand=pygame.image.load("Images/Hand.cur")

def FadeOut(Hwnd):
    """
    淡出后退出
    """
    for i in range(240,1,-1):
        win32gui.SetLayeredWindowAttributes(Hwnd,0,i,win32con.LWA_ALPHA)
        pygame.display.flip()
        pygame.time.delay(3)
    pygame.quit()

def IsInRect(cx,cy,x,y,width,height):
    """
    判断点是否在矩形内部
    cx,cy:点坐标
    x,y:矩形左上角坐标
    width,height:矩形长和宽
    """
    if (x<cx<x+width) and (y<cy<y+height):
        return True
    else:
        return False

def MouseMoveCheckButton(x,y):
    """
    鼠标移动时检查是否需要更改按钮样式
    """
    for i in range(6):
        if IsInRect(x,y,BtnPos[i][0],BtnPos[i][1],200,55):
            BtnStatus[i]=True
        else:
            BtnStatus[i]=False
    if IsInRect(x,y,BtnPos[6][0]-10,BtnPos[6][1]-15,30,25):
        BtnStatus[6]=True
    else:
        BtnStatus[6]=False
    if IsInRect(x,y,BtnPos[7][0]-6,BtnPos[7][1]-6,25,25):
        BtnStatus[7]=True
    else:
        BtnStatus[7]=False

def HotKeyShowWindow(Hwnd):
    """隐藏窗口后检测热键以显示窗口"""
    win32gui.ShowWindow(Hwnd,win32con.SW_HIDE)
    global ShowFlag
    ShowFlag=False
    while True:
        if ShowFlag:
            return
        if win32api.GetAsyncKeyState(win32con.VK_LCONTROL) and win32api.GetAsyncKeyState(win32con.VK_F10):
            win32gui.ShowWindow(Hwnd,win32con.SW_SHOW)
            win32gui.SetActiveWindow(Hwnd)
            break
        time.sleep(0.1)

def IsDayEnd():
    """判断今天是否已结束，如果结束则写入文件并重置今日数据"""
    #判断今天是否已结束
    global LastTime,LastText,LastPath,DataDict,TodayDict
    while True:
        t=time.time()
        TimeNow=time.localtime(t)
        IsDayEnd=TimeNow[3]==23 and TimeNow[4]==59 and TimeNow[5]==59
        if IsDayEnd:
            NowTime=int(t)
            NowTuple=(LastPath,LastText)
            #总数据
            if NowTuple in DataDict:
                DataDict.update({NowTuple:DataDict[NowTuple]+(NowTime-LastTime)})
            else:
                DataDict.update({NowTuple:NowTime-LastTime})
            #今日数据
            if NowTuple in TodayDict:
                TodayDict.update({NowTuple:TodayDict[NowTuple]+(NowTime-LastTime)})
            else:
                TodayDict.update({NowTuple:NowTime-LastTime})
            SaveData(LastTime,NowTime)
            #如果今天已结束则加一秒跳到第二天并重置今日数据
            if IsDayEnd:
                LastTime=NowTime+1
                TodayDict={}
                #建立第二天数据文件
                file=open('data/'+time.strftime("%Y-%m-%d", time.localtime(LastTime))+'.txt','wb')
                file.write(str(TodayDict).encode("utf-8"))
                file.close()
        time.sleep(1)

def GetForegroundInfo(hwnd=0,type=0):
    """
    获取前台窗口信息
    hwnd:主窗口句柄,用于type=1时初始化数据
    type:(默认)0-运行期间
                   1-首次获取
                   2-程序结束
    """
    global LastTime,LastText,LastPath,DataDict,TodayDict
    if type==0:
        #运行期间
        #循环获取前台窗口信息直到获取成功
        while True:
            Hwnd=win32gui.GetForegroundWindow() #窗口句柄
            Text=win32gui.GetWindowText(Hwnd) #窗口标题
            _,Pid=win32process.GetWindowThreadProcessId(Hwnd) #进程标识符
            #数字超出2字节整型范围或小于0代表获取出错
            if Pid >= 65535 or Pid < 0:
                continue
            try:
                Handle=win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION,False,Pid) #进程句柄
            except:
                continue
            Path=win32process.GetModuleFileNameEx(Handle,0) #进程路径
            break
        #如果和上次不同则写入文件
        if Text != LastText or Path !=LastPath:
            NowTime=int(time.time())
            NowTuple=(LastPath,LastText)
            #总数据
            if NowTuple in DataDict:
                DataDict.update({NowTuple:DataDict[NowTuple]+(NowTime-LastTime)})
            else:
                DataDict.update({NowTuple:NowTime-LastTime})
            #今日数据
            if NowTuple in TodayDict:
                TodayDict.update({NowTuple:TodayDict[NowTuple]+(NowTime-LastTime)})
            else:
                TodayDict.update({NowTuple:NowTime-LastTime})
            SaveData(LastTime,NowTime)
            #更新上次数据
            LastText=Text
            LastPath=Path
            LastTime=NowTime
    elif type==1:
        #首次获取
        #初始化信息
        LastTime=int(time.time())
        LastHwnd=hwnd #窗口句柄
        LastText=win32gui.GetWindowText(LastHwnd) #窗口标题
        _,Pid=win32process.GetWindowThreadProcessId(LastHwnd) #进程标识符
        Handle=win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION,False,Pid) #进程句柄
        LastPath=win32process.GetModuleFileNameEx(Handle,0) #进程路径
        #判断本地是否存在统计文件夹,不存在则创建
        IsDataPathExists=os.path.exists('data')
        if not IsDataPathExists:
            os.mkdir("data")
        #判断本地是否存在日志文件夹,不存在则创建
        IsLogPathExists=os.path.exists('log')
        if not IsLogPathExists:
            os.mkdir("log")
        #判断本地是否存在总统计文件,不存在则创建
        IsDataExists=os.path.exists('data/data.txt')
        if(IsDataExists):
            file=open('data/data.txt','rb')
            DataDict=eval(file.read())
            file.close()
        else:
            file=open('data/data.txt','wb')
            file.write(str(DataDict).encode("utf-8"))
            file.close()
        #判断本地是否存在今日统计文件,不存在则创建
        IsLogExists=os.path.exists('data/'+time.strftime("%Y-%m-%d", time.localtime())+'.txt')
        if(IsLogExists):
            file=open('data/'+time.strftime("%Y-%m-%d", time.localtime())+'.txt','rb')
            TodayDict=eval(file.read())
            file.close()
        else:
            file=open('data/'+time.strftime("%Y-%m-%d", time.localtime())+'.txt','wb')
            file.write(str(TodayDict).encode("utf-8"))
            file.close()
    elif type==2:
        #程序结束
        NowTime=int(time.time())
        NowTuple=(LastPath,LastText)
        #总数据
        if NowTuple in DataDict:
            DataDict.update({NowTuple:DataDict[NowTuple]+(NowTime-LastTime)})
        else:
            DataDict.update({NowTuple:NowTime-LastTime})
        #今日数据
        if NowTuple in TodayDict:
            TodayDict.update({NowTuple:TodayDict[NowTuple]+(NowTime-LastTime)})
        else:
            TodayDict.update({NowTuple:NowTime-LastTime})
        SaveData(LastTime,NowTime)

def SaveData(LastTime,NowTime):
    """将数据及日志写入文件"""
    #总数据
    file=open('data/data.txt','wb')
    file.write(str(DataDict).encode("utf-8"))
    file.close()
    #今日数据
    file=open('data/'+time.strftime("%Y-%m-%d", time.localtime(NowTime))+'.txt','wb')
    file.write(str(TodayDict).encode("utf-8"))
    file.close()
    #日志
    file=open('log/'+time.strftime("%Y-%m-%d", time.localtime(NowTime))+'.txt','ab+')
    file.write(str(time.strftime("%H:%M:%S", time.localtime(LastTime))+" - "+time.strftime("%H:%M:%S", time.localtime(NowTime))+" : "+LastText+" "+LastPath+" 用时:"+str(NowTime-LastTime)+"s\n").encode("utf-8"))
    file.close()

def OutputHtml(type,view,filter,date):
    """
    根据绘图选项生成统计图html
    type:图表类型-柱形图,饼图
    view:视图类型-日视图,周视图,月视图,总视图
    filter:筛选-10,20,30
    date:要生成视图的日期
    """
    #检验日期合法性
    if view=="日视图" or view=="周视图":
        if re.match(r"^\d{4}-\d{2}-\d{2}$",date)==None:
            win32api.MessageBox(0,"输入的日期数据格式不正确!","统计视图",win32con.MB_OK | win32con.MB_ICONEXCLAMATION | win32con.MB_TOPMOST,0)
            return -1
    elif view=="月视图":
        if re.match(r"^\d{4}-\d{2}$",date)==None:
            win32api.MessageBox(0,"输入的日期数据格式不正确!","统计视图",win32con.MB_OK | win32con.MB_ICONEXCLAMATION | win32con.MB_TOPMOST,0)
            return -1
    #判断统计文件是否存在
    if view=="日视图":
        #判断是否存在当日统计数据
        IsDataExists=os.path.exists('data/'+ date +'.txt')
        if not IsDataExists:
            win32api.MessageBox(0,"日期 "+ date + " 的统计数据不存在!","统计视图",win32con.MB_OK | win32con.MB_ICONEXCLAMATION | win32con.MB_TOPMOST,0)
            return -1
    elif view=="周视图":
        try:
            #查找周一
            InputDateTimeTuple=datetime.datetime.strptime(date,"%Y-%m-%d")
            InputTimeTuple=time.strptime(date,"%Y-%m-%d")
            MondayDelta=datetime.timedelta(days=0-calendar.weekday(InputTimeTuple[0],InputTimeTuple[1],InputTimeTuple[2]))
            MondayDateTimeTuple=InputDateTimeTuple+MondayDelta
            #循环插入列表
            DateList=[]
            Delta=datetime.timedelta(days=1)
            for i in range(7):
                CurrentDateTimeTuple=MondayDateTimeTuple.strftime("%Y-%m-%d")
                DateList.append(CurrentDateTimeTuple)
                MondayDateTimeTuple=MondayDateTimeTuple+Delta
            #检验当周的统计数据是否全不存在
            IsAllNotExists=True
            for i in DateList:
                if os.path.exists('data/'+ i +'.txt'):
                    IsAllNotExists=False
                    break
            if IsAllNotExists:
                win32api.MessageBox(0,"所选日期 "+ date + " 所属的周("+ DateList[0] + " ~ " + DateList[-1] +")无统计数据!","统计视图",win32con.MB_OK | win32con.MB_ICONEXCLAMATION | win32con.MB_TOPMOST,0)
                return -1
        except:
            win32api.MessageBox(0,"输入的日期 "+ date + " 不正确!","统计视图",win32con.MB_OK | win32con.MB_ICONEXCLAMATION | win32con.MB_TOPMOST,0)
            return -1
    elif view=="月视图":
        #检验当月的统计数据是否全不存在
        IsAllNotExists=True
        for i in range(1,32):
            if os.path.exists('data/'+ date + '-' + str(i).zfill(2) + '.txt'):
                IsAllNotExists=False
                break
        if IsAllNotExists:
            win32api.MessageBox(0,"所选月份 "+ date + " 中无统计数据!","统计视图",win32con.MB_OK | win32con.MB_ICONEXCLAMATION | win32con.MB_TOPMOST,0)
            return -1
    #读取数据
    ChartDict={}
    if view=="日视图":
        file=open('data/'+ date +'.txt','rb')
        ChartDict=eval(file.read())
        file.close()
    elif view=="周视图":
        for i in DateList:
            if os.path.exists('data/'+ i +'.txt'):
                file=open('data/'+ i +'.txt','rb')
                TempDict=eval(file.read())
                file.close()
                for j in TempDict.keys():
                    if j in ChartDict:
                        ChartDict.update({j:ChartDict[j]+TempDict[j]})
                    else:
                        ChartDict.update({j:TempDict[j]})
    elif view=="月视图":
        for i in range(1,32):
            if os.path.exists('data/'+ date + '-' + str(i).zfill(2) + '.txt'):
                file=open('data/'+ date + '-' + str(i).zfill(2) + '.txt','rb')
                TempDict=eval(file.read())
                file.close()
                for j in TempDict.keys():
                    if j in ChartDict:
                        ChartDict.update({j:ChartDict[j]+TempDict[j]})
                    else:
                        ChartDict.update({j:TempDict[j]})
    elif view=="总视图":
        global DataDict
        ChartDict=DataDict.copy()
    #排序数据
    ZippedDict=zip(ChartDict.values(),ChartDict.keys())
    SortedDataList=list(sorted(ZippedDict,key=lambda s: s[0], reverse=True))
    #标题字符串
    if view=="日视图" or view=="月视图":
        TitleStr=view + "(" + date + ") - 基于Python的电脑使用情况统计系统(Top " + str(filter) +")"
    elif view=="周视图":
        TitleStr=view + "(" + DateList[0] + " ~ " + DateList[-1] + ") - 基于Python的电脑使用情况统计系统(Top " + str(filter) +")"
    elif view=="总视图":
        TitleStr=view + " - 基于Python的电脑使用情况统计系统(Top " + str(filter) +")"
    #生成html
    if type=="柱形图":
        #筛选数据
        FilterList=reversed(SortedDataList[:filter])
        NameList=[]
        TimeList=[]
        for i in FilterList:
            NameList.append("'" + i[1][1].replace("\\","\\\\") + "'")
            TimeList.append(str(i[0]))
        #写入文件
        file=open('chart.html','wb')
        file.write(str("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="Images/Icon.ico" rel="icon" type="image/x-icon" />
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="ECharts">
<title>""" + TitleStr + """</title>
<script src="echarts.js"></script>
</head>
<body>
<div id="main" style="width: 1200px;height:""" + str(filter*60) + """px;"></div>
<script type="text/javascript">
    var myChart = echarts.init(document.getElementById('main'));
    var category = [""" + ", ".join(NameList) + """];
    var barData = [""" + ", ".join(TimeList) + """];
 
    var option = {
        title: {
				text: " """ + TitleStr + """ "
			},
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'value',
            axisLine: {
                show: false
            },
            axisTick: {
                show: false
            }
        },
        yAxis: {
            type: 'category',
            data: category,
            splitLine: {show: false},
            axisLine: {
                show: false
            },
            axisTick: {
                show: false
            },
            offset: 10,
            nameTextStyle: {
                fontSize: 15
            },
			axisLabel:{
			formatter: function (value) {
			  var maxlength=10;
			  if (value.length>maxlength) {
			      return value.substring(0, maxlength-1)+'...';
			      } else{
			      return value;
			      };
			      }
			}
        },
        series: [
            {
                name: '时间(秒)',
                type: 'bar',
                data: barData,
                barWidth: 14,
                barGap: 10,
                smooth: true,
                label: {
                    normal: {
                        show: true,
                        position: 'right',
                        offset: [5, -2],
                        textStyle: {
                            color: '#F68300',
                            fontSize: 13
                        },
					formatter: '{c} 秒'
                    }
                },
                itemStyle: {
                    emphasis: {
                        barBorderRadius: 7
                    },
                    normal: {
                        barBorderRadius: 7,
                        color: new echarts.graphic.LinearGradient(
                            0, 0, 1, 0,
                            [
                                {offset: 0, color: '#3977E6'},
                                {offset: 1, color: '#37BBF8'}
 
                            ]
                        )
                    }
                }
            }
        ]
    };
    myChart.setOption(option);
</script>
</body>
</html>""").encode("utf-8"))
        file.close()
        #显示
        win32api.ShellExecute(0,"open","Chart.exe",None,os.getcwd(),1)
    elif type=="饼图":
        #筛选数据
        FilterList=SortedDataList[:filter]
        FilterDict={}
        FilterStr=""
        for i in FilterList:
            FilterDict.update({"value":i[0],"name":i[1][1]})
            FilterStr=FilterStr+str(FilterDict)+","
        #计算其他程序时间
        OtherList=SortedDataList[filter:]
        OtherTime=0
        for i in OtherList:
            OtherTime=OtherTime+i[0]
        FilterStr=FilterStr + "{'value': " + str(OtherTime) + ", 'name': '其他'}"
        #写入文件
        file=open('chart.html','wb')
        file.write(str("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="Images/Icon.ico" rel="icon" type="image/x-icon" />
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="ECharts">
<title>""" + TitleStr + """</title>
<script src="echarts.js"></script>
</head>
<body>
<div id="main" style="width: 1200px;height: 700px;"></div>
<script type="text/javascript">
    var myChart = echarts.init(document.getElementById('main'));
 
		myChart.setOption({
			title: {
				text: " """ + TitleStr + """ "
			},
			tooltip: {
				trigger: 'item',
				formatter: "{b} <br />{a} : {c} ({d}%)"
			},
			series : [
				{
					name: "时间(秒)",
					type: "pie",
					radius: "55%",
					data:[""" + FilterStr + """],
					itemStyle: {
						emphasis: {
							shadowBlur: 200,
							shadowOffsetX: 0,
							shadowColor: 'rgba(0, 0, 0, 0.5)'
						},
						normal:{ 
							label:{ 
								show: true, 
								formatter: '{b} : {c} ({d}%)' 
							}, 
							labelLine :{show:true} 
						} 
					}
				}
			]
		})
</script>
</body>
</html>""").encode("utf-8"))
        file.close()
        #显示
        win32api.ShellExecute(0,"open","Chart.exe",None,os.getcwd(),1)
    elif type=="雷达图":
        pass
    elif type=="旭日图":
        pass

def SheetDataGUI():
    """显示数据汇总窗口"""
    global DataDict
    ShowSheetDataGUI(DataDict)

def GetRemindStatus():
    """获取超时提醒运行状态"""
    global RemindStatus,RemindPath,RemindTime,RemindType
    return (RemindStatus,RemindPath,RemindTime,RemindType)

def StartRemind(path,time,type):
    """开启超时提醒检测"""
    global RemindStatus,RemindPath,RemindTime,RemindType,RemindThread,ExitFlag
    ExitFlag=False
    RemindStatus=True
    RemindPath=path
    RemindTime=time
    RemindType=type
    RemindThread=threading.Thread(target=Remind,args=((path).lower(),time,type))
    RemindThread.start()
    
def Remind(path,ttime,type):
    """超时提醒检测"""
    global ExitFlag
    RunTime=0
    Pid=-1
    while True:
        #判断退出标志
        if ExitFlag:
            return
        #获取进程pid列表
        ProcessTuple=win32process.EnumProcesses()
        #判断是否存在已知的对应pid
        if Pid==-1:
            #不存在已知pid则遍历查找路径
            for i in ProcessTuple:
                try:
                    Handle=win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION,False,i)
                    Path=(win32process.GetModuleFileNameEx(Handle,0)).lower()
                    if Path==path:
                        Pid=i
                        RunTime=RunTime+1
                except:
                    pass
        else:
            #存在已知pid则直接查找元组
            if Pid in ProcessTuple:
                RunTime=RunTime+1
            else:
                Pid=-1
                for i in ProcessTuple:
                    try:
                        Handle=win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION,False,i)
                        Path=(win32process.GetModuleFileNameEx(Handle,0)).lower()
                        if Path==path:
                            Pid=i
                            RunTime=RunTime+1
                    except:
                        pass
        if RunTime>=ttime:
            if type=="窗口抖动":
                MeHwnd=win32gui.FindWindow("pygame","基于Python的电脑使用情况统计系统")
                win32gui.ShowWindow(MeHwnd,win32con.SW_RESTORE)
                global ShowFlag
                ShowFlag=True
                win32gui.SetWindowPos(MeHwnd,win32con.HWND_TOPMOST,0,0,0,0,win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                win32gui.SetActiveWindow(MeHwnd)
                Rect=win32gui.GetWindowRect(MeHwnd)
                for i in range(20):
                    offsetX=random.randint(-15,15)
                    offsetY=random.randint(-15,15)
                    win32gui.SetWindowPos(MeHwnd,0,Rect[0]+offsetX,Rect[1]+offsetY,0,0,win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
                    time.sleep(0.05)
                win32gui.SetWindowPos(MeHwnd,win32con.HWND_NOTOPMOST,Rect[0],Rect[1],0,0,win32con.SWP_NOSIZE)
            elif type=="结束进程":
                try:
                    Handle=win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS,False,Pid)
                    win32process.TerminateProcess(Handle,0)
                except:
                    win32api.ShellExecute(0,"open","taskkill","/f /im " + path.split("\\")[-1],os.getcwd(),0)
            elif type=="锁屏":
                ctypes.windll.user32.LockWorkStation()
            elif type=="关机":
                win32api.ShellExecute(0,"open","shutdown","-s -t 0",os.getcwd(),0)
            break
        time.sleep(1)
    StopRemind()

def StopRemind():
    """停止超时提醒检测"""
    global RemindStatus,RemindPath,RemindTime,RemindType,RemindThread,ExitFlag
    ExitFlag=True
    RemindStatus=False
    RemindPath=""
    RemindTime=0
    RemindType=""