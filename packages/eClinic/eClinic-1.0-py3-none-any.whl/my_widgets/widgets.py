import tkinter.ttk as ttk
from tkinter import *
from datefield import Datepicker
from tkinter import scrolledtext
from collections import OrderedDict
import ast
from mysql.connector import connect
import sys
from tkinter import font as tkFont


class Treeview(ttk.Treeview):
    '''
    A treeview widget that can be used as a table widget.
    Inherits from ttk.Treeview
    '''
    def __init__(self, parent, headers, parent_self=None, *args, **kwargs):
        ''' Example: Treeview(parent, headers=["ID","NAME","AGE"]) '''
        ttk.Treeview.__init__(self, parent,  columns = headers, show="headings", *args, **kwargs)

        self.vsb = ttk.Scrollbar(parent, orient="vertical", command=self.yview)
        self.hsb = ttk.Scrollbar(parent, orient="horizontal", command=self.xview)
        self.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.vsb.pack(side='right', fill="y", anchor='w')
        self.hsb.pack(side='bottom', fill="x")

        self.parent = parent
        self.headers = headers
        self.parent_self = parent_self
        self.current_selection = None
        self.bind("<<TreeviewSelect>>", self.get_selection)
        self._build_tree()

    def set_headers(self, headers):
        self.headers = headers

    def destroy_scrollbars(self):
        self.hsb.destroy()
        self.vsb.destroy()

    def set_col_width(self, w):
        for col in self.headers:
            if col=="ID":
                self.column(col, width=50)
            else:
                self.column(col, width=w)

    def _build_tree(self):
        for col in self.headers:
            self.heading(col, text=col, anchor='w', command=lambda c=col: self.sortby(self, c, 0))
            self.column(col, anchor='w')

    def sortby(self, tree, col, descending):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        tree.heading(col, command=lambda col=col: self.sortby(tree, col, int(not descending)))

    def fill_tree(self):
        self.delete(*self.get_children())
        if self.register is not None:
            for item in self.register:
                self.insert('', 'end', values=item)
                # adjust column's width if necessary to fit each value
                for ix, val in enumerate(item):
                    try:
                        col_w = tkFont.Font().measure(val)
                        if self.column(self.headers[ix], width=None) < col_w:
                            self.column(self.headers[ix], width=col_w)
                    except:
                        pass

    def get_selection(self, event=None):
        '''Gets the item under focus and returns its rows in a list'''
        if event:
            current_selection = event.widget.focus()
            rows = self.item(current_selection)['values']
            if self.parent_self:
                ID = rows[0]
                self.parent_self.find_by_id(pt_id=ID)

    def set_register(self, register):
        '''Updates the treeview with the new register
        >>Register should be a list of tuples
        e.g [(1, "First Name", "Last Name","Sex"), (2, "Second Name", "Third Name", "Male")]'''
        self.register = register
        self.update_tree()

    def update_tree(self):
        '''Clears the treeview and update it with the new register.
        This method should not be called directly but rather
        calling set_register(register) calls update method.
        '''
        self.clear()
        self.fill_tree()

    def clear(self):
        self.delete(*self.get_children())

    def get_all(self):
        """Returns a list of all treeview items"""
        return [item for item in self.get_children()]


