import tkinter
import time
from tkinter import ttk
from tkinter import *
from tkinter import font
import numpy as np

L2_TOTAL_SIZE = 32 * 1024 * 1024

class UI:
    def __init__(self, l2):
        self.l2 = l2
        top = tkinter.Tk()
        top.title("L2 addr an")
        top.geometry("700x400")
        self.main_page = Frame(top)
        self.create_main_page()

        top.mainloop()

    def make_frame_mid(self, frame):
        # ========= canvas ============
        length = 650
        l2_canvas = Canvas(frame, bd=2, bg='#ccc', height=200, width=length)
        l2_canvas.place(x=25, y=100)
        Label(frame, text="0").place(x=25, y=310)
        Label(frame, text="32M").place(x=655, y=310)

        # ========= slice  ============
        def change_time(arg):
            l2_canvas.delete('all')
            l2_canvas.clipboard_clear()
            t = time.get()
            frags = self.l2.states[t].frags
            for frag in frags:
                left = int(length * frag.addr / L2_TOTAL_SIZE)
                right = int(length * (frag.addr + frag.size) / L2_TOTAL_SIZE)
                l2_canvas.create_rectangle(left, 0, right, 200, fill='purple')
        time = IntVar()
        interval_scale = Scale(frame, activebackground="green",
                               from_=0, to=len(self.l2.states) - 1,
                               resolution=1, orient=HORIZONTAL,
                               tickinterval=0, length=330, width=20,
                               command=change_time, variable=time)
        interval_scale.set(0)
        interval_scale.place(relx=0.05, rely=0.85, relwidth=0.9)




    def create_main_page(self):
        self.main_page.grid(row=0, column=0, sticky="nsew")

        frame_mid = Frame(self.main_page)
        frame_mid.pack()
        frame_mid.config(width=700, height=400)
        self.make_frame_mid(frame_mid)

if __name__ == "__main__":
    ui = UI()
