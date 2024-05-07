from tkinter import Toplevel, Label


def upper_bound(nums, target):
    low, high = 0, len(nums) - 1
    pos = len(nums)
    while low < high:
        mid = (low + high) // 2
        if nums[mid] <= target:
            low = mid + 1
        else:
            high = mid
            pos = high
    if nums[low] > target:
        pos = low
    return pos


class ToolTip:
    # 针对指定的 widget 创建一个 tooltip

    def __init__(self, widget, text, tag=None, timeout=500, offset=(0, -20)):
        '''
        参数
        =======
        widget: tkinter 小部件
        text: (str) tooltip 的文本信息
        timeout: 鼠标必须悬停 timeout 毫秒，才会显示 tooltip
        '''
        # 设置 用户参数
        self.widget = widget
        self.text = text
        self.timeout = timeout
        self.offset = offset
        # 内部参数初始化
        self._init_params()
        # 绑定事件
        if tag:
            self.widget.tag_bind(tag, "<Enter>", self.enter)
            self.widget.tag_bind(tag, "<Leave>", self.leave)
            self.widget.tag_bind(tag, "<ButtonPress>", self.leave)
        else:
            self.widget.bind("<Enter>", self.enter)
            self.widget.bind("<Leave>", self.leave)
            self.widget.bind("<ButtonPress>", self.leave)

    def _init_params(self):
        '''内部参数的初始化'''
        self.id_after = None
        self.x, self.y = 0, 0
        self.tipwindow = None
        self.background = 'lightyellow'

    def cursor(self, event):
        '''设定 鼠标光标的位置坐标 (x,y)'''
        self.x = event.x
        self.y = event.y

    def unschedule(self):
        '''取消用于鼠标悬停时间的计时器'''
        if self.id_after:
            self.widget.after_cancel(self.id_after)
        else:
            self.id_after = None

    def tip_window(self):
        window = Toplevel(self.widget)
        # 设置窗体属性
        # 隐藏窗体的标题、状态栏等
        window.overrideredirect(True)
        # 保持在主窗口的上面
        window.attributes("-toolwindow", 1)  # 也可以使用 `-topmost`
        window.attributes("-alpha", 0.92857142857)  # 设置透明度为 13/14
        x = self.widget.winfo_rootx() + self.x + self.offset[0]
        y = self.widget.winfo_rooty() + self.y + self.offset[1]
        window.wm_geometry("+%d+%d" % (x, y))
        return window

    def showtip(self):
        """
        创建一个带有工具提示文本的 topoltip 窗口
        """
        params = {
            'text': self.text,
            'justify': 'left',
            'background': self.background,
            'relief': 'solid',
            'borderwidth': 1
        }
        self.tipwindow = self.tip_window()
        label = Label(self.tipwindow, **params)
        label.grid(sticky='nsew')

    def schedule(self):
        """
        安排计时器以计时鼠标悬停的时间
        """
        self.id_after = self.widget.after(self.timeout, self.showtip)

    def enter(self, event):
        """
        鼠标进入 widget 的回调函数

        参数
        =========
        :event:  来自于 tkinter，有鼠标的 x,y 坐标属性
        """
        self.cursor(event)
        self.schedule()

    def hidetip(self):
        """
        销毁 tooltip window
        """
        if self.tipwindow:
            self.tipwindow.destroy()
        else:
            self.tipwindow = None

    def leave(self, event):
        """
        鼠标离开 widget 的销毁 tooltip window

        参数
        =========
        :event:  来自于 tkinter，没有被使用
        """
        self.unschedule()
        self.hidetip()