class SearchEngine(Frame):
    '''A custom search engine designed for querying databases'''
    def __init__(self, frame, command_to_run):
        '''Constructror takes a frame to pack the widget, the frame should not have gridded widgets,
        It also expects a command from the calling instance to run on selection of an item
        eg. engine= SearchEngine(self.engineframe, command_to_run=self.lookup)
            >>Connect to a desired MySQL database
            engine.connect_to(user=user, host="host", database='database', database='database')
            >> choose a table to use
            engine.use("mytable")
        '''
        Frame.__init__(self)

        self.frame = frame
        self.command = command_to_run
        self.tablename=None
        self.treeheaders=[]

        var = StringVar()
        self.ent = ttk.Entry(self.frame, textvariable=var, width=40)
        self.ent.configure(font="Calibri 16 bold", foreground="green")
        self.ent.focus()
        self.ent.pack(side='top', fill=Y, pady=2, anchor='w')

        self.var = var
        if self.var == '':
            self.var = self.ent["textvariable"] = StringVar()

        self.var.trace('w', self.changed)
        self.tree_up = False

    def set_width(self, width):
        '''Dynamically alter the width of search entry'''
        self.ent.configure(width=width)

    def set_padding(self, padx=5, pady=5):
        self.ent.pack_configure(padx=padx, pady=pady)

    def connect_to(self, user, database, password,host='localhost'):
        try:
            self.connection= connect(user=user, password=password,database=database, host=host)
        except:
            '''Alerting the user would break the search engine'''
            self.connection=None

    def use(self, table, column=None):
        self.tablename= table
        self.column_to_lookup= column

    def find_by_name(self, name):

        if self.tablename and self.connection and self.column_to_lookup:
            cursor = self.connection.cursor()
            try:
                cursor.execute("""SELECT * FROM {} WHERE {} RLIKE '{}'""".format(self.tablename,
                    self.column_to_lookup, name))
                fields= cursor.description
            except:
                return []

            if not self.treeheaders:
                for field in fields:
                    self.treeheaders.append(field[0])
            return cursor.fetchall()
        else:
            return []

    def changed(self, name, index, mode):
        # Keep track of the updates by calling Search function every keypress
        if self.var.get() == '':
            try:
                self.tree.destroy()
                self.tree.destroy_scrollbars()
                self.tree_up = False
            except:
                pass
        else:
            words = self.comparison()
            if words:
                if not self.tree_up:
                    self.tree = Treeview(self.frame, headers=self.treeheaders)
                    self.tree.pack(expand=1, fill=BOTH,padx=5, pady=5)

                    self.tree.bind("<Double-Button-1>", self.selection)
                    self.tree.bind("<Return>", self.selection)
                    self.tree_up = True
                self.tree.set_register(words)
            else:
                if self.tree_up:
                    self.tree.destroy()
                    self.tree.destroy_scrollbars()
                    self.tree_up = False


    def selection(self, event):
        if self.tree_up:
            current_selection = event.widget.focus()
            selection = event.widget.item(current_selection)['values']
            self.tree.destroy()
            self.tree.destroy_scrollbars()
            self.command(selection)

            self.tree_up = False
            try:
                self.ent.delete(0, 'end')
            except TclError:
                pass  # Deleting the lab search entry when demogframe is dstroyed.

    def comparison(self):
        '''Queries the database and returns dynamically results with each keypress'''
        return self.find_by_name(self.var.get())

class Notebook(ttk.Notebook):
    def __init__(self, parent, *args, **kwargs):
        ttk.Notebook.__init__(self, parent,*args, **kwargs)
        self.parent = parent

    def add_tab(self, frame, text):
        self.add(frame, text=text)
        return frame

    def hide_tab(self, tab):
        return self.hide(tab)

    def hide_tabs(self, tabs=[]):
        if isinstance(tabs, list):
            for tab in tabs:
                self.hide_tab(tab)
        else:
            raise TypeError("Expected a list of tab_ids(Frames), got {} type".format(type(tabs)))

