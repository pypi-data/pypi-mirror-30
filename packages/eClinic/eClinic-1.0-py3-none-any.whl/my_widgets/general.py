from collections import OrderedDict
import tkinter.ttk as ttk
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import tkinter.font as tkFont
import ast

general_exam_dict = OrderedDict()

general_exam_items = ["Apperance","Jaundice", "Anaemia", "Cyanosis", "Clubbing", "Oedema", "Lympadenopathy", "Dehydration", "Peripheries", "Skin", "Back"]

appearance_list=["Good General Condition", "Fair general condition",
                "Very sick loooking", "Sick loooking", "Toxic appearance",
                "unkempt", "Diaphoretic", "Semi-conscious","Unconscious"]

jaundice_list = ["No Jaundice", "Tinge of Jaundice", "Moderate Jaundice","Deep Jaundice"]
anaemia_list = ["No pallor", "mild pallor","moderate pallor", "severe pallor"]
cyanosis_list= ["No cyanosis", "peripheral cyanosis", "central cyanosis", "acrocyanosis"]
clubbing_list = ["No digital clubbing", "grade 1 finger clubbing", "grade 2 finger clubbing","grade 3 finger clubbing","grade 4 finger clubbing","hypertrophic pulmonary osteoarthropathy"]

oedema_list =["No eodema", "grade 1 oedema", "grade 2 oedema", "grade 3 oedema", "anarsaca"]
lympadenopathy_list = ["No lympadenopathy", "lympadenopathy"]
dehydration_list =["No dehydration", "mild dehydration", "moderate dehydration", "severe dehydration"]

peripheries_list = ["Warm peripheries", "Cold peripheries", "Cold and clammy peripheries"]
skin_list = []
back_list = []

# Populate the OrderedDict by zipping categories with respective lists
all_lists = [appearance_list, jaundice_list, anaemia_list, cyanosis_list,
            clubbing_list,oedema_list, lympadenopathy_list, dehydration_list,
            peripheries_list, skin_list, back_list]

for category, category_listing in zip(general_exam_items, all_lists):
    general_exam_dict[category] = category_listing

class GEntry:
    def __init__(self, frame, parent=None):
        self.frame = frame
        self.parent = parent
        self.general_entries=OrderedDict()

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("TLabel",
                            background="SystemButtonFace",
                            font="Calibri 14")

        self.initUI()

    def initUI(self):
        for finding, options in general_exam_dict.items():
            frame = Frame(self.frame, padx=10,pady=1)
            frame.pack(fill=BOTH, expand =1)

            label = ttk.Label(frame, text= finding)
            label.pack(side=LEFT)

            if finding == "Skin" or finding=="Back":
                entry = ScrolledText(frame, width=30, height=5, font="Calibri 13", wrap=WORD)
            else:
                entry = ttk.Combobox(frame, values = options, width=45)
                entry.set(options[0])

            entry.pack(side=RIGHT, anchor='w')
            # set 1st item as default
            key = finding.upper().replace(" ", "_")
            self.general_entries[key] = entry

    def get(self):
        results = []
        for value in self.general_entries.values():
            try:
                results.append(value.get().strip())
            except:
                # Cater for the ScrolledText
                results.append(value.get("1.0", "end").strip())

        return results

    def delete(self, start=0, end=END):
        for entry in self.general_entries:
            try:
                self.general_entries[entry].delete(start, end)
            except:
                self.general_entries[entry].delete("1.0", end)

    def set(self, list_of_findings):
        # Convert '[]'>>[]
        if isinstance(list_of_findings, str):
            list_of_findings = ast.literal_eval(list_of_findings)

        for index, entry in enumerate(self.general_entries):
            try:
                self.general_entries[entry].set(list_of_findings[index])
            except AttributeError:
                # For ScrolledText widget
                self.general_entries[entry].insert("1.0", list_of_findings[index])

if __name__ == '__main__':
    root = Tk()
    gen = GEntry(root)
    gen.set([1,2,3,4,5,6,7,8,9,10,11])
    print(gen.get())
    root.mainloop()
