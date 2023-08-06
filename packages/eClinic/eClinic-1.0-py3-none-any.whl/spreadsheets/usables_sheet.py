import sys
sys.path.append("../")

from tkinter import ttk
from tkinter import *
from collections import OrderedDict
from my_widgets.widgets import SearchEngine
import ast

class UsablesSheet(Frame):
    def __init__(self, rows, cols, headers, parent, **kwargs):
        Frame.__init__(self)
        self.rows=rows
        self.columns=cols

        if 'base' in kwargs:
            self.department = kwargs['base'].department

        assert self.rows==1, "Must initailise with one row"
        assert self.columns==5, "Columns must be 5"

        self.header_labels = headers
        self.widgets=[]
        self.widget_rows=[]
        self.find_cell_inserted=[]
        self.mainframe= parent

        top_frame= Frame(self.mainframe)
        top_frame.pack(expand=0, fill=BOTH)

        #----------------------------------------------
        title=Label(top_frame, text="Usables")
        title.pack(side=TOP, padx=4,pady=4,anchor='nw')
        title.configure(font="Arial 14 bold italic underline", fg='tan')

        if self.department=="Clinician":
            btn=Button(top_frame, text="CLEAR", font="Consolas 10 bold",
                command=self.clear, bg='powderblue')
            btn.pack(side=LEFT, padx=4,pady=4,anchor='nw')

        self.engine=SearchEngine(top_frame, command_to_run= self.select_drug)
        self.engine.connect_to(user="root",
                                database="patients",
                                password="cmaster2018")
        self.engine.use(table='usables', column="ItemName")
        self.engine.set_width(75)
        self.engine.set_padding(2)
        self.parent= Frame(self.mainframe)
        self.parent.pack(fill=BOTH, expand=1)

        # Context Menu
        self.menu = Menu(tearoff=False)
        self.menu.add_command(label="Clear Cell", command=self.clear_cell)
        self.menu.add_command(label="Clear Row",command=self.clear_row)
        self.menu.add_command(label="Clear Table", command=self.clear)

        if self.department !="Cashier":
            self.parent.bind_class("Entry","<Up>", self.up)
            self.parent.bind_class("Entry","<Down>", self.down)
            self.parent.bind_class("Entry","<Button-3>", self.on_context_menu)

    def is_empty(self, data):
        n=len(data)
        if data ==[""*n]:
            return True

    def select_drug(self, selection):
        if not self.department=="Clinician":
            return
        sheet_data= self.get()
        if self.is_empty(sheet_data):
            sheet_data=[]
        selcted_drug=[selection[0], selection[1],selection[2],
        "",""]
        sheet_data.extend(selcted_drug)
        self.insert(0, sheet_data)

    def on_context_menu(self, event):
        self.menu.post(event.x_root , event.y_root)

    def clear_cell(self):
        widget = self.mainframe.focus_get()
        if isinstance(widget, Entry):
            widget.delete(0, END)

    def clear_row(self):
        widget = self.mainframe.focus_get()
        if isinstance(widget, Entry):
            row= widget.grid_info()["row"]
            for widget in self.widgets:
                if widget.grid_info()['row']==row:
                    widget.delete(0, END)

    def delete(self, _from=None, to=None):
        self.clear()

    def clear(self):
        for cell in self.widgets[self.columns:]:
            cell.delete(0, 'end')

        self.rows=1
        self.columns=self.columns
        self.widgets=[]
        self.widget_rows=[]
        self.find_cell_inserted=[]
        self.build_sheet()

    def build_sheet(self):
        self.parent.destroy()
        self.parent= Frame(self.mainframe)
        self.parent.pack(fill=BOTH, expand=1, padx=2)

        for i in range(self.rows):
            wid_row=[]
            for j in range(self.columns):
                cell= Entry(self.parent, font="Arial 10")
                cell.grid(row=i, column=j, sticky='nsew')
                self.parent.grid_columnconfigure(i, weight=1)
                self.parent.grid_rowconfigure(j, weight=1)
                self.widgets.append(cell)
                wid_row.append(cell)

            self.widget_rows.append(tuple(wid_row))

        for index, entry in enumerate(self.widgets):
            self.header_rows=OrderedDict()

            info= entry.grid_info()

            if info['row']==0:
                entry.configure(font="Arial 11 bold")
                self.header_rows[info['column']]=entry

            # Insert header items
            for key, value in self.header_rows.items():
                value.insert(0, self.header_labels[key])
                value.configure(state=DISABLED, foreground='blue')

    def get_values(self):
        return (cell.get() for \
            cell in self.widgets[self.columns:] if \
            cell.grid_info()["row"] !=0)

    def get(self):
        values=[]
        for val in self.get_values():
            values.append(val)

        return values


    def insert(self, index, values):
        if isinstance(values, str):
            values= ast.literal_eval(values)

        for i in range(len(values)):
            try:
                assert len(values)<= len(self.widgets)-self.columns # No headers
            except AssertionError:
                self.add_row()

            W= list(self.widgets[self.columns:])[i]
            W.delete(0, 'end')
            W.insert(0, values[i])

    def add_row(self):
        i=self.rows = self.rows + 1
        wid_row=[]
        for j in range(self.columns):
            cell= Entry(self.parent, font="Arial 10")
            cell.grid(row=i, column=j, sticky='nsew')
            self.parent.grid_columnconfigure(i, weight=1)
            self.parent.grid_rowconfigure(j, weight=1)
            self.widgets.append(cell)
            wid_row.append(cell)

            if j==0:
                cell.configure(width=8)

            if j==1:
                cell.configure(width=55)

            if j==2:
                cell.configure(width=8)
            if j==3:
                cell.configure(width=15)
            if j==4:
                cell.configure(width=20)
                if self.department !="Cashier":
                    cell.configure(state=DISABLED)

        self.widget_rows.append(tuple(wid_row))


    def up(self, event):
        info=event.widget.grid_info()
        row, col= info['row'], info['column']
        upper_row, upper_col = row-1, col
        cell = self.find_cell(upper_row, upper_col)
        if cell:
            cell.focus_set()

    def find_cell(self, row, column):
        for child in self.widgets:
            _row = child.grid_info()["row"]
            _column=child.grid_info()["column"]
            if _row==row and _column==column:
                return child

    def down(self, event):
        info = event.widget.grid_info()
        row,col= info['row'], info['column']
        lower_row, lower_col = row+1, col
        cell = self.find_cell(lower_row, lower_col)
        if cell:
            cell.focus_set()

if __name__ == '__main__':
    root=Tk()
    sheet= UsablesSheet(1, 5,["Item ID", "Item Name", "Cost", "Qty", "Subtotal"],root)
    sheet.build_sheet()
    root.mainloop()
