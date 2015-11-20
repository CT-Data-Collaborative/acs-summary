from csv import reader, DictReader, writer, DictWriter
from os import path

# some file name constants
filenames = {
    "lookup" : "Sequence_Number_and_Table_Number_Lookup.csv",
    "geography" : "g20135ct.csv"
}

# Get path to raw files
rawDir = path.join(path.dirname(path.abspath(__file__)), "..", "raw")
rawDir = path.normpath(rawDir)

# build geography data
state = [] # 050 - will only be one row, and will be append to others
towns = [] # 060
counties = []  # 050
with open(path.join(rawDir, filenames["geography"])) as geoFile:
    geoReader = reader(geoFile)
    for geo in geoReader:
        if geo[2] == "050":
            print(geo)

# tables = []
# with open(path.join(rawDir, filenames["lookup"])) as lookupFile:
#     lookupReader = DictReader(lookupFile)
#     for row in lookupReader:
#         if row["Start Position"].strip() != "":
#             tables.append(row)

# for t in tables[1:10]:
#     print(t)