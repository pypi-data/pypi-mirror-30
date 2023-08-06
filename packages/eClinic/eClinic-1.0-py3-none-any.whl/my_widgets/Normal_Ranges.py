from collections import OrderedDict

# Initialise dictionaries for reference ranges for CBC
CBC_Nranges = OrderedDict()
CBC_REF_RANGE = OrderedDict()

# Initialise dictionaries for reference ranges for General Lab tests
GENERAL_LAB_RANGES = OrderedDict()
GENERAL_REF_RANGES = OrderedDict()

def get_normal_ranges():
    # CBC Normal Ranges
    filename = 'config/CBC_Normal_Ranges.txt'
    with open(filename, 'r') as f:
        cbc_parameters = f.readlines()

    for item in cbc_parameters:
        test = item.strip("\n") # Read each test on a new line
        key, value, ref_range = test.split(":")
        CBC_Nranges[key] = value
        CBC_REF_RANGE[key] = ref_range

    return CBC_Nranges, CBC_REF_RANGE


def get_lab_normal_ranges():
    # General lab Normal Ranges,
    # To be implemented soon
    glab_filename = "config/General_Lab_Normal_Ranges.txt"
    with open(glab_filename, 'r') as file:
        generalLab_parameters = file.readlines()

    for item in generalLab_parameters:
        test = item.strip("\n") # Read each test on a new line
        key, value, ref_range = test.split(":")
        GENERAL_LAB_RANGES[key] = value
        GENERAL_REF_RANGES[key] = ref_range

    return GENERAL_LAB_RANGES, GENERAL_REF_RANGES
