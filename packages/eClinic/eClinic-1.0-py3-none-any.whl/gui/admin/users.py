import os, sys
sys.path.append("../")
from tkinter import *
from tkinter import ttk
from collections import OrderedDict
from my_widgets import Treeview
from tkinter.messagebox import *


class Users:
    def __init__(self, frame, base):
        self.frame = frame
        self.frame.configure(padx=10, pady=5)
        self.base = base
        self.connection = self.base.get_connection()
        self.entries=OrderedDict()
        self.users_table="users"
        self.fields = ("UserID","FirstName","LastName",
            "Username","Department","Title","Password")

        self.initUI()

    def initUI(self):
        for i, field in enumerate(self.fields):
            label = Label(self.frame, text= field, font="Consolas 14")
            if field=="Department":
                entry = ttk.Combobox(self.frame, width=42, font="Consolas 12")
                entry['values']=['Clinician',"Reception",'Laboratory',
                "Cashier","Administrator", "Pharmacy"]
            else:
                entry = Entry(self.frame, width=40, font="Consolas 14")

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
            parent_self=self, style='T.Treeview', headers=["UserID", "FirstName", "LastName"])
        self.tree.pack(side='bottom', fill=BOTH, expand=1)
        self.load_register()
        self.tree.set_register(self.REGISTERED)

    def find_by_id(self, pt_id=None):
        sql = """SELECT * FROM users WHERE UserID="%s" """%pt_id
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
        sql = "SELECT UserID, FirstName, LastName FROM users"
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

        query = '''INSERT INTO users ({})
        VALUES('''.format(keys) + """ "%s",""" * num_columns % (data)
        query = query[:-1] + ")"
        if self.connection:
            cursor = self.connection.cursor()
            try:
                cursor.execute(query)
                self.connection.commit()
                self.load_register()
                self.tree.set_register(self.REGISTERED)
                showinfo("Users","Saved OK")
            except Exception as e:
                showerror("Users", str(e))

    def update(self):
        userid = self.entries["UserID"].get()
        if userid:
            entryItems = self.entries.items()
            query = "UPDATE users SET"
            for key, value in entryItems:
                if not key == "UserID":
                    text = value.get()
                    query += """ %s = "%s",""" % (key, text)
            query = query[:-1] + " WHERE UserID = %s " % userid

            if self.connection:
                try:
                    c= self.connection.cursor()
                    c.execute(query)
                    self.connection.commit()
                    self.load_register()
                    self.tree.set_register(self.REGISTERED)
                    showinfo("Users", "Updated Ok")
                except Exception as e:
                    showerror("Users", str(e))

    def delete(self):
        userid = self.entries["UserID"].get()
        if userid:
            ans = askquestion("Confirm",
                "Delete %s from clients?"%self.entries["FirstName"].get())
            if not ans =="yes":return
            sql= "DELETE FROM users WHERE UserID='%s'"%userid
            if self.connection:
                try:
                    cursor=self.connection.cursor()
                    cursor.execute(sql)
                    self.connection.commit()
                    self.load_register()
                    self.tree.set_register(self.REGISTERED)
                    showinfo("Users", "Deleted OK")
                except Exception as e:
                    showerror("Users", str(e))

    def find_next(self):
        try:
            _next = int(self.entries["UserID"].get()) +1
            self.find_by_id(pt_id= _next)
        except:
            return

    def find_prev(self):
        try:
            prev = int(self.entries["UserID"].get()) -1
            self.find_by_id(pt_id= prev)
        except:
            return

    def close(self):
        self.frame.destroy()


if __name__ == '__main__':
    admin = Users(Tk(), None)
    mainloop()