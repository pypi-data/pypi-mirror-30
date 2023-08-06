import sys
sys.path.append("../")
import os
from tkinter import *
import pyautogui
from my_widgets import word_docx, numbers


class Receipt(Frame):
    """docstring for [Receipt class]."""
    def __init__(self, parent, base=None):
        super(Receipt, self).__init__()
        self.parent = parent
        self.base = base
        self.rows=10
        self.columns=4
        self.build()


    def build(self):
        self.headers=["ITEM","CHARGE","PAID","BALANCE"]
        side_headers=["Consultation", "Laboratory","Radiology",
                     "Medication", "Procedures","Usables",
                     "Nursing Care", "Medical Reviews","TOTALS"]

        for i in range(self.rows):
            for j in range(self.columns):
                ent= Entry(self.parent, width=15)
                ent.grid(row=i,column=j,padx=1)
                ent.configure(font="Calibri 14 bold")
                ent.bind("<KeyRelease>", self.changed)

                if i ==0:
                    ent.insert(0, self.headers[j])
                    ent.config(relief='raised', bd=2)
                    ent['state']=DISABLED
                if j==0 and i>0:
                    ent.insert(0, side_headers[i-1])
                    ent.config(relief='raised', bd=2)
                    ent['state']=DISABLED
                if j==3:
                    ent.bind("<Key>", self.disable_typing)
                    ent.configure(fg='brown')

                if i==(self.rows-1) and j==1 or i==(self.rows-1) and j==2 \
                or i==(self.rows-1) and j==3:
                    ent.bind("<Key>", self.disable_typing)
                    ent.bind("<Enter>", self.show_words)
                    ent.bind("<Leave>", self.remove_words)

        p = Button(self.parent, text="Print Receipt", cursor='hand2', fg="blue",
            command= self._print, bg="powderblue", font="Consolas 14 bold")
        p.grid(row=self.rows+1, column=3, stick='ew', pady=4)

        self.number=Label(self.parent, text="", justify='left', wraplength=500,
            font='Calibri 12')
        self.number.grid(column=0, columnspan=10, sticky='w',pady=4)


    def _print(self):
        from datetime import datetime
        date_time=datetime.now().strftime("%A, %d-%m-%Y  %I:%M:%S %p")
        doc = word_docx.MyDocument()
        if self.base:
            doc= self.base.check_if_logo(doc)
            names= self.base.entries['FIRST_NAME'].get() + " " + \
                   self.base.entries['LAST_NAME'].get()
            paymentid= self.base.entries['PATIENT_ID'].get()

            name = doc.add_paragraph("NAME:   {}  ".format(names))
            doc.add_text(name, "\tReceipt NO:   {}".format(paymentid))

        data= self.get_table_data()
        table= doc.add_table("Receipt for Medical Bills   {}".format(date_time), self.headers, data )
        table.style = 'Medium Shading 1 Accent 5'
        doc.save(os.path.abspath("./documents/receipt.docx"))
        os.startfile(os.path.abspath("./documents/receipt.docx"))


    def changed(self, event):
        if event.widget.get() !="":
            value = event.widget.get()
            try:
                cost= int(value)
            except:
                pyautogui.hotkey("BACKSPACE")
            else:
                event.widget.configure(background='white')
        else:
            event.widget.configure(background='yellow')

        self.compute()

    def disable_typing(self, event):
        return "break"

    def cell(self, i, j):
        info = self.grid_info()
        for w in self.parent.children.values():
            if isinstance(w, Entry):
                if w.grid_info()['row']==i and w.grid_info()['column']==j:
                    return w

    def delete(self, *args):
        return [w.delete(0, 'end') for w in self.parent.children.values()]

    def insert(self, index:int, values:list):
        i=1
        for row in values:
            j=1; x=0
            while j<self.columns:
                cell = self.cell(i, j)
                cell.delete(0, END)
                cell.insert(0, row[x])
                j +=1
                x +=1
            i +=1
        self.compute()

    def get(self, event=None):
        all_rows=[]
        for i in range(1, self.rows):
            rows=[]
            j=1
            while j< self.columns:
                cell = self.cell(i, j)
                rows.append(cell.get())
                j +=1
            all_rows.append(tuple(rows))

        return all_rows

    def get_table_data(self):
        all_rows=[]
        for i in range(1, self.rows):
            rows=[]
            j=0
            while j< self.columns:
                cell = self.cell(i, j)
                if j==0:
                    cell.configure(state=NORMAL)
                    rows.append(cell.get())
                    cell.configure(state=DISABLED)
                else:
                    rows.append(cell.get())

                j +=1
            all_rows.append(tuple(rows))

        return all_rows

    def compute(self, event=None):
        all_rows = self.get()

        sub_charges=[]
        sub_paid=[]

        for i in range(1, self.rows-1):
            datarow=[]
            bal_widgets=[]

            j=1
            while j< self.columns:
                cell = self.cell(i, j)
                if j==3:
                    bal_widgets.append(cell)
                try:
                    datarow.append(int(cell.get()))
                except ValueError:
                    datarow.append(0)

                if j==1:
                    value= cell.get()
                    try:
                        c = int(value)
                    except ValueError:
                        c=0
                    sub_charges.append(c)
                elif j==2:
                    value= cell.get()
                    try:
                        c = int(value)
                    except ValueError:
                        c=0
                    sub_paid.append(c)

                j +=1

            charge = datarow[0]
            paid=datarow[1]
            try:
                bal= int(charge)-int(paid)
                bal_widgets[0].delete(0, END)
                bal_widgets[0].insert(0, bal)
            except:
                raise

            tot_charge= self.cell(self.rows-1, 1)
            tot_charge.configure(foreground='blue')
            tot_paid = self.cell(self.rows-1, 2)
            tot_paid.configure(foreground='green')
            tot_balance = self.cell(self.rows-1, 3)
            tot_balance.configure(foreground='red')

            if tot_charge and tot_paid:
                tot_charge.delete(0, END)
                tot_paid.delete(0, END)

                tot_charge.insert(0, self.sep(sum(sub_charges)))
                tot_paid.insert(0, self.sep(sum(sub_paid)))

        tot_balance.delete(0, END)
        tot_balance.insert(0, self.sep(sum(sub_charges)-sum(sub_paid)))

    def sep(self, s, thou=", ", dec="."):
        try:
            '''Generates thousand seperators'''
            if str(s).isdigit():
                s = str(s) + '.0'
            integer, decimal = str(s).split(".")
            integer = re.sub(r"\B(?=(?:\d{3})+$)", thou, integer)
            return integer
        except:
            return ""

    def show_words(self, event):
        if event.widget.cget("state")==NORMAL:
            num = event.widget.get()
        else:
            event.widget["state"]=NORMAL
            num = event.widget.get()
            event.widget["state"]=DISABLED

        if num:
            try:
                num= str(num).replace(", ", "")
                num = int(num)
            except Exception as e:
                self.top=None
            else:
                self.number.configure(text=str(numbers.num2name(num)).title())

    def remove_words(self, event):
        self.number.configure(text="")

if __name__ == '__main__':
    root= Tk()
    rec = Receipt(root)
    mainloop()
