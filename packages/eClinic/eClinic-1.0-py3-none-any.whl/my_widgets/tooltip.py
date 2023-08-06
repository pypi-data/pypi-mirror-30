from tkinter import *
from tkinter import ttk

class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() +50

        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT, wraplength=150,
                        background="#ffffe0", relief=SOLID, borderwidth=1,
                        font=("tahoma", "10", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
        #===========================================================
def createToolTip( widget, text=None):
    toolTip = ToolTip(widget)
    def enter(event):
        if text is None:
            if isinstance(widget, Entry):
                toolTip.showtip(widget.get())
        else:
            toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

if __name__ == '__main__':
    root= Tk()
    entry = ttk.Entry(root, width=50)
    entry.pack(padx=4, pady=4)
    createToolTip(entry, "This is an entry widget from uganda")
    root.mainloop()
