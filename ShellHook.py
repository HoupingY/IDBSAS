import win32api,win32gui,win32con
import ctypes
from GUICallBack import GetForegroundInfo

lpPrevWndProc=0
msgShellHook=0

def StartHook(Hwnd):
    """开始窗口消息钩子"""
    global lpPrevWndProc,msgShellHook
    msgShellHook=win32api.RegisterWindowMessage("SHELLHOOK")
    ctypes.windll.user32.RegisterShellHookWindow(Hwnd)
    lpPrevWndProc=win32gui.SetWindowLong(Hwnd,win32con.GWL_WNDPROC,WindowProc)

def EndHook(Hwnd):
    """结束窗口消息钩子"""
    #还原系统消息处理
    win32api.SetWindowLong(Hwnd,win32con.GWL_WNDPROC,lpPrevWndProc)

def WindowProc(Hwnd,uMsg,wParam,lParam):
    if uMsg==msgShellHook:
        if wParam==1: #HSHELL_WINDOWCREATED
            pass
            print("钩取到窗口创建消息")
        elif wParam==2: #HSHELL_WINDOWDESTROYED
            pass
            print("钩取到窗口销毁消息")
        elif wParam==3: #HSHELL_ACTIVATESHELLWINDOW
            pass
        elif wParam==6: #HSHELL_REDRAW
            GetForegroundInfo()
            print("钩取到窗口重绘消息")
        elif wParam==32772: #ACTIVATE
            GetForegroundInfo()
            print("钩取到窗口激活消息")
        else:
            pass
    return win32gui.CallWindowProc(lpPrevWndProc,Hwnd,uMsg,wParam,lParam)