import tkinter
from tkinter import ttk
from tkinter import messagebox
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
import numpy as np
from utils import *

L2_TOTAL_SIZE = 32 * 1024 * 1024
L1_TOTAL_SIZE = 6 * 1024 * 1024


class UI:
    def __init__(self, recorder):
        self.recorder = recorder
        self.top = tkinter.Tk()
        self.top.title("L1/L2 Addr Analyzer ver1.6")
        # top.geometry("700x400")
        self.width = 1400
        self.height = 800

        self.main_page = Frame(self.top)
        self.create_main_page()

        self.top.mainloop()

    def general_feedback(self, title, str1):
        messagebox.showinfo(title, str1)

    def show_frags(self, buffer, t):
        table = Tk()
        table.title("{}地址占用表(cycle={}时刻)".format(buffer, self.recorder.time_stamp[t]))

        scrollbar = Scrollbar(table)
        scrollbar.pack(side=RIGHT, fill=Y)

        columns = ("op_name", "core_id", "addr", "size")
        treeview = ttk.Treeview(table, height=20, show="headings", columns=columns, yscrollcommand=scrollbar.set)  # 表格

        treeview.column("op_name", width=400, anchor='w')
        treeview.column("core_id", width=50, anchor='center')
        treeview.column("addr", width=100, anchor='center')
        treeview.column("size", width=100, anchor='center')

        treeview.heading("op_name", text="op_name")
        treeview.heading("core_id", text="core_id")
        treeview.heading("addr", text="addr")
        treeview.heading("size", text="size")

        treeview.pack(side=TOP, fill=BOTH)
        scrollbar.config(command=treeview.yview)

        def fill_tabel():
            frags = self.recorder.states[t].L1_frags if buffer == "L1" else self.recorder.states[t].L2_frags
            frags = sorted(frags, key=lambda x: x.addr)
            for i in range(len(frags)):
                treeview.insert('', i, values=(frags[i].op_name, frags[i].core_id, frags[i].addr, frags[i].size))

        fill_tabel()

    def make_frame_mid(self, frame):
        # ========= canvas ============
        length = self.width - 150
        left = 65
        s = self.height / 800
        style = ttk.Style(frame)
        style.configure('lefttab.TNotebook', tabposition='ws')

        # ========= l2 frame ============
        l2_frame = LabelFrame(frame, bd=2, text="L2 addr", relief=SUNKEN)
        l2_frame.place(x=5, y=s*5, height=s*180, width=self.width-10)
        l2_display_choice = ttk.Notebook(l2_frame, style='lefttab.TNotebook')
        l2_display_choice.place(x=5, y=s*5, height=s*150, width=self.width-75)
        l2_sub_frame1 = Frame(l2_display_choice)
        l2_canvas1 = Canvas(l2_sub_frame1, bd=0, bg='#ccc', height=s*150, width=length)
        l2_canvas1.place(x=20, y=0)
        l2_sub_frame2 = Frame(l2_display_choice)
        l2_canvas2 = Canvas(l2_sub_frame2, bd=0, bg='#ccc', height=s*150, width=length)
        l2_canvas2.place(x=20, y=0)
        l2_display_choice.add(l2_sub_frame1, text='real\naddr')
        l2_display_choice.add(l2_sub_frame2, text='addr\noccu')
        Label(l2_sub_frame1, text="32M", bg='#ccc').place(x=left+length-65, y=s*130)
        Button(l2_frame, text="detail", command=lambda: self.show_frags("L2", stamp.get()))\
            .place(x=left+length+15, y=s*100)

        # ========= l1 frame ============
        l1_frame = LabelFrame(frame, bd=2, text="L1 addr", relief=SUNKEN)
        l1_frame.place(x=5, y=s*190, height=s*185, width=self.width-10)
        l1_display_choice = ttk.Notebook(l1_frame, style='lefttab.TNotebook')
        l1_display_choice.place(x=5, y=s*5, height=s*150, width=self.width-75)
        l1_sub_frame1 = Frame(l1_display_choice)
        l1_canvas1 = Canvas(l1_sub_frame1, bd=0, bg='#ccc', height=s*150, width=length)
        l1_canvas1.place(x=20, y=0)
        l1_sub_frame2 = Frame(l1_display_choice)
        l1_canvas2 = Canvas(l1_sub_frame2, bd=0, bg='#ccc', height=s*150, width=length)
        l1_canvas2.place(x=20, y=0)
        l1_display_choice.add(l1_sub_frame1, text='real\naddr')
        l1_display_choice.add(l1_sub_frame2, text='addr\noccu')
        Label(l1_sub_frame1, text="6M", bg='#ccc').place(x=left+length-70, y=s*130)
        Button(l1_frame, text="detail", command=lambda: self.show_frags("L1", stamp.get()))\
            .place(x=left+length+15, y=s*100)

        # ========= cost frame ============
        cost_frame = LabelFrame(frame, bd=2, text="cost model profiling", relief=SUNKEN)
        cost_frame.place(x=5, y=s*380, height=s*290, width=self.width-10)
        cost_canvas = Canvas(cost_frame, bd=2, bg='#ccc', height=s*270, width=length)
        cost_canvas.place(x=left, y=0)
        streams = ["L3>>L3", "L3>>L2", "L2>>L3", "L2>>L2", "L3>>L1", "L2>>L1", "Workload", "L1>>L1", "L1>>L2", "L1>>L3"]
        colors = ["#66FF99", "#4DA041", "#7DA041", "#A9A1B3", "#5D3041",
                  "#B4AEF4", "#B1B8B2", "#488888", "#A99087", "#A99087"]
        stream_idx = {stream: i for i, stream in enumerate(streams)}
        for i, stream in enumerate(streams):
            Button(cost_frame, text=stream).place(x=0, y=s*30*i)

        Label(frame, text="cycle_time =").place(x=45, y=s*730)
        cycle_time = Label(frame, text="")
        cycle_time.place(x=left+60, y=s*730)

        def change_l2():
            # ========= real addr  ============
            l2_canvas1.delete('all')
            l2_canvas1.clipboard_clear()
            t = stamp.get()
            frags = self.recorder.states[t].L2_frags
            for frag in frags:
                left = length * frag.addr / L2_TOTAL_SIZE + 3  # avoid missing addr close to 0
                right = length * (frag.addr + frag.size) / L2_TOTAL_SIZE + 3
                block = l2_canvas1.create_rectangle(left, 0, right, s*150,
                                                    fill=colors[stream_idx[self.recorder.node_stream_map[frag.op_name]]])
                block_tip = ToolTip(l2_canvas1, tag=block,
                                    text="{}\naddr: {} - {}".format(frag.op_name, frag.addr, frag.addr + frag.size))
            # ========= addr occupancy ============
            l2_canvas2.delete('all')
            scale = time_scale.get()
            time = self.recorder.time_stamp[t]
            time_interval = [time - 100 * 2 ** scale, time + 100 * 2 ** scale]
            stamp_begin = max(0, upper_bound(self.recorder.time_stamp, time_interval[0]) - 1)
            stamp_end = upper_bound(self.recorder.time_stamp, time_interval[1])
            for i in range(5):
                l2_canvas2.create_line(0, s * (140 - i * 30), length, s * (140 - i * 30), fill='gray', dash=(4, 4))
                l2_canvas2.create_text(20, s * (130 - i * 30), text="{}%".format(i * 20))
            time_line = l2_canvas2.create_line(length / 2, 0, length / 2, s * 150, fill='gray', dash=(4, 4))
            last_o = 0
            last_h = 150
            for t in range(stamp_begin, stamp_end):
                total_size = 0
                frags = self.recorder.states[t].L2_frags
                for frag in frags:
                    total_size += frag.size
                o = length * (self.recorder.time_stamp[t] - time_interval[0]) / (
                            time_interval[1] - time_interval[0])
                h = s * 140 * (1 - total_size / L2_TOTAL_SIZE)
                # if total_size / L2_TOTAL_SIZE > 0.9:
                #     print(self.recorder.time_stamp[t], [frag.size for frag in frags], total_size / L2_TOTAL_SIZE)
                rate = l2_canvas2.create_oval(o - 5, h - 5, o + 5, h + 5, fill="brown")
                ToolTip(l2_canvas2, tag=rate, text="{:.2f}%".format(100 * total_size / L2_TOTAL_SIZE))
                # l2_canvas2.create_text(o, h-15, text="{:.2f}%".format(100 * total_size / L1_TOTAL_SIZE))
                l2_canvas2.create_line(o, h, last_o, last_h, fill='gray')  # , dash=(4, 4)
                last_o = o
                last_h = h

        def change_l1():
            # ========= real addr  ============
            l1_canvas1.delete('all')
            l1_canvas1.clipboard_clear()
            t = stamp.get()
            frags = self.recorder.states[t].L1_frags
            for frag in frags:
                left = length * frag.addr / L1_TOTAL_SIZE + 3
                right = length * (frag.addr + frag.size) / L1_TOTAL_SIZE + 3
                block = l1_canvas1.create_rectangle(left, 0, right, s*150,
                                                    fill=colors[stream_idx[self.recorder.node_stream_map[frag.op_name]]])
                block_tip = ToolTip(l1_canvas1, tag=block,
                                    text="{}\naddr: {} - {}".format(frag.op_name, frag.addr, frag.addr + frag.size))
            # ========= addr occupancy ============
            l1_canvas2.delete('all')
            scale = time_scale.get()
            time = self.recorder.time_stamp[t]
            time_interval = [time - 100 * 2 ** scale, time + 100 * 2 ** scale]
            stamp_begin = max(0, upper_bound(self.recorder.time_stamp, time_interval[0]) - 1)
            stamp_end = upper_bound(self.recorder.time_stamp, time_interval[1])
            for i in range(5):
                l1_canvas2.create_line(0, s*(150-i*30), length, s*(150-i*30), fill='gray', dash=(4, 4))
                l1_canvas2.create_text(20, s*(140-i*30), text="{}%".format(i*20))
            time_line = l1_canvas2.create_line(length / 2, 0, length / 2, s * 150, fill='gray', dash=(4, 4))
            last_o = 0
            last_h = 150
            for t in range(stamp_begin, stamp_end):
                total_size = 0
                frags = self.recorder.states[t].L1_frags
                for frag in frags:
                    total_size += frag.size
                o = length * (self.recorder.time_stamp[t] - time_interval[0]) / (time_interval[1] - time_interval[0])
                h = s * 150 * (1 - total_size / L1_TOTAL_SIZE)
                rate = l1_canvas2.create_oval(o-5, h-5, o+5, h+5, fill="green")
                ToolTip(l1_canvas2, tag=rate, text="{:.2f}%".format(100 * total_size / L1_TOTAL_SIZE))
                # l1_canvas2.create_text(o, h-15, text="{:.2f}%".format(100 * total_size / L1_TOTAL_SIZE))
                l1_canvas2.create_line(o, h, last_o, last_h, fill='gray')  # , dash=(4, 4)
                last_o = o
                last_h = h

        def change_cost():
            cost_canvas.delete('all')
            cost_canvas.clipboard_clear()
            time_line = cost_canvas.create_line(length / 2, 0, length / 2, s*270, fill='gray', dash=(4, 4))
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
                    if task.op_name in task_set:
                        continue
                    task_set.add(task.op_name)
                    left = length * (task.start - time_interval[0]) / (time_interval[1] - time_interval[0])
                    right = length * (task.end - time_interval[0]) / (time_interval[1] - time_interval[0])
                    top = s*30 * stream_idx[task.stream]
                    down = top + s*24
                    block = cost_canvas.create_rectangle(left, top, right, down, fill=colors[stream_idx[task.stream]])
                    if len(task.opType) * 8 < right - left:
                        cost_canvas.create_text((left + right) // 2, (top + down) // 2, text=task.opType)
                    block_tip = ToolTip(cost_canvas, tag=block,
                                        text="{}\ncycle: {} - {}".format(task.op_name, task.start, task.end))

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
        self.stamp_scale.place(x=left, y=s*680, width=length)

        interval_scale = Scale(frame, activebackground="green", from_=0, to=12, variable=time_scale,
                               resolution=1, orient=VERTICAL, tickinterval=0, length=s*100, width=20,
                               command=change_time)
        interval_scale.set(0)
        interval_scale.place(x=left+length+15, y=s*660)
        Label(frame, text="scale").place(x=left+length-15, y=s*750)

        def stamp_add(event):
            if event.delta > 0 or event.keysym == "Left":
                self.stamp_scale.set(stamp.get() - 1)
            elif event.delta < 0 or event.keysym == "Right":
                self.stamp_scale.set(stamp.get() + 1)
            elif event.keysym == "Up":
                interval_scale.set(time_scale.get() - 1)
            elif event.keysym == "Down":
                interval_scale.set(time_scale.get() + 1)

        cost_canvas.bind("<MouseWheel>", stamp_add)
        cost_frame.bind("<Key>", stamp_add)
        cost_frame.focus_set()

    def add_topLevel(self):
        topwindow = Toplevel(width=350)
        topwindow.title("设置窗口大小")

        Label(topwindow, text="设置高度:").pack()
        height_chosen = ttk.Combobox(topwindow, width=40)
        height_list = [500, 600, 700, 800, 900, 1000]
        height_chosen['values'] = height_list
        height_chosen.pack(side=TOP, expand=YES)
        height_chosen["state"] = "readonly"
        height_chosen.set(800)
        height_chosen.bind("<<ComboboxSelected>>")  # 绑定事件

        Label(topwindow, text="设置宽度:").pack()
        width_chosen = ttk.Combobox(topwindow, width=40)
        width_list = [600, 750, 900, 1080, 1200, 1400]
        width_chosen['values'] = width_list
        width_chosen.pack(side=TOP, expand=YES)
        width_chosen["state"] = "readonly"
        width_chosen.set(900)
        width_chosen.bind("<<ComboboxSelected>>")  # 绑定事件
        def set_and_quit():
            self.height = int(height_chosen.get())
            self.width = int(width_chosen.get())

            self.general_feedback("SUCCESS", "已修改高度为: {}, 宽度为: {}".
                                  format(str(height_chosen.get()), str(width_chosen.get())))
            topwindow.destroy()
            self.frame_mid.destroy()
            self.frame_mid = Frame(self.main_page, width=self.width, height=self.height)
            self.frame_mid.pack()
            self.make_frame_mid(self.frame_mid)

        Button(topwindow, text="确定", command=set_and_quit).pack()

    def jump_to_node(self):
        topwindow = Toplevel(width=350)
        topwindow.title("jump to op_name")

        Label(topwindow, text="Op name:").pack()
        name = StringVar()
        node_name = Entry(topwindow, textvariable=name)
        node_name.pack()

        def set_and_quit():
            if name.get() in self.recorder.node_start_map:
                self.general_feedback("SUCCESS", "start time: {}".format(self.recorder.node_start_map[name.get()]))
                stamp = self.recorder.time_map[self.recorder.node_start_map[name.get()]]
                self.stamp_scale.set(stamp)
                topwindow.destroy()
            else:
                self.general_feedback("FAIL", "no op named {}".format(name.get()))

        Button(topwindow, text="确定", command=set_and_quit).pack()


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

        submenu = Menu(menu, tearoff=0)
        submenu.add_command(label="设置窗口尺寸", command=self.add_topLevel)
        submenu.add_command(label="设置配色", command=lambda: self.general_feedback("ERROR", "unavailable"))
        menu.add_cascade(label="Setting", menu=submenu)

        submenu = Menu(menu, tearoff=0)
        submenu.add_command(label="查看Node", command=self.jump_to_node)
        menu.add_cascade(label="Search", menu=submenu)

        self.frame_mid = Frame(self.main_page)
        self.frame_mid.pack()
        self.height = min(self.height, self.top.winfo_screenheight())
        self.frame_mid.config(width=self.width, height=self.height)
        # v = Scrollbar(frame_mid)
        # v.place(x=800, y=0)

        self.make_frame_mid(self.frame_mid)


if __name__ == "__main__":
    ui = UI()

