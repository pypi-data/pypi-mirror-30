import sys
sys.path.append("../")

from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont
from tkinter.messagebox import askquestion, showinfo, showerror
import Pmw
from collections import OrderedDict
from my_widgets import Treeview
from search import AutocompleteEntry
from admin import Drugs
from spreadsheets import PrescriptionSheet, ProceduresSheet, UsablesSheet,Receipt
from datetime import datetime
import ast

class Pharmacy:
    def __init__(self, frame, base=None):
        self.frame= frame
        self.base = base
        self.entries=OrderedDict()
        self.updatable=OrderedDict()

        if self.base:
            self.connection = self.base.get_connection()

        self.initUI()

    def initUI(self):
        F2= Frame(self.frame, relief='ridge', bd=4)
        F3= Frame(self.frame)
        F2.pack(fill=X) # next top for controls/toolbar

        F3.pack(expand=1, fill=BOTH)
        # PanedWidget to hold bottom frame
        pane= PanedWindow(F3, orient=HORIZONTAL)
        pane.pack(expand=1, fill=BOTH)

        F4= Frame(pane) # Left main
        F5= Frame(pane) # Right Main

        pane.add(F4)
        pane.add(F5)

        F6= Frame(F4) # Left top # treeview
        F7= Frame(F4) # Left bottom # Search

        F6.pack(expand=0, fill=None, anchor='nw') # Left top # treeview
        F7.pack(expand=0, fill=Y, anchor='nw') # Left bottom # Search

        F8= Frame(F5) # Right top # Main UI
        F8.pack(expand=1, fill=BOTH)

        # Controls
        self.today= datetime.today().strftime("%d-%m-%Y")

        conn= self.connection
        if conn:
            c= conn.cursor()
            c.execute("SELECT DATE_SEEN FROM {}".format(self.base.table_name))
            dates= c.fetchall()
            if dates:
                cbolist=[date[0] for date in dates]
                cbolist.append(self.today)
            else:
                cbolist=[]

        else:
            cbolist=self.today

        Label(F2, text="Filter Dates: ").pack(side=LEFT)
        self.cbo= ttk.Combobox(F2, width=20, values=cbolist)
        self.cbo.pack(side=LEFT)
        self.cbo.set(self.today)

        # LEFT FRAME WIDGETS
        demos= Frame(F6)
        demos.pack(fill=None, expand=0, anchor='nw')
        self.create_demos(demos)

        pending= Pending(F6, self, self.connection, self.base.table_name)

        # Search
        engine= AutocompleteEntry(F4, self)
        engine.ent.configure(width=25)
        engine.ent.pack_configure(expand=0, fill=None, anchor='w')

        self.create_management(F8)
        self.create_buttons(F2)
        # self.find_pending()

    def create_buttons(self, btnframe):
        self.base.style.configure("P.TButton", background='powderblue',
                        font='Calibri 12 bold', foreground='blue', padding=3)

        b4= ttk.Button(btnframe, text="EXIT", command=self.close, style='P.TButton')
        b3= ttk.Button(btnframe, text="UPDATE", command= self.update, style='P.TButton')
        b2= ttk.Button(btnframe, text="DRUGS", command= self.view_drugs, style='P.TButton')
        b1= ttk.Button(btnframe, text="CLEAR", command=self.clear, style='P.TButton')
        rect= ttk.Button(btnframe, text="RECEIPT", command=self.show_receipt, style='P.TButton')

        b4.pack(side=RIGHT, padx=10)
        b3.pack(side=RIGHT, padx=2)
        b2.pack(side=RIGHT, padx=2)
        b1.pack(side=RIGHT, padx=2)
        rect.pack(side=RIGHT, padx=10)

    def create_demos(self, f):
        fields=["Patient ID", "First Name", "Last Name",
        "Age", "Sex", "Date Seen","Time Seen",
        "Paid For Drugs", "Drugs Given"]

        for i, field in enumerate(fields):
            Label(f, text=field).grid(row=i, column=0, sticky='e')
            if field=="Paid For Drugs" or field=="Drugs Given":
                entry = ttk.Combobox(f, width=33,
                    font="Calibri 10 bold", values=["YES","NO"])
            else:
                entry = ttk.Entry(f, width=40)

            entry.grid(row=i, column=1,pady=1)
            key = field.upper().replace(" ", "_")
            self.entries[key] = entry

    def create_management(self, frame):
        pane2= PanedWindow(frame, orient=VERTICAL, bg='powderblue')
        pane2.pack(expand=1, fill=BOTH, pady=8)

        drugs_frame = Pmw.ScrolledFrame(pane2)
        pane2.add(drugs_frame)

        drugs= PrescriptionSheet(1, 10,
            ["Drug ID", "Form/Route", "Drug Name","Dose","Freq",
            "Instructions","Days","Qty","Unit Cost","Subtotal"],
            drugs_frame.interior(), base=self.base)
        self.entries["MANAGEMENT"]= drugs
        drugs.build_sheet()

        usables_frame = Pmw.ScrolledFrame(pane2)
        pane2.add(usables_frame)
        usables= UsablesSheet(1, 5,
            ["Item ID", "Item Name", "Cost", "Qty", "Subtotal"],
            usables_frame.interior(), base=self.base)
        self.entries["USABLES"]= usables
        usables.build_sheet()

    def show_receipt(self):
        ID= self.entries["PATIENT_ID"].get()
        if ID !="":
            top=Toplevel()
            top.title("e-Clinic Payments")
            top.iconbitmap('images/icon.ico')
            top.focus()
            top.grab_set()
            top.configure(padx=5, pady=5)
            top.resizable(0,0)

            payslip = Receipt(top)
            self.fill_receipt(ID, payslip)

    def fill_receipt(self, ID, receipt):
        conn= self.connection
        if conn:
            c= conn.cursor()
            c.execute("""
                SELECT PAYMENT FROM {}
                WHERE PATIENT_ID='{}'
                """.format(self.base.table_name, ID))
            pay = c.fetchone()

            try:
                pay = ast.literal_eval(pay[0])
                receipt.insert(0, pay)
            except: # I expect pay[0] to be a "[]" eval can work on
                pass

    def view_drugs(self):
        top = Toplevel()
        top.title("Drugs")
        top.resizable(0,0)
        top.focus()
        top.grab_set()
        top.iconbitmap("./images/icon.ico")
        drugs= Drugs(top, base=self.base)

    def update(self):
        if self.entries['PATIENT_ID'].get() != '' \
            and self.entries['FIRST_NAME'].get() != '':
            query = "UPDATE {} SET".format(self.base.table_name)
            query += """ DRUGS_GIVEN = "%s" """ % (self.entries["DRUGS_GIVEN"].get())

            c= self.connection.cursor()
            c.execute(query)
            self.connection.commit()
            showinfo("Pharmacy", "Updated that all drugs and items were dispensed")
        else:
            showinfo("Pharmacy", "Select a client")

    def find_by_id(self, pt_id=None):
        cursor= self.connection.cursor()
        query = """SELECT PATIENT_ID, FIRST_NAME, LAST_NAME,
        AGE, SEX,  DATE_SEEN, TIME_SEEN, PAID_FOR_DRUGS, DRUGS_GIVEN,
        MANAGEMENT, USABLES
        FROM {} """.format(self.base.table_name) + "WHERE PATIENT_ID ='%s'" % pt_id
        try:
            cursor.execute(query)
        except Exception as e:
            showerror("Exception in Look up", str(e))
        else:
            results= cursor.fetchall()
            fields = cursor.description

            if results:
                for f in self.entries.values():
                    f.delete(0, END)
                for i in range(len(fields)):
                    field = self.entries.get(fields[i][0])
                    if isinstance(field, ttk.Combobox):
                        field.set(results[0][i])
                    else:
                        field.insert(0, results[0][i])

    def clear(self):
        [ent.delete(0, END) for ent in self.entries.values()]

    def close(self):
        self.base.close()

