from collections import OrderedDict
fields = ["Patient ID", "First Name","Last Name", "DOB", "Age", 'Sex', "Village",
          "Parish","Sub County", "County", "District", "Date Seen", "Occupation",
          "Tribe", "Marital Status", "Next of Kin", "Mobile", "Religion", "Time Seen"
      ]

religions = ['Protestant',"Catholic", "Moslem", "Orthodox", "Born Again",
            "Seventh Day Adventist"]

occupations = ["None","Peasant", "House Wife", "Business man", "Business woman", "Primary Teacher","Secondary Teacher", "Lecturer", "Engineer", "Electrician", "Doctor", "Nurse",
  "Midwife", "Lab Attendant"]

tribes = ["Munyankole", "Muganda", "Mukiga", "Mutooro", "Munyarwanda", "Muteeso", "Mugisu",
          "Lugbara", "Luo"]

sexes = ["Male", "Female"]
m_statuses = ["Single", "Married", "Cohabiting", "Widow","Widower", "Divorced"]

options = OrderedDict()
values = [sexes, occupations, tribes,  m_statuses, religions]
options['values'] = values

def get_options():
    return options

def get_fields():
    return fields

