import tkinter.ttk as ttk
from tkinter import Tk, Frame, BOTH, WORD, font
# from datefield import Datepicker

class Treeview(ttk.Treeview):
    def __init__(self, parent, headers, parent_self, *args, **kwargs):
        ttk.Treeview.__init__(self, parent,  columns = headers, show="headings", height=2, *args, **kwargs)

        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=self.xview)
        self.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill="y", anchor='w')
        hsb.pack(side='bottom', fill="x")

        self.parent = parent
        self.headers = headers
        self.current_selection = None
        self.parent_self= parent_self
        self.bind("<<TreeviewSelect>>", self.get_selection)
        self._build_tree()

    def _build_tree(self):
        for col in self.headers:
            self.heading(col, text=col, anchor='w',command=lambda c=col: self.sortby(self, c, 0))
            # adjust the column's width to the header string
            self.column(col, anchor='nw', width=100)

    def sortby(self, tree, col, descending):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        tree.heading(col, command=lambda col=col: self.sortby(tree, col, int(not descending)))

    def fill_tree(self):
        # Delete children and repopulate
        self.delete(*self.get_children())

        if self.register is not None:
            for item in self.register:
                self.insert('', 'end', values=item)  # Returns row-id
                # adjust column's width if necessary to fit each value
                try:
                    for ix, val in enumerate(item):
                        col_w = font.Font().measure(val)
                        if self.column(self.headers[ix], width=None) < col_w:
                            self.column(self.headers[ix], width=col_w)
                except TypeError:
                    raise TypeError("Tree_list must be a list of tuples")

    def get_selection(self, event=None):
        if event:
            current_selection = event.widget.focus()
            rows = self.item(current_selection)['values']
            self.current_selection = rows
            ip_no = rows[1]
            self.parent_self.find_by_id(pt_id = ip_no)

    def set_register(self, register):
        self.register = register
        self.update_tree()

    def update_tree(self):
        self.clear()
        self.fill_tree()

    def clear(self):
        self.delete(*self.get_children())

    def get_all(self):
        return [item for item in self.get_children()]