# How do i generate FactFinder-esque column names??
cols = []
prefix = []
for col in [x['Table Title'] for x in table[2:]]:
    if col[-1] == ":":
        if len(prefix) == 0:
            prefix.append(col)
        else:
            i = ""
            while i not in ["r", "R", "a", "A"]:
                i = raw_input("Should \"" + col + "\" be (a)dded or (r)eplace the current prefix end (\""+ " ".join(prefix) +"\")?")
            if i in ["r", "R"]:
                print(prefix.pop())
            prefix.append(col)


    newcol = " ".join(prefix)
    if col != prefix[-1]:
        newcol += " " + col
    cols.append(newcol.strip())
    
for c in cols:
    print(c)