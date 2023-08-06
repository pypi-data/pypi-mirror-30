# RELEASE NOTE

## Version 1.0.0b1 - First Release

- `Open Excel` Opens the Excel file from the path provided in the file name parameter. If the boolean useTempDir is set to true, depending on the operating system of the computer running the test the file will be opened in the Temp directory if the operating system is Windows or tmp directory if it is not.
- `Read Cell` Returns the value stored in the cell indicated by row and column.
- `Read Cell Data By Name` Uses the cell name to return the data from that cell.
- `Read Cell Data By Coordinates` Uses the column and row to return the data from that cell. This keyword was formally called Read Cell.
- `Get Sheet Names` Returns the names of all the worksheets in the current workbook.
- `Get Number Of Sheets` Returns the number of worksheets in the current workbook.
- `Get Column Count` Returns the specific number of columns of the sheet name specified.
- `Get Row Count` Returns the specific number of rows of the sheet name specified.
- `Get Column Values` Returns the specific column values of the sheet name specified.
- `Get Row Values` Returns the specific row values of the sheet name specified.
- `Get Sheet Values` Returns the values from the sheet name specified.
- `Get Workbook Values` Returns the values from each sheet of the current workbook.
- `Check Cell Type` Checks the type of value that is within the cell of the sheet name selected.

- `Create Excel` Creates a new Excel workbook.
- `Add New Sheet` Creates and appends new Excel worksheet using the new sheet name to the current workbook.
- `Put Number To Cell` Using the sheet name the value of the indicated cell is set to be the number given in the parameter.
- `Put String To Cell` Using the sheet name the value of the indicated cell is set to be the string given in the parameter.
- `Put Date To Cell` Using the sheet name the value of the indicated cell is set to be the date given in the parameter.
- `Modify Cell With` Using the sheet name a cell is modified with the given operation and value.
- `Add To Date` Using the sheet name the number of days are added to the date in the indicated cell.
- `Subtract Fom Date` Using the sheet name the number of days are subtracted from the date in the indicated cell.
- `Save Excel` Saves the Excel file indicated by file name, the useTempDir can be set to true if the user needs the file saved in the temporary directory. If the boolean useTempDir is set to true, depending on the operating system of the computer running the test the file will be saved in the Temp directory if the operating system is Windows or tmp directory if it is not.
