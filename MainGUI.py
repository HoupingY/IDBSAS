import win32api,win32gui,win32con
import pygame
import sys
import os
import threading
from GUICallBack import *
from ShellHook import *
from ChartOptionGUI import *
from SheetGUI import *
from RemindGUI import *

def GuiInit():
    #初始化pygame
    pygame.init()
    #获取屏幕逻辑宽度与高度
    DesktopHwnd=win32gui.GetDesktopWindow()
    MonitorHwnd=win32api.MonitorFromWindow(DesktopHwnd,win32con.MONITOR_DEFAULTTONEAREST)
    ScreenWidth=win32api.GetMonitorInfo(MonitorHwnd)["Monitor"][2]
    ScreenHeight=win32api.GetMonitorInfo(MonitorHwnd)["Monitor"][3]
    #初始化窗口
    WindowWidth=1080
    WindowHeight=661
    Window = pygame.display.set_mode((WindowWidth,WindowHeight),pygame.NOFRAME)
    pygame.display.set_caption("基于Python的电脑使用情况统计系统")
    pygame.display.set_icon(pygame.image.load("Images/Icon.ico"))
    #获得窗口句柄
    MeHwnd=pygame.display.get_wm_info()["window"]
    #隐藏窗口
    win32gui.ShowWindow(MeHwnd,win32con.SW_HIDE)
    #绘制窗口背景
    BackgroundImage=pygame.image.load("Images/Back.jpg")
    Window.blit(BackgroundImage,[0,0])
    pygame.display.flip()
    #窗口居中
    win32gui.SetWindowPos(MeHwnd,0,int((ScreenWidth-WindowWidth)/2),int((ScreenHeight-WindowHeight)/2),WindowWidth,WindowHeight,win32con.SWP_NOZORDER | win32con.SWP_NOSIZE)
    #窗口圆角
    RoundRegion=win32gui.CreateRoundRectRgn(0, 0, WindowWidth, WindowHeight, 60, 60)
    win32gui.SetWindowRgn(MeHwnd, RoundRegion, True)
    #设置透明度1
    win32gui.SetWindowLong(MeHwnd,win32con.GWL_EXSTYLE,win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(MeHwnd,0,1,win32con.LWA_ALPHA)
    #显示窗口
    win32gui.ShowWindow(MeHwnd,win32con.SW_SHOW)
    #淡入
    for i in range(1,241):
        win32gui.SetLayeredWindowAttributes(MeHwnd,0,i,win32con.LWA_ALPHA)
        pygame.display.flip()
        pygame.time.delay(4)
    #初始化信息
    GetForegroundInfo(MeHwnd,1)
    #开启检测今日是否结束线程
    tDayEnd=threading._start_new_thread(IsDayEnd,())
    #开启窗口消息钩子
    StartHook(MeHwnd)


    while True:
        #鼠标光标
        try:
            CurX,CurY=win32api.GetCursorPos()
        except:
            CurX,CurY=(0,0)
        WindowX,WindowY,WindowW,WindowH=win32gui.GetWindowRect(MeHwnd)
        if WindowX<CurX<WindowX+WindowW and WindowY<CurY<WindowY+WindowH:
            IsInWindow=True
            while win32api.ShowCursor(False)>=0:
                win32api.ShowCursor(False)
        else:
            IsInWindow=False
            while win32api.ShowCursor(True)<0:
                win32api.ShowCursor(True)
        #遍历所有事件
        for event in pygame.event.get():
            #退出事件
            if event.type == pygame.QUIT:
                while win32api.ShowCursor(True)<0:
                    win32api.ShowCursor(True)
                if win32api.MessageBox(0,"确定要退出系统吗?","提示",win32con.MB_OKCANCEL | win32con.MB_ICONQUESTION | win32con.MB_TOPMOST)==1:
                    GetForegroundInfo(MeHwnd,2)
                    EndHook(MeHwnd)
                    FadeOut(MeHwnd)
                    return 1
            #鼠标按下事件
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button==1:
                    if True in BtnStatus:
                        #数据汇总
                        if BtnStatus.index(True)==0:
                            win32gui.EnableWindow(MeHwnd,False)
                            while win32api.ShowCursor(True)<0:
                                win32api.ShowCursor(True)
                            SheetDataGUI()
                            win32gui.EnableWindow(MeHwnd,True)
                        #今日数据
                        elif BtnStatus.index(True)==1:
                            win32gui.EnableWindow(MeHwnd,False)
                            while win32api.ShowCursor(True)<0:
                                win32api.ShowCursor(True)
                            ShowSheetLogGUI()
                            win32gui.EnableWindow(MeHwnd,True)
                        #统计视图
                        elif BtnStatus.index(True)==2:
                            win32gui.EnableWindow(MeHwnd,False)
                            while win32api.ShowCursor(True)<0:
                                win32api.ShowCursor(True)
                            ShowChartOptionGUI()
                            win32gui.EnableWindow(MeHwnd,True)
                        #隐藏窗口
                        elif BtnStatus.index(True)==3:
                            while win32api.ShowCursor(True)<0:
                                win32api.ShowCursor(True)
                            win32api.MessageBox(0,"提示:按下Ctrl+F10可以重新显示窗口","隐藏窗口",win32con.MB_OK | win32con.MB_ICONINFORMATION | win32con.MB_TOPMOST,0)
                            tShowWindow=threading._start_new_thread(HotKeyShowWindow,(MeHwnd,))
                        #超时提醒
                        elif BtnStatus.index(True)==4:
                            win32gui.EnableWindow(MeHwnd,False)
                            while win32api.ShowCursor(True)<0:
                                win32api.ShowCursor(True)
                            ShowRemindGUI()
                            win32gui.EnableWindow(MeHwnd,True)
                        #最小化
                        elif BtnStatus.index(True)==6:
                            win32gui.ShowWindow(MeHwnd,win32con.SW_MINIMIZE)
                        #退出系统
                        elif BtnStatus.index(True)==5 or BtnStatus.index(True)==7:
                            while win32api.ShowCursor(True)<0:
                                win32api.ShowCursor(True)
                            if win32api.MessageBox(0,"确定要退出系统吗?","提示",win32con.MB_OKCANCEL | win32con.MB_ICONQUESTION | win32con.MB_TOPMOST)==1:
                                GetForegroundInfo(MeHwnd,2)
                                EndHook(MeHwnd)
                                FadeOut(MeHwnd)
                                return 1
                    #窗口拖动
                    else:
                        win32gui.ReleaseCapture()
                        win32gui.SendMessage(MeHwnd, win32con.WM_NCLBUTTONDOWN, win32con.HTCAPTION, 0)
            #鼠标移动事件
            elif event.type==pygame.MOUSEMOTION:
                MouseMoveCheckButton(event.pos[0],event.pos[1])
                CurrentX=event.pos[0]
                CurrentY=event.pos[1]
            #其他事件
            else:
                pass
        #绘制窗口
        Window.blit(BackgroundImage,[0,0])
        for i in range(8):
            if BtnStatus[i]:Window.blit(BtnPng[i],BtnPos[i])
        if IsInWindow:
            if True in BtnStatus:
                Window.blit(CurHand,[CurrentX,CurrentY])
            else:
                Window.blit(CurArrow,[CurrentX,CurrentY])
        pygame.display.flip()

if __name__ == '__main__':
    try:
        while True:
            r=GuiInit()
            if r==1:
                break
        sys.exit(0)
    except SystemExit as e:
        if str(e) == '0':
            sys.exit(0)