class Diagnosis(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent

        self.entries=OrderedDict()
        self.fields=["Primary Diagnosis",
        "Secondary Diagnosis", "Co-morbidities"]
        for i, field in enumerate(self.fields):
            Label(self, text=field, font="Consolas 14").grid(row=i, column=0, sticky='w')
            entry = ttk.Entry(self, font="Arial 14 bold",width=80)
            entry.grid(row=i, column=1,
                padx=4,pady=2, sticky='ew')
            self.entries[field] = entry

    def get(self):
        DIAGNOSES=[]
        for entry in self.entries.values():
            DIAGNOSES.append(entry.get())
        return DIAGNOSES

    def delete(self,*args):
        [entry.delete(0,'end') for entry in self.entries.values()]

    def insert(self, index, items):
        try:
            items=ast.literal_eval(items)
        except:
            items=["","",""]
        if isinstance(items, list):
            self.entries["Primary Diagnosis"].insert(0, items[0])
            self.entries["Secondary Diagnosis"].insert(0, items[1])
            self.entries["Co-morbidities"].insert(0, items[2])

class BP(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent=parent

        self.entries=OrderedDict()
        self.fields=["SBP", "DBP", "MAP"]
        for i, field in enumerate(self.fields):
            Label(self, text=field, font="Consolas 12").pack(side=LEFT)
            entry = ttk.Entry(self, width=5, font="Arial 13 bold")
            entry.pack(side=LEFT, padx=4,pady=2)
            entry.bind("<FocusOut>", self.compute_map)
            self.entries[field] = entry

        self.entries["MAP"].config(state=DISABLED)

    def compute_map(self, event=None):
        try:
            SBP= int(self.entries["SBP"].get())
            DBP= int(self.entries["DBP"].get())
        except ValueError:
            return
        else:
            PULSE_BP = SBP-DBP
            MAP = int(float(DBP) + float(PULSE_BP)/3)
            self.entries["MAP"].config(state=NORMAL)
            self.entries["MAP"].delete(0,"end")
            self.entries["MAP"].insert(0, MAP)
            self.entries["MAP"].config(state=DISABLED)

            self.analyse_BPS(SBP, DBP)

    def analyse_BPS(self, sbp, dbp):
        try:
            assert 90 <sbp<140, "Systolic BP is abnormal"
        except AssertionError as e:
            self.entries["SBP"].config(foreground='red')
        else:
            self.entries["SBP"].config(foreground='green')

        try:
            assert 60 <dbp<90, "Diastolic BP is abnormal"
        except AssertionError as e:
            self.entries["DBP"].config(foreground='red')
        else:
            self.entries["DBP"].config(foreground='green')


    def get(self):
        self.entries["MAP"].config(state=NORMAL)
        BPS=[]
        for entry in self.entries.values():
            BPS.append(entry.get())
        self.entries["MAP"].config(state=DISABLED)
        return BPS

    def delete(self,*args):
        self.entries["MAP"].config(state=NORMAL)
        [entry.delete(0,'end') for entry in self.entries.values()]
        self.entries["MAP"].config(state=DISABLED)

    def insert(self, index, items):
        if isinstance(items, str):
            try:
                items=ast.literal_eval(items)
            except:
                items=["","",""]
        elif isinstance(items, list):
            items=items

        self.entries["SBP"].insert(0, items[0])
        self.entries["DBP"].insert(0, items[1])
        self.entries["MAP"].config(state=NORMAL)
        self.entries["MAP"].insert(0, items[2])
        self.compute_map()
        self.entries["MAP"].config(state=DISABLED)


class DateField(Datepicker):
    def __init__(self, parent, *args, **kwargs):
        Datepicker.__init__(self, parent, *args, **kwargs)

        self.parent= parent

class ComboBox(ttk.Combobox):
    def __init__(self, parent, *args, **kwargs):
        ttk.Combobox.__init__(self,parent, *args, **kwargs)

    def insert(self,start, item):
        '''Allows the Combobox widget to be used as an entry widget'''
        self.set(str(item))

class MyText(scrolledtext.ScrolledText):
    def __int__(self, parent, *args, **kwargs):
        '''Inherits tkinter.scrolledtext.ScrolledText'''
        super().__init__( wrap=WORD, *args, **kwargs)


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
        x = x + self.widget.winfo_rootx() + 100
        y = y + cy + self.widget.winfo_rooty() +5

        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                        background="#ffffe0", relief=SOLID, borderwidth=1,
                        font=("tahoma", "10", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
        #===========================================================
def createToolTip( widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)



