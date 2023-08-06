from tkinter import *
from tkinter import ttk
from my_widgets.widgets import BP
from collections import OrderedDict
import ast

class Vitals(Frame):
    __fields=("BP","PR", "RR", "TEMP", "SPO2")
    __field_units=("(mmHg)","(bpm)", "(/min)", "(oC)", "(%)")

    def __init__(self, parent=None, *args, **kwargs):
        self.parent=parent
        super().__init__(parent, *args, **kwargs)
        self.pack(expand=1, fill=BOTH)

        self.entries=OrderedDict()
        self.init_UI()

    def init_UI(self):
        label=Label(self, text="VITAL SIGNS",
            fg='green', font='Calibri 20 bold')
        label.grid(row=0, column=0, columnspan=2)

        for index, field in enumerate(self.__fields):
            label=Label(self, text=field + self.__field_units[index],
                font="Consolas 12")

            if field=="BP":
                entry=BP(self)
            else:
                entry= Entry(self, width=30)
                entry.configure(font="Consolas 12 bold")
                entry.bind("<FocusOut>", self.analyse_vitals)

            label.grid(row=index+1, column=0)
            entry.grid(row=index+1, column=1)

            self.entries[field] = entry

        b=ttk.Button(self, text="CLEAR", cursor='hand2', command=self.delete)
        b.grid(column=0, columnspan=2, pady=4)

    def analyse_vitals(self, event=None):
        try:
            PR=int(self.entries["PR"].get())
            try:
                assert 60<=PR<=90, "PR is abnormal"
            except AssertionError:
                self.entries["PR"].config(foreground="red")
            else:
                self.entries["PR"].config(foreground="green")
        except ValueError:pass

        try:
            RR=int(self.entries["RR"].get())
            try:
                assert 12<=RR<=20, "RR is abnormal"
            except AssertionError:
                self.entries["RR"].config(foreground="red")
            else:
                self.entries["RR"].config(foreground="green")

        except ValueError:pass

        try:
            SPO2=int(self.entries["SPO2"].get())
            try:
                assert SPO2>=90, "SPO2 is abnormal"
            except AssertionError:
                self.entries["SPO2"].config(foreground="red")
            else:
                self.entries["SPO2"].config(foreground="green")
        except ValueError:
            if "%" in self.entries["SPO2"].get():
                try:
                    SPO2= int(self.entries["SPO2"].get().replace("%",""))
                    try:
                        assert SPO2>=90, "SPO2 is abnormal"
                    except AssertionError:
                        self.entries["SPO2"].config(foreground="red")
                    else:
                        self.entries["SPO2"].config(foreground="green")
                except ValueError:pass

        try:
            TEMP = float(self.entries["TEMP"].get())
            try:
                assert 36.1<=TEMP<=37.2, "TEMP is abnormal"
            except AssertionError:
                self.entries["TEMP"].config(foreground="red")
            else:
                self.entries["TEMP"].config(foreground="green")
        except ValueError:
            pass

    def delete(self, *args):
        [entry.delete(0, END) for entry in self.entries.values()]

    def insert(self, index, values):
        if isinstance(values, str):
            try:
                values=ast.literal_eval(values)
            except:
                values=[["","",""],"","","",""]

        elif isinstance(values, list):
            values=values

        for i, entry in enumerate(self.entries.values()):
            entry.insert(0, values[i])

    def get(self):
        vals=[entry.get() for entry in self.entries.values()]
        return vals

if __name__ == '__main__':
    root= Tk()
    vitals = Vitals(root)
    values= "[['120', '80', '93'], '22', '22', '66', '77']"
    vitals.insert(0, values)
    root.mainloop()



