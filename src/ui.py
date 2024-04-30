import tkinter
import time
from tkinter import ttk
from tkinter import font
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
import numpy as np

L2_TOTAL_SIZE = 32 * 1024 * 1024
L1_TOTAL_SIZE = 3 * 1024 * 1024


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, tag, text='unknown addr'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.tag_bind(tag, "<Enter>", self.enter)
        self.widget.tag_bind(tag, "<Leave>", self.leave)
        self.widget.tag_bind(tag, "<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


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


class UI:
    def __init__(self, recorder):
        self.recorder = recorder
        # self.l2_s = l2_scratch
        # self.l2_b = l2_buffer
        # self.l1_a = l1_all
        self.top = tkinter.Tk()
        self.top.title("L1/L2 Addr Analyzer")
        # top.geometry("700x400")

        # width, height = 600, 600
        g_screenwidth = self.top.winfo_screenwidth()
        g_screenheight = self.top.winfo_screenheight()
        # alignstr = '%dx%d+%d+%d' % (width, height, (g_screenwidth - width) / 2, (g_screenheight - height) / 2)
        # self.top.geometry(alignstr)

        self.main_page = Frame(self.top)
        self.create_main_page()

        self.top.mainloop()

    def make_frame_mid(self, frame):
        # ========= canvas ============
        length = 750
        left = 65
        s = self.top.winfo_screenheight() / 800 if self.top.winfo_screenheight() < 800 else 1
        l2_canvas = Canvas(frame, bd=2, bg='#ccc', height=s*150, width=length)
        l2_canvas.place(x=left, y=s*20)
        Label(frame, text="0").place(x=left, y=s*180)
        Label(frame, text="32M").place(x=800, y=s*180)
        Label(frame, text="L2").place(x=25, y=s*95)

        l1_canvas = Canvas(frame, bd=2, bg='#ccc', height=s*150, width=length)
        l1_canvas.place(x=left, y=s*210)
        Label(frame, text="0").place(x=left, y=s*370)
        Label(frame, text="3M").place(x=800, y=s*370)
        Label(frame, text="L1").place(x=25, y=s*285)

        cost_canvas = Canvas(frame, bd=2, bg='#ccc', height=s*250, width=length)
        cost_canvas.place(x=left, y=s*400)
        streams = ["L3>>L3", "L3>>L2", "L2>>L3", "L2>>L2", "L3>>L1", "L2>>L1", "Workload", "L1>>L1", "L1>>L2"]
        colors = ["#66FF99", "#4DA041", "#4DA041", "#A99087", "#4DA041", "#B4AEF4", "#B1B8B2", "#A99087", "#A99087"]
        stream_idx = {stream: i for i, stream in enumerate(streams)}
        for i, stream in enumerate(streams):
            Label(frame, text=stream).place(x=0, y=s*400+s*30*i)

        Label(frame, text="cycle_time =").place(x=45, y=s*725)
        cycle_time = Label(frame, text="")
        cycle_time.place(x=125, y=s*725)

        # ========= slice  ============
        def change_l2():
            l2_canvas.delete('all')
            l2_canvas.clipboard_clear()
            t = stamp.get()
            frags = self.recorder.states[t].L2_frags
            for frag in frags:
                left = int(length * frag.addr / L2_TOTAL_SIZE)
                right = int(length * (frag.addr + frag.size) / L2_TOTAL_SIZE)
                block = l2_canvas.create_rectangle(left, 0, right, s*150, fill='purple')
                # l2_canvas.tag_bind(block, "<Enter>", show_addr)
                block_tip = CreateToolTip(l2_canvas, block, text="{}\n{} - {}".format(frag.node, frag.addr, frag.addr + frag.size))

        def change_l1():
            l1_canvas.delete('all')
            l1_canvas.clipboard_clear()
            t = stamp.get()
            frags = self.recorder.states[t].L1_frags
            for frag in frags:
                left = int(length * frag.addr / L1_TOTAL_SIZE)
                right = int(length * (frag.addr + frag.size) / L1_TOTAL_SIZE)
                block = l1_canvas.create_rectangle(left, 0, right, s*150, fill='green')
                # l1_canvas.tag_bind(block, "<Enter>", show_addr)
                block_tip = CreateToolTip(l1_canvas, block, text="{}\n{} - {}".format(frag.node, frag.addr, frag.addr + frag.size))

        def change_cost():
            cost_canvas.delete('all')
            cost_canvas.clipboard_clear()
            time_line = cost_canvas.create_line(length / 2, 0, length / 2, s*250, fill='gray', dash=(4, 4))
            t = stamp.get()
            scale = time_scale.get()
            time = self.recorder.time_stamp[t]
            time_interval = [time - 100 * 2**scale, time + 100 * 2**scale]
            stamp_begin = max(0, upper_bound(self.recorder.time_stamp, time_interval[0]) - 1)
            stamp_end = upper_bound(self.recorder.time_stamp, time_interval[1])

            task_set = set()
            for t in range(stamp_begin, stamp_end):
                tasks = self.recorder.states[t].tasks
                for task in tasks:
                    if task.node in task_set:
                        continue
                    task_set.add(task.node)
                    left = int(length * (task.start - time_interval[0]) / (time_interval[1] - time_interval[0]))
                    right = int(length * (task.end - time_interval[0]) / (time_interval[1] - time_interval[0]))
                    top = int(s*30 * stream_idx[task.stream])
                    down = top + 23
                    block = cost_canvas.create_rectangle(left, top, right, down, fill=colors[stream_idx[task.stream]])
                    block_tip = CreateToolTip(cost_canvas, block,
                                              text="{}\ncycle: {} - {}".format(task.node, task.start, task.end))

        def change_time(arg):
            if not self.recorder.recs:
                print("sss")
                return
            change_l2()
            change_l1()
            change_cost()
            cycle_time.config(text=str(self.recorder.time_stamp[stamp.get()]))

        stamp = IntVar()
        time_scale = IntVar()
        self.stamp_scale = Scale(frame, activebackground="green", from_=0, to=len(self.recorder.states) - 1,
                            resolution=1, orient=HORIZONTAL, tickinterval=0, length=330, width=20,
                            command=change_time, variable=stamp)
        self.stamp_scale.set(0)
        self.stamp_scale.place(x=left, y=s*670, width=length)
        interval_scale = Scale(frame, activebackground="green", from_=0, to=12, variable=time_scale,
                               resolution=1, orient=VERTICAL, tickinterval=0, length=s*100, width=20,
                               command=change_time)
        interval_scale.set(0)
        interval_scale.place(x=820, y=s*660)
        Label(frame, text="scale").place(x=800, y=s*750)

    def create_main_page(self):
        self.main_page.grid(row=0, column=0, sticky="nsew")
        menu = Menu(self.main_page)

        def open_csv():
            initdir = "./"
            file_path = askopenfilename(filetypes=[('DAT', '*.csv')], initialdir=initdir)
            if file_path:
                self.recorder.run(file_path)
                self.stamp_scale.config(to=len(self.recorder.states) - 1)

        submenu = Menu(menu, tearoff=0)  # 生成下拉菜单
        submenu.add_command(label="打开", command=open_csv)
        submenu.add_command(label="退出", command=self.top.quit)
        menu.add_cascade(label="File", menu=submenu)
        self.top.config(menu=menu)

        frame_mid = Frame(self.main_page)
        frame_mid.pack()
        frame_mid.config(width=900, height=800)
        # v = Scrollbar(frame_mid)
        # v.place(x=800, y=0)

        self.make_frame_mid(frame_mid)

        

if __name__ == "__main__":
    ui = UI()

