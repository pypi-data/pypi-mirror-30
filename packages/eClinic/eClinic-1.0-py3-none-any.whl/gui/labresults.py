import sys, os
sys.path.append("../")

from tkinter import *
from tkinter import ttk
import Pmw, configparser, os
from search import AutocompleteEntry
from mysql.connector import connect
from my_widgets.widgets import Treeview, MyText
from collections import OrderedDict
from config_data import investigations_dict
from my_widgets import CBC, get_lab_normal_ranges
from labrequest import charges_dict
from my_widgets import createToolTip
from datetime import datetime

class TextEdit(Pmw.ScrolledText):
    def __init__(self, parent, *args, **kwargs):
        Pmw.ScrolledText.__init__(self, parent, *args, **kwargs)
        self.configure(text_height=6, text_wrap=WORD, text_width=30)

    def reset_height(self):
        # Must call Tk().update_idletasks for tkinter to know the width
        height= self.tk.call((self._w, "count", "-update","-lines", "1.0", "end"))
        self.configure(text_height= height)


class Laboratory:
    current_results=[]
    current_demographics=[]

    def __init__(self, parent=None, base=None):
        self.parent=parent
        self.base=base
        self.requested_tests=OrderedDict()
        self.requested=None

        self.results_list= []
        self.createUI()
        self.build_pending_list()


    def getconfig(self):
        config = configparser.ConfigParser()
        config.optionxform = str
        # print(os.path.exists("./server.ini"))
        # print(os.path.abspath("./server.ini"))
        if os.path.exists("./server.ini"):
            config.read("./server.ini")
            # If option not in custom, it falls back to default section
            host = config.get('CUSTOM', 'host')
            user = config.get('CUSTOM', 'user')
            password = config.get('CUSTOM', 'password')
            database = config.get('CUSTOM', 'database')
            table_name = config.get("CUSTOM", 'table_name')

            config = {
                "host": host,
                "user": user,
                "password": password,
                "database": database,
            }

            return config, table_name
        else:
            return None, None

    def createUI(self):
        top_btns=Frame(self.parent)
        top_btns.pack(fill=X, expand=0, anchor='n',pady=5)

        searchfrm =Frame(self.parent)
        search = AutocompleteEntry(searchfrm, self.base)
        search.ent.configure(width=50)
        search.ent.pack_configure(anchor='w')
        searchfrm.pack(fill=BOTH, expand=1, anchor='nw',pady=5)

        main=Frame(self.parent)
        main.pack(fill=BOTH, expand=0,pady=5)

        self.pending=Frame(main)
        self.pending.pack(fill=BOTH, expand=1,pady=5, anchor='n')

        self.resultsfrm=Frame(main)
        self.resultsfrm.pack(fill=BOTH, expand=1,pady=5)

        self.name=StringVar()
        client_selected=Label(top_btns,
            textvariable= self.name, fg='red', font='Consolas 16 bold')
        client_selected.pack(side=LEFT,anchor='nw',padx=50)

        bt= ttk.Button(top_btns, text="RESULTS", command=self.build_results_interface)
        bt.pack(side=LEFT, padx=50,pady=2)


    def build_pending_list(self):
        l=Label(self.pending, text="PENDING REQUESTS", font="Arial 14 bold")
        l.pack(expand=1)
        self.tree = Treeview(self.pending,
            ["DATE","PATIENT_ID", "FIRST NAME", "LAST NAME","AGE","SEX"], self)

        self.tree.pack(side='top', fill=BOTH, expand=1, anchor='center')
        self.tree.bind('<<TreeviewSelect>>', self.get_selection)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Calibri', 12))
        ttk.Style().configure("Treeview", background='lightcyan',
        font=('Calibri', 12), foreground='black', pady=4)
        ttk.Style().configure("TButton", background='powderblue',
        font=('Calibri', 12), foreground='blue', pady=4)
        self.tree.set_register(self.get_pending_requests())
        self.call_update()

    def call_update(self):
        self.parent.after(5000, self.update_pending)

    def update_pending(self):
        self.tree.set_register(self.get_pending_requests())
        self.call_update()

    def get_selection(self, event=None):
        '''Gets the item under focus and returns its rows in a list'''
        current_selection = event.widget.focus()
        rows = self.tree.item(current_selection)['values']
        if self.base is not None:
            self.name.set("ID: "+ str(rows[1])+" : " +rows[2] + " " + rows[3])
            self.base.find_by_id(pt_id=rows[1])
            self.ID= rows[1]
            self.requested = self.base.panel.get()

    def get_pending_requests(self):
        today = datetime.today().strftime("%d-%m-%Y")
        config, table_name = self.getconfig()
        sql= """SELECT DATE_SEEN, PATIENT_ID, FIRST_NAME, LAST_NAME, AGE, SEX
        FROM {} WHERE PAID_FOR_LAB="YES" AND SEEN_IN_LAB='NO' AND DATE_SEEN="{}"
        ORDER BY DATE_SEEN DESC""".format(table_name, today)
        conn = connect(**config)
        c= conn.cursor()
        c.execute(sql)
        pts= c.fetchall()
        conn.close()
        return pts


    def build_results_interface(self):
        self.toplevel = Toplevel()
        self.toplevel.title("eClinic-Results")
        self.toplevel.iconbitmap("./images/icon.ico")
        self.toplevel.geometry("{}x{}+0+0".format(self.toplevel.winfo_screenwidth(),
            self.toplevel.winfo_screenheight()))
        self.toplevel.overrideredirect(1)
        self.toplevel.focus()
        self.toplevel.grab_set()
        self.results_entries=OrderedDict()

        sf= Pmw.ScrolledFrame(self.toplevel, hull_width=1250, hull_height=700, usehullsize=1)
        sf.pack(expand=1, fill=BOTH, pady=10)

        top = sf.interior()

        particulars_frame = Frame(top, bg="powderblue")
        labfields = ("PATIENT_ID", "First Name", "Last Name",
            "Age", "Sex", "District", "Clinician")

        self.labfields_dict = OrderedDict()
        for index, field in enumerate(labfields):
            if index == 0:
                width = 5
            elif index==1:
                width=15
            elif index==2:
                width=15
            elif index==3:
                width=12
            elif index==4:
                width=12
            elif index==5:
                width = 15
            else:
                width=25

            frame = Frame(particulars_frame)
            frame.pack(side=LEFT)
            Label(frame, text=field, font="Arial 10 bold").pack(side=LEFT)
            ent = ttk.Entry(frame, width=width, font='Calibri 12', foreground='blue')
            ent.pack(side=LEFT)
            self.labfields_dict[field.upper().replace(" ", "_")] = ent

        particulars_frame.pack(expand=1, fill=X, anchor="n", pady=2, padx=2)

        demogsfrm = Frame(top, bg="powderblue")

        if self.base.department=="Laboratory":
            submit=ttk.Button(demogsfrm, text="SUBMIT",  command=self.set_results)
            submit.pack(side=LEFT)

            submit=ttk.Button(demogsfrm, text="CLOSE",  command=self.toplevel.destroy)
            submit.pack(side=LEFT, anchor='ne', padx=5, pady=4)

            submit=ttk.Button(demogsfrm, text="PRINT",  command=self.print_investigations)
            submit.pack(side=LEFT, anchor='ne', padx=5, pady=4)
        else:
            submit=ttk.Button(demogsfrm, text="CLOSE",  command=self.toplevel.destroy)
            submit.pack(side=RIGHT, anchor='ne', padx=5, pady=4)

            submit=ttk.Button(demogsfrm, text="PRINT",  command=self.print_investigations)
            submit.pack(side=LEFT, anchor='ne', padx=5, pady=4)

        demogsfrm.pack(expand=1, fill=BOTH, anchor="nw", pady=2, padx=2)

        cbc_frame = Frame(top, relief='flat', bg="SystemButtonFace")
        cbc_frame.pack(expand=1, fill=Y, anchor='w')

        LFrame = Frame(top)
        LFrame.pack(side=LEFT, expand=1, fill=BOTH, anchor='nw')

        RFrame = Frame(top)
        RFrame.pack(side=RIGHT, expand=1, fill=BOTH, anchor='nw', padx=5)
        x1 = 0
        x2 = 0

        requested=self.update_requested_dict().items()
        keys= list(self.update_requested_dict().keys())
        for group, tests in requested:
            if x1 <= len(keys)//2:
                GRP = Pmw.Group(LFrame, tag_text=group, tag_font="Arial 12 bold", tag_foreground='navyblue')
                GRP.grid(row=x1, column=0, sticky='nsew', padx=5, pady=5)
                x1 += 1
            else:
                GRP = Pmw.Group(RFrame, tag_text=group, tag_font="Arial 12 bold", tag_foreground='navyblue')
                GRP.grid(row=x2, column=1, sticky='nw', padx=5, pady=5)
                x2 += 1

            for i, field in enumerate(tests):
                key = field.upper().replace(" ", "_")
                if field == "CBC":
                    entry = CBC(cbc_frame, self)  # Must attach parent_self to print
                else:
                    label = Label(GRP.interior(), text=field, font='Calibri 12')
                    label.grid(row=i, column=0, sticky='e')
                    entry= ttk.Entry(GRP.interior(), width=50)
                    entry.configure(font='Consolas 13')
                    entry.grid(row=i, column=1, pady=2, padx=2)

                createToolTip(entry)

                self.results_entries[field]=entry

        demos=[self.base.entries[field].get() for field in self.labfields_dict]
        for i, field in enumerate(labfields):
            self.labfields_dict[field.upper().replace(" ","_")].insert(0, demos[i])

        for test in self.current_results: # Update if delete of test
            if isinstance(test, tuple):
                key= test[0]
                result = test[1]
                try:
                    w = self.results_entries[key]
                    w.insert(0, result)
                except KeyError:
                    pass


    def process_results(self):
        tests = Laboratory.current_results
        if not tests:
            showinfo("Unable to print", "No results to print")
            return

        table_data = []

        NR_DICT, UNITS_DICT = get_lab_normal_ranges()

        try:
            for key, value in tests:
                if value != "" and key !="CBC":
                    try:
                        field_value = float(value)
                        LOWERLIMIT, UPPERLIMIT = NR_DICT[key].split(',')
                        if field_value < float(LOWERLIMIT):
                            FLAG = 'L'
                        elif field_value > float(UPPERLIMIT):
                            FLAG = 'H'
                        else:
                            FLAG = 'N.R'
                        unit = UNITS_DICT[key]
                        ref_range = '-'.join(NR_DICT[key].split(',')) + str(unit)
                    except KeyError as e:
                        FLAG = ""
                        ref_range = ""
                    except ValueError:
                        FLAG = ""
                        ref_range = ""
                        field_value = value
                    except TypeError:
                        pass
                    table_data.append((key, field_value, FLAG, ref_range))

                if value != "" and key =="CBC":
                    try:
                        self.results_entries["CBC"].print("documents/CbcReport.docx")
                    except:
                        pass

            return table_data
        except ValueError:
            return []

    def print_investigations(self):
        data= self.process_results()
        if data:
            self.base.print_investigations(data)
            return data


    def get_cbc_details(self):
        cbc = self.results_entries["CBC"]

        cbc.set_footer_text("Thank you coming to us!")
        if self.base.phone_number:
            cbc.set_phone(self.base.phone_number)
        cbc.set_patient_detail(
            self.base.entries["PATIENT_ID"].get(),
            self.base.entries["FIRST_NAME"].get() + " " +
            self.base.entries["LAST_NAME"].get(),
            self.base.entries["AGE"].get(),
            self.base.entries["SEX"].get())
        return self.base.form_header

    def check_if_logo(self, document):
        return self.base.check_if_logo(document)

    def update_requested_dict(self):
        tests = self.base.panel.get()
        for key in investigations_dict.keys():
            # Create empty categories
            self.requested_tests[key] = []
            for test in tests:
                if test in investigations_dict[key]:
                    # Populate categories with matching tests
                    self.requested_tests[key].append(test)

        # Remove empty categories
        for key in investigations_dict.keys():
            if self.requested_tests[key] == []:
                self.requested_tests.pop(key, None)
        return self.requested_tests

    def set_results(self):
        for test, entry in self.results_entries.items():
            value = entry.get()
            self.results_list.append((test,value))

        self.toplevel.destroy()
        self.update()

    def get(self):
        return self.results_list

    def update(self):
        if self.base.department=="Laboratory":
            self.base.update_results(self.results_list)

    def delete(self,index1=0, index2=END):
        for entry in self.results_entries.values():
            try:
                entry.delete(0, END)
            except:
                entry.delete("1.0", END)


    def insert(self, index, values):
        import ast
        try:
            values = ast.literal_eval(values)
        except Exception as e:
            values=[]

        Laboratory.current_results= values
        demos = " ".join([self.base.entries[field].get() for field in ["PATIENT_ID","FIRST_NAME", "LAST_NAME"]])
        self.name.set(demos)

if __name__ == '__main__':
    Laboratory(Tk())
    mainloop()
