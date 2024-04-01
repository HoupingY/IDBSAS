from tkinter import *
from tkinter import ttk
import time
import re

def ShowSheetDataGUI(DataDict):
    #初始化
    top = Tk()
    #窗口标题
    top.title('数据汇总 - 基于Python的电脑使用情况统计系统')
    #加载窗口图标
    top.iconbitmap("Images/Icon.ico")
    # 窗口居中
    ws = top.winfo_screenwidth()
    hs = top.winfo_screenheight()
    x = (ws / 2) - (1125 / 2)
    y = (hs / 2) - (600 / 2)
    top.geometry('%dx%d+%d+%d' % (1125,600,x,y))
    #禁止窗口改变大小
    top.resizable(0,0)

    #表格
    columns = ("时长(秒)", "窗口标题", "进程路径")
    treeview = ttk.Treeview(top, height=18, show="headings", columns=columns)  
    #表示列,不显示
    treeview.column("时长(秒)", width=100, anchor='center') 
    treeview.column("窗口标题", width=500, anchor='center')
    treeview.column("进程路径", width=500, anchor='center')
    #显示表头
    treeview.heading("时长(秒)", text="时长(秒)") 
    treeview.heading("窗口标题", text="窗口标题")
    treeview.heading("进程路径", text="进程路径")
    #添加进窗体
    treeview.pack(side=LEFT, fill=BOTH)
    #添加数据
    SheetDict=DataDict.copy()
    ZippedDict=zip(SheetDict.values(),SheetDict.keys())
    SortedDataList=list(sorted(ZippedDict,key=lambda s: s[0], reverse=True))
    count=1
    for i in SortedDataList:
        treeview.insert("",count,values=(i[0],i[1][1],i[1][0]))
        count=count+1
    #添加滚动条
    VScroll = Scrollbar(top, orient='vertical', command=treeview.yview)
    VScroll.place(relx=0.980, rely=0.0, relwidth=0.020, relheight=1.0)
    treeview.configure(yscrollcommand=VScroll.set)
    #运行
    top.mainloop()
    top.quit()

def ShowSheetLogGUI():
    #初始化
    top = Tk()
    #窗口标题
    top.title('今日数据 - 基于Python的电脑使用情况统计系统')
    #加载窗口图标
    top.iconbitmap("Images/Icon.ico")
    # 窗口居中
    ws = top.winfo_screenwidth()
    hs = top.winfo_screenheight()
    x = (ws / 2) - (1250 / 2)
    y = (hs / 2) - (600 / 2)
    top.geometry('%dx%d+%d+%d' % (1250,600,x,y))
    #禁止窗口改变大小
    top.resizable(0,0)

    #表格
    columns = ("时间", "时长(秒)", "窗口标题", "进程路径")
    treeview = ttk.Treeview(top, height=18, show="headings", columns=columns)  
    #表示列,不显示
    treeview.column("时间", width=150, anchor='center') 
    treeview.column("时长(秒)", width=100, anchor='center') 
    treeview.column("窗口标题", width=500, anchor='center')
    treeview.column("进程路径", width=500, anchor='center')
    #显示表头
    treeview.heading("时间", text="时间")
    treeview.heading("时长(秒)", text="时长(秒)") 
    treeview.heading("窗口标题", text="窗口标题")
    treeview.heading("进程路径", text="进程路径")
    #添加进窗体
    treeview.pack(side=LEFT, fill=BOTH)
    #添加数据
    file=open('log/'+time.strftime("%Y-%m-%d", time.localtime())+'.txt','rb')
    TodayLog=file.readlines()
    file.close()
    count=1
    for i in TodayLog:
        Detail=i.decode("utf-8")
        Time=(re.search(r"^\d{2}:\d{2}:\d{2} - \d{2}:\d{2}:\d{2}",Detail).group()).replace(" ","")
        Name=(re.search(r": (.*) [C-Z]:\\",Detail).group())[2:-4]
        Path=(re.search(r" [C-Z]:\\.*用时",Detail).group())[1:-3]
        Long=(re.search(r"用时:\d*",Detail).group())[3:]
        treeview.insert("",count,values=(Time,Long,Name,Path))
        count=count+1
    #添加滚动条
    VScroll = Scrollbar(top, orient='vertical', command=treeview.yview)
    VScroll.place(relx=0.980, rely=0.0, relwidth=0.020, relheight=1.0)
    treeview.configure(yscrollcommand=VScroll.set)
    #运行
    top.mainloop()
    top.quit()