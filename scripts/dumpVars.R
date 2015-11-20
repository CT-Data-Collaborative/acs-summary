library(acs)
library(data.table)

# designed to be run from acs-sumarry/scripts directory!
tables <- fread(
    file.path(getwd(), "..", "raw", "Sequence_Number_and_Table_Number_Lookup.csv")
)

tables <- unique(tables$`Table ID`)

# container
data = data.table()
for (table in tables) {
    vars = NA
    tryCatch(
        vars <- acs.lookup(table.name = table),
        error = function(e) {
            print(paste("Error! Table '", table, "' not listed in xml resource. Skipping . . .", sep = ""))
        }
    )
    if( is.logical(get0("vars", ifnotfound = F)) ) {
        next
    }
    else {
        vars = vars@results
        names(vars) <- c("Variable Code", "Table ID", "Table Name", "Variable Name")
        vars$`Variable Code` <- gsub("_", "", vars$`Variable Code`, fixed = T)

        data <- rbind(data, vars)
    }
    remove(vars, table)
}

# Write to File
write.table(
    data,
    file.path(getwd(), "..", "raw", "tableVars.csv"),
    sep = ",",
    row.names = F,
    na = "-9999"
)
