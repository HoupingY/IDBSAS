import os, sys
from tkinter import *
from tkinter.font import Font
from tkinter.ttk import *
from tkinter.messagebox import *
import threading
import win32api,win32con
from GUICallBack import GetRemindStatus,StartRemind,StopRemind
#import tkinter.filedialog as tkFileDialog
#import tkinter.simpledialog as tkSimpleDialog    #askstring()

class Tooltip:
    def __init__(self, widget, text, bg='#FFFFEA', pad=(5, 3, 5, 3), waittime=500, wraplength=300):
        self.waittime = waittime
        self.wraplength = wraplength
        self.widget = widget
        self.text = text
        self.widget.bind('<Enter>', self.onEnter)
        self.widget.bind('<Leave>', self.onLeave)
        self.widget.bind('<ButtonPress>', self.onLeave)
        self.bg = bg
        self.pad = pad
        self.id_ = None
        self.tw = None

    def onEnter(self, event=None):
        self.schedule()

    def onLeave(self, event=None):
        self.unschedule()
        self.Hide()

    def schedule(self):
        self.unschedule()
        self.id_ = self.widget.after(self.waittime, self.Show)

    def unschedule(self):
        id_ = self.id_
        self.id_ = None
        if id_:
            self.widget.after_cancel(id_)

    def Show(self):
        def tip_pos_calculator(widget, label, pad=(5, 3, 5, 3), tip_delta=(15, 10)):
            s_width, s_height = widget.winfo_screenwidth(), widget.winfo_screenheight()
            width, height = (pad[0] + label.winfo_reqwidth() + pad[2], pad[1] + label.winfo_reqheight() + pad[3])
            mouse_x, mouse_y = widget.winfo_pointerxy()
            x1, y1 = mouse_x + tip_delta[0], mouse_y + tip_delta[1]
            if x1 + width > s_width:
                x1 = mouse_x - tip_delta[0] - width
            if y1 + height > s_height - 30:
                y1 = mouse_y - tip_delta[1] - height
                if y1 < 0:
                    Y1 = 0
            return x1, y1

        self.Hide()
        self.tw = Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        label = Label(self.tw, text=self.text, justify=LEFT, background=self.bg, relief=RAISED, borderwidth=1, wraplength=self.wraplength)
        label.pack(ipadx=1)
        x, y = tip_pos_calculator(self.widget, label, self.pad)
        self.tw.wm_geometry('+%d+%d' % (x, y))

    def Hide(self):
        tw = self.tw
        if tw:
            tw.destroy()
        self.tw = None

