import datetime
import os
import tkinter.ttk as ttk
from collections import OrderedDict
from tkinter import *
from tkinter.messagebox import *
from tkinter.scrolledtext import ScrolledText
from Normal_Ranges import get_normal_ranges
from word_docx import MyDocument
import table

class CBC(Frame):
    # Set class variables for the CBC Report
    reg = ""
    name = ""
    age = ""
    sex = ""
    date = datetime.datetime.today().strftime("%d/%m/%Y   %I:%M:%S %p")
    footer_text = "Thank you for coming. We promise to be there for you!"
    phone = "No Phone Set"
    lab_tech = None

    def __init__(self, parent=None, parent_self=None, **kwargs):
        Frame.__init__(self, parent, width= 1000, relief='ridge', borderwidth=4, background='powderblue')

        self.parent_self = parent_self

        if "print" not in kwargs:
            self.pack(fill=BOTH, expand=1)

        fields = [
            "WBC", "LY#", "MO#", "GR#", "LY%", "MO%", "GR%", "RBC",
            "HGB", "HCT", "MCV", "MCH", "MCHC", "RDW CV", "RDW SD",
            "PLT", "MPV", "PDW", "PCT"]

        self.entries = OrderedDict()
        self.print_ = False
        # Create table if not exists

        frametop = Frame(self)
        frametop.grid(row=0, column=0)
        frametop.config(background='powderblue')

        frame = Frame(self)
        frame.grid(row=1, column=0)
        frame.config(background='powderblue')

        for index, field in enumerate(fields):
            label = Label(frame, text=field, font='Arial 10 bold', background='powderblue')
            label.grid(row=index + 1, column=0, sticky='e')

            entry = ttk.Entry(frame, text=field, width=28)
            entry.grid(row=index + 1, column=1, pady=2)

            key = field.upper().replace(" ", "_").replace("%", "_PERC").replace("#", '')
            self.entries[key] = entry

        frame2 = Frame(self, background="powderblue")
        frame2.grid(row=0, column=0, pady=5, sticky="n")

        btnfont = 'Calibri 12'
        Button(frame2, text='CLEAR', font=btnfont, foreground='blue', command=self.clearContents).pack(side='left',padx=10)

        Button(frame2, text='PRINT PREVIEW', font=btnfont, foreground='blue',
               command=self.CreatePrettyTable).pack(side='left', padx=10)

        Button(frame2, text='PRINT', font=btnfont, foreground='blue',
               command=lambda: self.print('documents/CbcReport.docx')).pack(side='left')

        frame3 = Frame(self, background='powderblue', relief='ridge', bd=4)
        frame3.grid(row=0, column=2, rowspan=10, padx=10, pady=5,sticky="nw")

        self.text = table.Table(frame3,
            columns= ["Parameter", "Result", "Alarm", "Reference Range"],
            column_minwidths=[100, 150, 100,200])
        self.text.pack(expand=1, fill=BOTH, anchor=NW)

    def set_lab_tech(self, lab_tech):
        self.lab_tech = lab_tech

    def set_patient_detail(self, reg, name, age, sex):
        self.reg = reg
        self.name = name
        self.age = age
        self.sex = sex

    def set_footer_text(self, footer):
        self.footer_text = footer

    def set_phone(self, phone):
        self.phone = phone

    def preview(self, *args):
        try:
            document = MyDocument()
            # Attach logo if one exists
            document = self.parent_self.check_if_logo(document)
            name = document.add_paragraph("NAME: {}".format(self.name))
            document.add_text(name, "\tREG NO: {}".format(self.reg)).bold = True

            document.add_text(name, "\tAGE: {}".format(self.age))
            document.add_text(name, "\tSEX: {}".format(self.sex))

            tabledata = self.CreatePrettyTable()

            table = document.add_table("FULL HAEMOGRAM REPORT        Date: %s" % self.date,
                                       ["Parameter", "Result", "Alarm", "Ref Range"], tabledata)

            table.style = 'Medium Shading 1 Accent 5'
            if self.lab_tech:
                document.add_paragraph("Lab Technician: {}".format(self.lab_tech))
            footer = document.add_paragraph("\n\n\n\n")
            if self.footer_text:
                document.add_text(footer, "{} \n".format(self.footer_text))
            if self.phone:
                document.add_text(footer, "Contact Us: {} \n".format(self.phone))

        except Exception as e:
            raise

        try:
            document.save("documents/CbcReport.docx")
        except Exception as e:
            showerror("Error", str(e))
        else:
            self.print_ = True

    def CreatePrettyTable(self):
        FLAGS_DICT = OrderedDict()
        tabledata = []

        NR_DICT, UNITS_DICT = get_normal_ranges()

        for key, value in NR_DICT.items():
            entries_key = key.upper().replace(" ", "_").replace("%", "_PERC").replace("#", '')

            field_value = self.entries[entries_key].get()
            LOWERLIMIT, UPPERLIMIT = NR_DICT[key].split(',')

            unit = UNITS_DICT[key]
            ref_range = '-'.join(NR_DICT[key].split(',')) + str(unit)

            if field_value != "":
                try:
                    field_value = float(self.entries[entries_key].get())
                except ValueError:
                    showinfo("Error", "Invalid characters in field: '{}'\n"
                        "Must be an integer or float".format(key))
                    return

                if field_value < float(LOWERLIMIT):
                    FLAGS_DICT[key] = str(value)
                    FLAG = 'L'
                elif field_value > float(UPPERLIMIT):
                    FLAGS_DICT[key] = str(value)
                    FLAG = 'H'
                else:
                    FLAGS_DICT[key] = str(value)
                    FLAG = 'N.R'

                tabledata.append((key, field_value, FLAG, ref_range))

        self.text.clear()
        self.text.set_data(tabledata)
        return tabledata

    def print(self, doc_name):
        # Set patient details before creating a preview(Report)
        # This enables Lab Printing

        if self.parent_self:
            self.parent_self.get_cbc_details() #set from patients main

        self.preview()

        if self.print_:
            try:
                os.startfile(os.path.abspath(doc_name))
            except Exception as e:
                showinfo("OS ERRROR", str(e))

    def clearContents(self):
        for entry in self.entries.values():
            entry.delete(0, 'end')

        self.text.clear()

    # Over-ride methods get, insert, delete
    def get(self):
        """ Return CBC parameters with the values"""

        list_of_tuples_cbc = []
        for param, entry in self.entries.items():
            try:
                if entry.get() != "":
                    list_of_tuples_cbc.append((param, entry.get()))
            except:
                pass

        return list_of_tuples_cbc

    def delete(self, start, last):
        self.clearContents()

    def insert(self, index, tests):
        self.delete(0, 0)
        import ast
        if isinstance(tests, str):
            tests = ast.literal_eval(tests)
        elif isinstance(tests, list):
            tests= tests
        self.fill_CBC_Form(tests)
        self.CreatePrettyTable()

    def fill_CBC_Form(self, tests):
        for key, value in tests:
            self.entries[key].insert(0, value)


def main():
    root = Tk()
    cbc = CBC(root)
    cbc.set_patient_detail(10, "Abiira Nathan", 29, "Male")
    cbc.set_footer_text("Thank you.Come again")
    cbc.set_phone("0785434581")

    cbc.mainloop()


if __name__ == '__main__':
    main()
