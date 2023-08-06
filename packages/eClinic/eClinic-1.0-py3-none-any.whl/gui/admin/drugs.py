import os, sys
path=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(path)
from tkinter import *
from tkinter import ttk
from collections import OrderedDict
from my_widgets import Treeview, createToolTip
from tkinter.messagebox import *


class Drugs:
    def __init__(self, frame, base):
        self.frame = frame # Frame if a tople
        self.frame.configure(padx=10, pady=5)
        self.base = base
        self.connection = self.base.get_connection()
        self.entries=OrderedDict()

        self.fields = ("DrugID", "DrugName", "Cost")

        self.initUI()

    def initUI(self):
        for i, field in enumerate(self.fields):
            label = Label(self.frame, text= field, font="Consolas 14")
            entry = Entry(self.frame, width=60, font="Consolas 14")
            label.grid(row=i+2, column=0, padx=2,pady=2)
            entry.grid(row=i+2, column=1, pady=2)
            self.entries[field]=entry

        self.create_btns()
        self.create_tree()

    def create_btns(self):
        n= len(self.fields)
        btnframe = Frame(self.frame)
        btnframe.grid(row=n+2, columnspan=5, pady=10)

        FONT="Consolas 12"
        BG="powderblue"
        b1= ttk.Button(btnframe, text="CLEAR", command=self.clear)
        b2= ttk.Button(btnframe, text="SAVE", command= self.save)
        b3= ttk.Button(btnframe, text="UPDATE", command= self.update)
        b4= ttk.Button(btnframe, text="DELETE", command=self.delete)
        b5= ttk.Button(btnframe, text="CLOSE", command=self.close)

        prev= ttk.Button(btnframe, text="<<", command=self.find_prev)
        nxt= ttk.Button(btnframe, text=">>", command=self.find_next)

        b1.pack(side=LEFT, padx=2)
        b2.pack(side=LEFT, padx=2)
        b3.pack(side=LEFT, padx=2)
        b4.pack(side=LEFT, padx=2)
        b5.pack(side=LEFT, padx=2)

        prev.pack(side=LEFT, padx=2)
        nxt.pack(side=LEFT, padx=2)

    def create_tree(self):
        treeframe = Frame(self.frame)
        treeframe.grid(row=len(self.fields)+4, columnspan=5, pady=10,sticky='nsew')

        self.tree = Treeview(treeframe,
            parent_self=self, style='T.Treeview', headers=["DrugID", "DrugName", "Cost"])
        self.tree.pack(side='bottom', fill=BOTH, expand=1)
        self.load_register()
        self.tree.set_register(self.REGISTERED)

    def find_by_id(self, pt_id=None):
        sql = """SELECT * FROM drugs WHERE DrugID="%s" """%pt_id
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            fields= cursor.description
            self.clear()
            for i in range(len(fields)):
                field = self.entries.get(fields[i][0])
                if isinstance(field, Entry):
                    field.insert(0, results[0][i])
                else:
                    field.set(results[0][i])

    def load_register(self):
        sql = "SELECT DrugID, DrugName, Cost FROM drugs"
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            self.REGISTERED= results

    def clear(self):
        [e.delete(0,END) for e in self.entries.values()]

    def save(self):
        data = []
        keys=[]
        for key in self.entries.keys():
            data.append(self.entries[key].get())
            keys.append(key)

        num_columns = len(data)
        data = tuple(data)
        keys = ", ".join(keys)

        query = '''INSERT INTO drugs ({})
        VALUES('''.format(keys) + """ "%s",""" * num_columns % (data)
        query = query[:-1] + ")"
        if self.connection:
            cursor = self.connection.cursor()
            try:
                cursor.execute(query)
                self.connection.commit()
                self.load_register()
                self.tree.set_register(self.REGISTERED)
                showinfo("Admin","Saved OK")
            except Exception as e:
                showerror("Admin", str(e))

    def update(self):
        DrugID = self.entries["DrugID"].get()
        if DrugID:
            entryItems = self.entries.items()
            query = "UPDATE drugs SET"
            for key, value in entryItems:
                if not key == "DrugID":
                    text = value.get()
                    query += """ %s = "%s",""" % (key, text)
            query = query[:-1] + " WHERE DrugID = %s " % DrugID

            if self.connection:
                try:
                    c= self.connection.cursor()
                    c.execute(query)
                    self.connection.commit()
                    self.load_register()
                    self.tree.set_register(self.REGISTERED)
                    showinfo("Admin", "Updated Ok")
                except Exception as e:
                    showerror("Admin", str(e))

    def delete(self):
        DrugID = self.entries["DrugID"].get()
        if DrugID:
            ans = askquestion("Confirm",
                "Delete %s from drugs?"%self.entries["DrugName"].get())
            if not ans =="yes":return
            sql= "DELETE FROM drugs WHERE DrugID='%s'"%DrugID
            if self.connection:
                try:
                    cursor=self.connection.cursor()
                    cursor.execute(sql)
                    self.connection.commit()
                    self.load_register()
                    self.tree.set_register(self.REGISTERED)
                    showinfo("Admin", "Deleted OK")
                except Exception as e:
                    showerror("Admin", str(e))

    def find_next(self):
        try:
            _next = int(self.entries["DrugID"].get()) +1
            self.find_by_id(pt_id= _next)
        except:
            return

    def find_prev(self):
        try:
            prev = int(self.entries["DrugID"].get()) -1
            self.find_by_id(pt_id= prev)
        except:
            return

    def close(self):
        self.frame.destroy()


if __name__ == '__main__':
    admin = Drugs(Tk(), None)
    mainloop()