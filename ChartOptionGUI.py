import os, sys
import time
import calendar
import datetime
from tkinter import *
from tkinter.font import Font
from tkinter.ttk import *
from tkinter.messagebox import *
from GUICallBack import OutputHtml
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

class ChartOption_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类ChartOption_callback中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('绘图选项 - 基于Python的电脑使用情况统计系统')
        self.master.resizable(0,0)
        # 窗口居中
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        x = (ws / 2) - (426 / 2)
        y = (hs / 2) - (180 / 2)
        self.master.geometry('%dx%d+%d+%d' % (426,180,x,y))
        self.createWidgets()

    def createWidgets(self):
        self.top = self.winfo_toplevel()

        self.style = Style()

        self.style.configure('TFrameMain.TLabelframe', background='#FFE0C0', font=('微软雅黑',12))
        self.style.configure('TFrameMain.TLabelframe.Label', background='#FFE0C0', font=('微软雅黑',12))
        self.FrameMain = LabelFrame(self.top, text='绘图选项', style='TFrameMain.TLabelframe')
        self.FrameMain.place(relx=0., rely=0., relwidth=0.997, relheight=0.997)

        self.LblTypeVar = StringVar(value='图表类型:')
        self.style.configure('TLblType.TLabel', anchor='w', background='#FFE0C0', font=('微软雅黑',10))
        self.LblType = Label(self.FrameMain, text='图表类型:', textvariable=self.LblTypeVar, style='TLblType.TLabel')
        self.LblType.setText = lambda x: self.LblTypeVar.set(x)
        self.LblType.text = lambda : self.LblTypeVar.get()
        self.LblType.place(relx=0.04, rely=0.160, relwidth=0.150, relheight=0.175)

        self.LblViewVar = StringVar(value='视图类型:')
        self.style.configure('TLblView.TLabel', anchor='w', background='#FFE0C0', font=('微软雅黑',10))
        self.LblView = Label(self.FrameMain, text='视图类型:', textvariable=self.LblViewVar, style='TLblView.TLabel')
        self.LblView.setText = lambda x: self.LblViewVar.set(x)
        self.LblView.text = lambda : self.LblViewVar.get()
        self.LblView.place(relx=0.04, rely=0.480, relwidth=0.150, relheight=0.175)

        self.LblFilterVar = StringVar(value='筛选:')
        self.style.configure('TLblFilter.TLabel', anchor='w', background='#FFE0C0', font=('微软雅黑',10))
        self.LblFilter = Label(self.FrameMain, text='筛选:', textvariable=self.LblFilterVar, style='TLblFilter.TLabel')
        self.LblFilter.setText = lambda x: self.LblFilterVar.set(x)
        self.LblFilter.text = lambda : self.LblFilterVar.get()
        self.LblFilter.place(relx=0.558, rely=0.160, relwidth=0.090, relheight=0.175)

        self.LblDateVar = StringVar(value='数据:')
        self.style.configure('TLblDate.TLabel', anchor='w', background='#FFE0C0', font=('微软雅黑',10))
        self.LblDate = Label(self.FrameMain, text='数据:', textvariable=self.LblDateVar, style='TLblDate.TLabel')
        self.LblDate.setText = lambda x: self.LblDateVar.set(x)
        self.LblDate.text = lambda : self.LblDateVar.get()
        self.LblDate.place(relx=0.558, rely=0.480, relwidth=0.090, relheight=0.175)

        self.ComboTypeList = ['柱形图','饼图']
        self.ComboTypeVar = StringVar(value='柱形图')
        self.ComboType = Combobox(self.FrameMain, state='readonly', text='柱形图', textvariable=self.ComboTypeVar, values=self.ComboTypeList, font=('微软雅黑',10))
        self.ComboType.setText = lambda x: self.ComboTypeVar.set(x)
        self.ComboType.text = lambda : self.ComboTypeVar.get()
        self.ComboType.place(relx=0.196, rely=0.150, relwidth=0.267)

        self.ComboViewList = ['日视图','周视图','月视图','总视图']
        self.ComboViewVar = StringVar(value='日视图')
        self.ComboView = Combobox(self.FrameMain, state='readonly', text='日视图', textvariable=self.ComboViewVar, values=self.ComboViewList, font=('微软雅黑',10))
        self.ComboView.setText = lambda x: self.ComboViewVar.set(x)
        self.ComboView.text = lambda : self.ComboViewVar.get()
        self.ComboView.place(relx=0.196, rely=0.470, relwidth=0.267)
        self.ComboViewVar.trace('w', self.ComboView_Change)

        self.ComboFilterList = ['前10','前20','前30']
        self.ComboFilterVar = StringVar(value='前10')
        self.ComboFilter = Combobox(self.FrameMain, state='readonly', text='前10', textvariable=self.ComboFilterVar, values=self.ComboFilterList, font=('微软雅黑',10))
        self.ComboFilter.setText = lambda x: self.ComboFilterVar.set(x)
        self.ComboFilter.text = lambda : self.ComboFilterVar.get()
        self.ComboFilter.place(relx=0.650, rely=0.150, relwidth=0.267)

        self.TextDateVar = StringVar(value=time.strftime("%Y-%m-%d", time.localtime()))
        self.TextDate = Entry(self.FrameMain, textvariable=self.TextDateVar, font=('微软雅黑',10))
        self.TextDate.setText = lambda x: self.TextDateVar.set(x)
        self.TextDate.text = lambda : self.TextDateVar.get()
        self.TextDateTooltip = Tooltip(self.TextDate, '日视图请按照YYYY-MM-DD格式指定日期\n周视图请按照YYYY-MM-DD格式指定日期，程序会自动匹配指定日期所属星期\n月视图请按照YYYY-MM格式指定月份')
        self.TextDate.place(relx=0.650, rely=0.470, relwidth=0.267)

        self.CmdSubmitVar = StringVar(value=' 生成！')
        self.style.configure('TCmdSubmit.TButton', background='#FFC0C0', font=('微软雅黑',12))
        self.CmdSubmit = Button(self.FrameMain, text=' 生成！', textvariable=self.CmdSubmitVar, command=self.CmdSubmit_Cmd, style='TCmdSubmit.TButton')
        self.CmdSubmit.setText = lambda x: self.CmdSubmitVar.set(x)
        self.CmdSubmit.text = lambda : self.CmdSubmitVar.get()
        self.CmdSubmit.place(relx=0.378, rely=0.70, relwidth=0.196, relheight=0.240)

