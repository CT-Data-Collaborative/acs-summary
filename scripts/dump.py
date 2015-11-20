from csv import reader, DictReader, writer, DictWriter
from os import path
from sys import argv, exit

# Get input from argv
try:
    searchTable = argv[1]
except IndexError:
    print("Please Supply a table number as a command line argument!")
    exit()

try:
    assert searchTable != ""
except AssertionError:
    print( "Please Supply a valid table number!")
    exit()

# print(searchTable)

# some file name constants
filenames = {
    "lookup" : "Sequence_Number_and_Table_Number_Lookup.csv",
    "geography" : "g20135ct.csv",
    "cols" : "tableVars.csv"
}

# Get path to raw files
rawDir = path.join(path.dirname(path.abspath(__file__)), "..", "raw")
rawDir = path.normpath(rawDir)

# Get path to output files
outputDir = path.join(path.dirname(path.abspath(__file__)), "..", "output")
outputDir = path.normpath(outputDir)

### build geography data
# Each entry in the geography arrays will be a Dict with the following entries:
#
# Recno => used to match data to entries in the actual data files later
# Geography => text name
# Id2 => FIPS - parsed out of combo census level/FIPS entry because it's easier than pasting multiple things with checks for blanks and sprintf calls
# Id => combo Census level/FIPS (ie 0400000US09)

counties = []  # 050 - plus one entry for state (040)
towns = [] # 060 - plus one entry for state (040)
with open(path.join(rawDir, filenames["geography"])) as geoFile:
    geoReader = reader(geoFile)
    for geo in geoReader: # there's definitely a more Zen/Pythonic way of handling this loop and ifs and reused code
        if geo[2] == "040" and geo[3] == "00":
            # reshape row into geo object
            geo = {
                "Recno" : geo[4],
                "Geography" : geo[49],
                "Id2" : geo[48].split("US")[1],
                "Id" : geo[48]
            }
            counties.append(geo)
            towns.append(geo)
        elif geo[2] == "050" and geo[3] == "00":
            # reshape row into geo object
            geo = {
                "Recno" : geo[4],
                "Geography" : geo[49],
                "Id2" : geo[48].split("US")[1],
                "Id" : geo[48]
            }
            counties.append(geo)
        elif geo[2] == "060" and geo[3] == "00" and geo[11] != "00000":
            # reshape row into geo object
            geo = {
                "Recno" : geo[4],
                "Geography" : geo[49],
                "Id2" : geo[48].split("US")[1],
                "Id" : geo[48]
            }
            towns.append(geo)

## Should be 9 and 170, respectively
# print("counties: " + str(len(counties)))
# print("* counties *")
# for r in counties[1:3]:
#     print(r)
# print("**")
# print("towns: " + str(len(towns)))
# print("* towns *")
# for r in towns[1:3]:
#     print(r)
# print("**")

tableShell = []
with open(path.join(rawDir, filenames["lookup"])) as lookupFile:
    lookupReader = DictReader(lookupFile)
    tableShell = [{k:v.strip() for k, v in row.iteritems()} for row in lookupReader if row["Table ID"].strip() == searchTable]


# print("* Shell *")
# for t in tableShell:
#     print(t)
# print("**")

# at this point, if we don't have a table shell we don't have a table. and should exit the program with an error
# that's a 'later' problem

columns = ["Id2",  "Id", "Geography"]
header = ["GEO.id2", "GEO.id", "GEO.display-label"]
vNum = 1
# get pretty columns
with open(path.join(rawDir, filenames["cols"])) as colFile:
    colReader = DictReader(colFile)
    # columns = [{k:v.strip() for k, v in row.iteritems()} for row in colReader if row["Table ID"].strip() == searchTable]
    for row in colReader:
        if row["Table ID"].strip() == searchTable:
            # pretty columns
            columns.append("Estimate; " + row["Variable Name"])
            columns.append("Margins of Error; " + row["Variable Name"])

            # Header columns
            header.append("HD01_VD"+"{0:02d}".format(vNum))
            header.append("HD02_VD"+"{0:02d}".format(vNum))
            

            vNum += 1

# columns = {r["Variable Name"] : r for r in columns}
# print("* Columns *")
# print(columns)
# print("**")

# Start to build the actual data
#pretty format table sequence
seq = tableShell[0]["Sequence Number"].zfill(4)

#estimate file
eFile = "e20135ct" + seq +"000.txt"
with open(path.join(rawDir, eFile)) as eFile:
    eReader = reader(eFile)
    eData = [row for row in eReader]

# print("* Estimates *")
# # for r in eData[1:10]:
#     print(r)
# print("**")

#moe file
mFile = "m20135ct" + seq +"000.txt"
with open(path.join(rawDir, mFile)) as mFile:
    mReader = reader(mFile)
    mData = [row for row in mReader]

# print("* MOEs *")
# for r in mData[1:10]:
#     print(r)
# print("**")

startPos = int(tableShell[0]["Start Position"]) - 1
# print("* Start Position *")
# print(startPos)
# print("**")
endPos = (len(tableShell) - 2) + startPos
# print("* End Position *")
# print(endPos)
# print("**")

positions = range(startPos, endPos)
# print("* Cell Positions *")
# print(positions)
# print("**")

townData = []
for town in towns:
    row = [
        town["Id2"],
        town["Id"],
        town["Geography"]
    ]
    rowEst = filter(lambda r: r[5] == town["Recno"], eData)[0]
    rowMoe = filter(lambda r: r[5] == town["Recno"], mData)[0]

    # now iterate and alternate estimates and moes, based on cell positions
    for p in positions:
        row.append(rowEst[p])
        row.append(rowMoe[p] if int(rowMoe[p]) != -1 else ".") # MOE coded as -1 are actually suppressions/nonexistant, so recode accordingly

    townData.append(row)

countyData = []
for county in counties:
    row = [
        county["Id2"],
        county["Id"],
        county["Geography"]
    ]
    rowEst = filter(lambda r: r[5] == county["Recno"], eData)[0]
    rowMoe = filter(lambda r: r[5] == county["Recno"], mData)[0]

    # now iterate and alternate estimates and moes, based on cell positions
    for p in positions:
        row.append(rowEst[p])
        row.append(rowMoe[p])

    countyData.append(row)

# write files
outputFileName = "ACS_13_5YR_"+ searchTable +"_with_ann.csv"
with open(path.join(outputDir, "Town", outputFileName), "w") as outputFile:
    townWriter = writer(outputFile)
    townWriter.writerow(header)
    townWriter.writerow(columns)
    for row in townData:
        townWriter.writerow(row)

with open(path.join(outputDir, "County", outputFileName), "w") as outputFile:
    countyWriter = writer(outputFile)
    countyWriter.writerow(header)
    countyWriter.writerow(columns)
    for row in countyData:
        countyWriter.writerow(row)

# # # Make sure to handle suppressions!!!!!
# suppression codes
# -1 = seems only attached to unweighted sample, meaning there is no "estimate" and therefor no MOE