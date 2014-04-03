#!/usr/bin/python

import os, sys

# Open a file
path = ""
dirs = os.listdir( path )

# This would print all the files and directories
for file in dirs:
    if file == "structPckId.py" :
        print file + " OK!"
    else:
       print file
