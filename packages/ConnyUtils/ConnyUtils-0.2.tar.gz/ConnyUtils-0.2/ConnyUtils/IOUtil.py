import os
import sys
import codecs
import pandas as pd
import numpy as np

# using pandas - get the dataframe out of the box
def fetchDataFrameFromSQL(sqlQueryString, connection):
    return pd.read_sql_query(sqlQueryString, connection)

# do manual fetch the array
def fetchResultsAs2DArray(pdCursor, amount=-1, logNRows=0, withDescription=True, withIndex=False):
    result = []
    if (withDescription):
        result.append([column[0] for column in pdCursor.description])
        if (withIndex):
            result[0].insert(0, "index")
    if (amount == -1):
        amount = sys.maxsize
    for ii in range(0, amount):
        row = pdCursor.fetchone()
        if not row:
            break
        if (withIndex):
            row = np.insert(row, 0, ii)
        result.append(list(row))

        if (ii < logNRows):
            print(list(row))
    return result

# opens a textfile with some encoding magic - does some lookup
# handy if file on disc has some encoding header
def openTextFile(filename, mode='r'):
    if os.path.isfile(filename):
        f = codecs.open(filename, 'rb')
        header = f.read(4)  # Read just the first four bytes.
        f.close()
        # Don't change this to a map, because it is ordered!!!
        encodings = [(codecs.BOM_UTF32, 'utf-32'),
                     (codecs.BOM_UTF16, 'utf-16'),
                     (codecs.BOM_UTF8, 'utf-8')]
        for h, e in encodings:
            if header.find(h) == 0:
                encoding = e
                break
        return codecs.open(filename, mode, encoding)
    else:
        print(filename, " not found")

# reads a .sql file containing a query, runs this query against a connection and returns the result as dataframe
def fetchDataFrameFromSqlFile(filename, connection):
    # read microsoft .sql file
    with openTextFile(filename=filename, mode='r') as myfile:
        sqlQuery = myfile.read()
        dataFrame = fetchDataFrameFromSQL(sqlQuery, connection)
    return dataFrame

# write a list to file. Will iterate over the list and write the content to disk.
def writeListToFile(theList, filename, encoding='utf-8'):
    print("sys.stdout.encoding:", sys.stdout.encoding)
    with open(filename, mode='w', encoding=encoding, errors='strict', buffering=1) as file:
        for item in theList:
            file.write("%s\n" % item)
        print("Wrote to file: ", os.path.abspath(file.name))
        file.close()

# reand an array from disk...
def readToArray(filename, encoding='utf-8'):
    with open(filename, mode='r', encoding=encoding, errors='strict', buffering=1) as f:
        lines = f.read().splitlines()
        f.close()
        return lines

# read and print a file
def readAndPrint(filename):
    with open(filename, mode='r', encoding="utf-8", errors='strict', buffering=1) as f:
        read_data = f.read()
        print(read_data)
        f.close()