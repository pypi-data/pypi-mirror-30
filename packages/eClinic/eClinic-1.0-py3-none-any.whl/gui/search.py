from tkinter import *
from tkinter.messagebox import *
import os, configparser
from mysql.connector import connect

class AutocompleteEntry(Frame):
    def __init__(self, frame, parent):
        Frame.__init__(self)

        self.SearchQuery()
        var = StringVar()
        self.frame = frame
        self.parent = parent
        self.ent = Entry(self.frame, textvariable=var, width=35)
        self.ent.configure(font="Calibri 18 bold", fg="green", bg='lightcyan')
        self.ent.focus()
        self.ent.pack(side='top', fill=Y, pady=2)
        self.var = var
        if self.var == '':
            self.var = self["textvariable"] = StringVar()
        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.up)
        self.bind("<Down>", self.down)
        self.lb_up = False

    def getconfig(self):
        config = configparser.ConfigParser()
        config.optionxform = str
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

    def SearchQuery(self, where=None):
        conf = self.getconfig()
        if conf is not None:
            config, table= conf[0], conf[1]
        else:
            self.PATIENTLIST=[]
            return

        self.PATIENTLIST = []
        query = "SELECT * FROM {} ".format(table)
        if where is not None:
            query += where

        connection= connect(**config)
        cursor = connection.cursor()
        try:
            cursor.execute(query)
        except Exception as e:
            print(e)
            return "Search failed", str(e)
        else:
            results = cursor.fetchall()
            for row in results:
                ip_no = row[0]
                first_name = row[1]
                last_name = row[2]
                name = ip_no + " " + first_name + " " + last_name
                if name not in self.PATIENTLIST:
                    self.PATIENTLIST.append(name)
                else:
                    pass

            cursor.close()
            connection.close()
            return connection, True

    def changed(self, name, index, mode):
        # Keep track of the updates by calling Search function every keypress
        self.SearchQuery()
        if self.var.get() == '':
            try:
                self.lb.destroy()
                self.sbar.destroy()
                self.lb_up = False
            except:
                pass
        else:
            words = self.comparison()
            if words:
                if not self.lb_up:
                    self.sbar = Scrollbar(self.frame)
                    self.lb = Listbox(self.frame, relief=SUNKEN)
                    self.sbar.config(command=self.lb.yview)  # xlink sbar and list
                    self.lb.config(yscrollcommand=self.sbar.set)  # move one moves other
                    self.sbar.pack(side=RIGHT, fill=Y, padx=1)  # pack first=clip last
                    self.lb.pack(side=LEFT, expand=YES, fill=BOTH)  # list clipped first
                    self.lb.config(font=('arial', 12, 'bold'), fg='navy', height=5)
                    self.lb.bind("<Double-Button-1>", self.selection)
                    self.lb.bind("<Return>", self.selection)
                    self.lb_up = True

                self.lb.delete(0, END)
                for w in words:
                    self.lb.insert(END, w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.sbar.destroy()
                    self.lb_up = False

    def selection(self, event):
        if self.lb_up:
            self.var.set(self.lb.get(ACTIVE))
            self.lb.destroy()
            self.sbar.destroy()
            self.lb_up = False
            item = self.ent.get().split(" ")
            ip_no = item[0]
            self.parent.find_by_id(pt_id=ip_no)
            self.ent.delete(0, 'end')

    def up(self, event):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != '0':
                self.lb.selection_clear(first=index)
                index = str(int(index) - 1)
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def down(self, event):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != END:
                self.lb.selection_clear(first=index)
                index = str(int(index) + 1)
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def comparison(self):
        try:
            pattern = re.compile('.*' + self.var.get() + '.*', re.I | re.M)
            return [w for w in self.PATIENTLIST if re.match(pattern, w)]
        except:
            pass

if __name__ == '__main__':
    AutocompleteEntry(Tk(), parent=None)
    mainloop()