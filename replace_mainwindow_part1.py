import re

with open("src/ui/mainwindow.py", "r") as f:
    content = f.read()

# Let's write a python script to patch mainwindow.py since it's quite large.