class Pending:
    def __init__(self, parent, base, connection, table):
        self.connection= connection
        self.base = base
        self.table_name = table
        self.parent=parent

        l=Label(self.parent, text="PENDING PATIENTS", font="Arial 8 bold")
        l.pack(anchor='nw')

        self.tree = Treeview(self.parent,
            ["Date","ID", "FirstName","LastName"], self.base)

        self.tree.pack(fill=BOTH, expand=1, anchor='nw')
        self.tree.bind('<<TreeviewSelect>>', self.get_selection)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Courier', 10, 'bold'))
        ttk.Style().configure("Treeview", background='lightcyan',
        font=('Calibri', 10, 'bold'), foreground='black', pady=4)
        ttk.Style().configure("TButton", background='powderblue',
        font=('Calibri', 10, 'bold'), foreground='blue', pady=4)
        self.tree.set_register(self.get_pending_requests())
        self.tree.set_col_width(95)
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
        self.base.find_by_id(pt_id=rows[1])

    def get_pending_requests(self):
        sql= """SELECT DATE_SEEN, PATIENT_ID, FIRST_NAME,LAST_NAME
        FROM {} WHERE SEEN_BY_DOC="YES" AND PAID_FOR_DRUGS='YES'
        AND DRUGS_GIVEN="NO" AND DATE_SEEN='{}'
        ORDER BY DATE_SEEN DESC""".format(self.table_name, self.base.cbo.get())

        c= self.connection.cursor()
        c.execute(sql)
        pts= c.fetchall()
        return pts