class ChartOption_callback(ChartOption_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在ChartOption_ui中。
    def __init__(self, master=None):
        ChartOption_ui.__init__(self, master)

    def ComboView_Change(self, *args):
        #视图类型被更改时同步更改日期数据
        if self.ComboView.text()=="日视图":
            self.TextDate.config(state=NORMAL)
            self.TextDate.setText(time.strftime("%Y-%m-%d", time.localtime()))
        elif self.ComboView.text()=="周视图":
            self.TextDate.config(state=NORMAL)
            NowTuple=time.localtime()
            Now=datetime.datetime.now()
            Delta=datetime.timedelta(days=0-calendar.weekday(NowTuple[0],NowTuple[1],NowTuple[2]))
            Date=Now+Delta
            self.TextDate.setText(Date.strftime("%Y-%m-%d"))
        elif self.ComboView.text()=="月视图":
            self.TextDate.config(state=NORMAL)
            self.TextDate.setText(time.strftime("%Y-%m", time.localtime()))
        elif self.ComboView.text()=="总视图":
            self.TextDate.config(state=DISABLED)
            self.TextDate.setText("")

    def CmdSubmit_Cmd(self, event=None):
        #根据本地数据生成html
        Result=OutputHtml(self.ComboType.text(),self.ComboView.text(),int((self.ComboFilter.text())[1:]),self.TextDate.text())
        if Result!=-1:
            self.master.destroy()

def ShowChartOptionGUI():
    #初始化
    top = Tk()
    #加载窗口图标
    top.iconbitmap("Images/Icon.ico")
    ChartOption_callback(top).mainloop()
    top.quit()