class Remind_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Remind中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('超时提醒 - 基于Python的电脑使用情况统计系统')
        self.master.resizable(0,0)
        #窗口居中
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        x = (ws / 2) - (418 / 2)
        y = (hs / 2) - (178 / 2)
        self.master.geometry('%dx%d+%d+%d' % (418,178,x,y))
        self.createWidgets()

    def createWidgets(self):
        self.top = self.winfo_toplevel()

        self.style = Style()

        self.style.configure('TFrameMain.TLabelframe', background='#FFE0C0', font=('微软雅黑',12))
        self.style.configure('TFrameMain.TLabelframe.Label', background='#FFE0C0', font=('微软雅黑',12))
        self.FrameMain = LabelFrame(self.top, text='提醒选项', style='TFrameMain.TLabelframe')
        self.FrameMain.place(relx=0., rely=0., relwidth=0.997, relheight=0.997)

        self.LblPathVar = StringVar(value='程序路径:')
        self.style.configure('TLblPath.TLabel', anchor='w', background='#FFE0C0', font=('微软雅黑',10))
        self.LblPath = Label(self.FrameMain, text='程序路径:', textvariable=self.LblPathVar, style='TLblPath.TLabel')
        self.LblPath.setText = lambda x: self.LblPathVar.set(x)
        self.LblPath.text = lambda : self.LblPathVar.get()
        self.LblPath.place(relx=0.04, rely=0.160, relwidth=0.150, relheight=0.175)

        self.TxtPathVar = StringVar(value='')
        self.TxtPath = Entry(self.FrameMain, textvariable=self.TxtPathVar, font=('微软雅黑',10))
        self.TxtPath.setText = lambda x: self.TxtPathVar.set(x)
        self.TxtPath.text = lambda : self.TxtPathVar.get()
        self.TxtPathTooltip = Tooltip(self.TxtPath, '在此输入要提醒使用时间的程序路径')
        self.TxtPath.place(relx=0.206, rely=0.180, relwidth=0.713, relheight=0.136)

        self.LblTimeVar = StringVar(value='运行时间(秒):')
        self.style.configure('TLblTime.TLabel', anchor='w', background='#FFE0C0', font=('微软雅黑',10))
        self.LblTime = Label(self.FrameMain, text='运行时间(秒):', textvariable=self.LblTimeVar, style='TLblTime.TLabel')
        self.LblTime.setText = lambda x: self.LblTimeVar.set(x)
        self.LblTime.text = lambda : self.LblTimeVar.get()
        self.LblTime.place(relx=0.04, rely=0.460, relwidth=0.200, relheight=0.175)

        self.TxtTimeVar = StringVar(value='')
        self.TxtTime = Entry(self.FrameMain, textvariable=self.TxtTimeVar, font=('微软雅黑',10))
        self.TxtTime.setText = lambda x: self.TxtTimeVar.set(x)
        self.TxtTime.text = lambda : self.TxtTimeVar.get()
        self.TxtTimeTooltip = Tooltip(self.TxtTime, '在此输入点击下方的开始按钮后\n指定的程序运行多少秒后进行提醒')
        self.TxtTime.place(relx=0.245, rely=0.490, relwidth=0.20, relheight=0.136)

        self.LblTypeVar = StringVar(value='提醒方式:')
        self.style.configure('TLblType.TLabel', anchor='w', background='#FFE0C0', font=('微软雅黑',10))
        self.LblType = Label(self.FrameMain, text='提醒方式:', textvariable=self.LblTypeVar, style='TLblType.TLabel')
        self.LblType.setText = lambda x: self.LblTypeVar.set(x)
        self.LblType.text = lambda : self.LblTypeVar.get()
        self.LblType.place(relx=0.485, rely=0.460, relwidth=0.150, relheight=0.175)

        self.ComboTypeList = ['窗口抖动','结束进程','锁屏','关机']
        self.ComboTypeVar = StringVar(value='窗口抖动')
        self.ComboType = Combobox(self.FrameMain, state='readonly', text='窗口抖动', textvariable=self.ComboTypeVar, values=self.ComboTypeList, font=('微软雅黑',10))
        self.ComboType.setText = lambda x: self.ComboTypeVar.set(x)
        self.ComboType.text = lambda : self.ComboTypeVar.get()
        self.ComboType.place(relx=0.650, rely=0.475, relwidth=0.27)

        self.CmdSubmitVar = StringVar(value=' 开始！')
        self.style.configure('TCmdSubmit.TButton', background='#FFC0C0', font=('微软雅黑',12))
        self.CmdSubmit = Button(self.FrameMain, text=' 开始！', textvariable=self.CmdSubmitVar, command=self.CmdSubmit_Cmd, style='TCmdSubmit.TButton')
        self.CmdSubmit.setText = lambda x: self.CmdSubmitVar.set(x)
        self.CmdSubmit.text = lambda : self.CmdSubmitVar.get()
        self.CmdSubmit.place(relx=0.378, rely=0.70, relwidth=0.196, relheight=0.240)


class Remind(Remind_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Remind_ui中。
    def __init__(self, master=None):
        Remind_ui.__init__(self, master)
        #获取当前提醒状态
        self.RemindData=GetRemindStatus()
        #根据状态显示到窗口
        if self.RemindData[0]==True:
            self.TxtPath.config(state=DISABLED)
            self.TxtTime.config(state=DISABLED)
            self.ComboType.config(state=DISABLED)
            self.CmdSubmit.setText(" 取消！")
            self.TxtPath.setText(self.RemindData[1])
            self.TxtTime.setText(str(self.RemindData[2]))
            self.ComboType.setText(self.RemindData[3])

    def CmdSubmit_Cmd(self, event=None):
        #判断按钮文本
        if self.CmdSubmit.text()==" 开始！":
            #检测输入的程序路径是否存在
            IsPathExists=os.path.exists(self.TxtPath.text())
            if not IsPathExists:
                win32api.MessageBox(0,"输入的程序路径不存在!","超时提醒",win32con.MB_OK | win32con.MB_ICONEXCLAMATION | win32con.MB_TOPMOST,0)
                return -1
            #检测输入的时间是否合法
            if (not (self.TxtTime.text().isdecimal()) or int(self.TxtTime.text())<0):
                win32api.MessageBox(0,"输入的时间不合法!","超时提醒",win32con.MB_OK | win32con.MB_ICONEXCLAMATION | win32con.MB_TOPMOST,0)
                return -1
            #禁用输入
            self.TxtPath.config(state=DISABLED)
            self.TxtTime.config(state=DISABLED)
            self.ComboType.config(state=DISABLED)
            #更改按钮文本
            self.CmdSubmit.setText(" 取消！")
            #开启超时提醒
            StartRemind(self.TxtPath.text(),int(self.TxtTime.text()),self.ComboType.text())
        else:
            #获取当前提醒状态
            self.RemindData=GetRemindStatus()
            if self.RemindData[0]==True:
                #停止线程
                StopRemind()
            #启用输入
            self.TxtPath.config(state=NORMAL)
            self.TxtTime.config(state=NORMAL)
            self.ComboType.config(state=NORMAL)
            #更改按钮文本
            self.CmdSubmit.setText(" 开始！")

def ShowRemindGUI():
    #初始化
    top = Tk()
    #加载窗口图标
    top.iconbitmap("Images/Icon.ico")
    Remind(top).mainloop()
    top.quit()