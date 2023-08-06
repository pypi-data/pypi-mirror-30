import sys
sys.path.append("../")

from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont
from tkinter.messagebox import askquestion, showinfo
import Pmw, ast, os, configparser
from collections import OrderedDict
from config_data import investigations_dict
from my_widgets import Treeview

charges_dict = OrderedDict()
if os.path.exists("./lab_costs.ini"):
    config = configparser.ConfigParser()
    config.optionxform = str

    config.read("./lab_costs.ini")
    sections = config.sections()
    for section in sections:
        options = config.options(section)
        for option in options:
            value = config.get(section, option)
            if option and value:
                try:
                    int_value = config[section].getint(option)
                    charges_dict[option] = int_value
                except KeyError:
                    pass

class LAB(Pmw.ScrolledFrame):
    def __init__(self, parent=None, parent_self=None):
        Pmw.ScrolledFrame.__init__(self, parent,
            labelpos='n',
            label_text='CLINICAL LABORATORY',
            vscrollmode='dynamic', hscrollmode='dynamic')

        self.pack(expand=1, fill=BOTH)
        self.labs = investigations_dict
        self.FINAL = []

        self.parent = parent
        self.active=True
        self.curItem = None
        self.parent_self = parent_self
        self.widgets=OrderedDict()
        Pmw.initialise()
        self.build_main_frame()
        self.frame = Frame(self.interior(), relief='flat', bd=4)
        self.results_frame = Frame(self.interior(), relief='ridge', bd=2)
        self.create_cost_frame()

    def create_cost_frame(self):
        self.cost_frame = Frame(self.interior(), height=500)
        self.cost_frame.pack(side='left', fill=BOTH, expand=1, anchor='nw', padx=5)

        self.header=Label(self.cost_frame,
            font='Arial 16 bold', relief='raised', fg='green',
            text='INVESTIGATIONS & CHARGES')
        self.header.pack()

        self.btn_frm = Frame(self.cost_frame)
        self.btn_frm.pack(pady=4)

        b1=ttk.Button(self.btn_frm, command=self.delete_selected_test,text='DELETE')
        b1.pack(side='left', padx=4, pady=4)
        b2=ttk.Button(self.btn_frm, command=self.delete_all,text='DELETE ALL')
        b2.pack(side='left', padx=4, pady=4)

        self.tree = Treeview(self.cost_frame, ["Lab Test", "Cost(Ugx)"], self)
        self.tree.pack(side='top', fill=BOTH, expand=1, anchor='nw')
        self.tree.bind('<<TreeviewSelect>>', self.getselection)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Courier', 14, 'bold'), foreground='red')
        ttk.Style().configure("Treeview", background='white',
        font=('Calibri', 12, 'bold'), foreground='black', pady=4)
        ttk.Style().configure("TButton", background='powderblue',
        font=('Calibri', 12, 'bold'), foreground='blue', pady=4)

    def getvalue(self, name, state):
        if state:
            self.multiple.button(name).config(bg='powderblue', fg='green')
            self.build_interface(name)

        else:
            self.frame.destroy()
            self.multiple.button(name).config(bg='SystemButtonFace', fg='black')


        self.update_labs()
        self.curItem = None

    def build_final_list(self, index, spec_name):
        self.ticked = self.vars[index].get() # Boolean flag
        test = spec_name

        if self.ticked:
            if test not in self.FINAL:
                self.FINAL.append(test)
            else:
                self.FINAL.remove(test)

        else:
            try:
                self.FINAL.remove(test)
            except ValueError:
                if test not in self.FINAL:
                    self.FINAL.append(test)

        self.FINAL = list(set(self.FINAL))
        self.update_labs()

    def build_interface(self, name):
        self.frame.pack_forget()
        F = self.interior()
        F.place(x=10, y=90)

        self.frame = Frame(F, relief='flat', bd=4)
        self.frame.pack(side='right', expand=0, fill=X, anchor='nw',padx=20)

        Label(self.frame, text=name.upper(), fg='green',
              font='Courier 14 bold underline').pack(expand=1, fill=X)

        fields = self.labs[name]
        for i, field in enumerate(fields):
            self.var = IntVar()
            entry = Checkbutton(self.frame, text=fields[i],
            name=field.lower(),variable=self.var, font="Arial 12",
            command=lambda i=i, field=field: self.build_final_list(i, field))
            entry.pack(anchor='nw', pady=2)
            key = fields[i]
            self.vars.append(self.var)
            self.widgets[key]=entry

    def build_main_frame(self):
        fields = sorted([key for key in self.labs.keys()])
        self.entries = {}
        self.vars = []

        self.multiple = Pmw.RadioSelect(self.interior(),
            labelpos=W, orient='vertical',
            command=self.getvalue, selectmode=MULTIPLE)
        self.multiple.pack(side='left', expand=0, fill=None, padx=10, pady=10,
            anchor='nw')

        for i, field in enumerate(fields):
            self.multiple.add(field)

        self.total_var = StringVar()

        self.total_var.set('Total: ' + str(sum(self.FINAL)))
        self.total = Label(self.interior(), font='Arial 14 bold',
                           textvariable=self.total_var)
        self.total.pack(anchor='w', padx=20)

    def delete_selected_test(self):
        if self.parent_self.patient_to_lab() == True:
            showinfo("Not allowed", "Patient already visited lab")
            return
        if not self.curItem: return
        name = self.tree.item(self.curItem)['values'][0]
        ans = askquestion("Delete", "Delete {} from the Tests?".format(name))
        if ans == 'yes':
            self.tree.delete(self.curItem)
            self.FINAL.remove(name)
            self.update_labs()
            self.parent_self.update_current(name)

            try:
                key = name.upper().replace(" ", "_")
                self.entries[key].deselect()

            except:
                pass

            self.curItem = None

    def delete_all(self):
        if self.parent_self.patient_to_lab() == True:
            showinfo("Not allowed", "Patient already visited lab")
            return

        self.tree.delete(*self.tree.get_children())
        self.FINAL = []
        self.update_labs()
        self.frame.destroy()

    def getselection(self, event):
        self.curItem = event.widget.focus()

    def update_labs(self):
        self.cost_frame.destroy()
        self.create_cost_frame()

        data_columns = []
        lab_costs = []

        for key, val in charges_dict.items():
            if key in self.FINAL:
                try:
                    self.widgets[key].select()
                except:pass
                item = (key, self.sep(val))
                if item not in data_columns:
                    data_columns.append(item)

                lab_costs.append(int(val))
            elif key in self.FINAL and key not in self.widgets:
                self.FINAL.remove(key)

        self.tree.set_register(list(data_columns))

        try:
            self.total_var.set("TOTAL: " + self.sep(str(sum(lab_costs))))
        except:
            pass

    def sep(self, s, thou=", ", dec="."):
        try:
            '''Generates thousand seperators'''
            if str(s).isdigit():
                s = str(s) + '.0'
            integer, decimal = str(s).split(".")
            integer = re.sub(r"\B(?=(?:\d{3})+$)", thou, integer)
            return integer + dec + decimal
        except:
            return 'Wrong number Format'

    def remove_buttons(self):
        self.btn_frm.destroy()
        self.total_var.set("")
        self.total['state']=DISABLED
        self.configure(vscrollmode='none')
        self.tree['displaycolumns']=["Lab Test"]
        self.header.configure(text="Requested Investigations", font='arial 20 bold')

        i=0
        for key in investigations_dict:
            btn= self.multiple.button(key)
            btn.config(width=1, height=1, text='', relief='flat')
            btn.config(state=DISABLED)
            if i <=4:
                btn.destroy()
            i +=1


    def get(self):
        return self.FINAL

    def delete(self, start, end):
        self.tree.delete(*self.tree.get_children())

    def insert(self, index, tests):
        if isinstance(tests, str):
            self.FINAL = ast.literal_eval(tests)
        elif isinstance(tests, list):
            self.FINAL = tests
        else:
            self.FINAL=[]
        self.update_labs()
        if self.active==False:
            self.remove_buttons()



if __name__ == '__main__':
    root = Tk()
    root.title('Laboratory Request Form')
    LAB(root).mainloop()
