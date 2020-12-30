import os, shutil
import nbformat
from nbconvert import PythonExporter

def convertNotebook(notebookPath, modulePath):
    with open(notebookPath) as fh:
        nb = nbformat.reads(fh.read(), nbformat.NO_CONVERT)
    
    exporter = PythonExporter()
    source, meta = exporter.from_notebook_node(nb)
    
    lines = source.split('\n')
    while '# REMOVE ME' in lines: 
        i1 = lines.index('# REMOVE ME')
        i2 = lines.index('# -------------------')
        lines = [i for j, i in enumerate(lines) if j not in range(i1, i2 + 1)]    
    source = '\n'.join(lines)
    
    with open(modulePath, 'w+') as fh:
        fh.writelines(source)

hiddenimports = [
    'numpy',
    'os',
    'subprocess',
    'itertools',
    'ctypes',
    'win32gui',
    'win32com',
    'pyautogui',
    'keyboard',
    'json',
    'datetime',
    'psutil',
    'time',
    'PIL',
    "mss",
    "cv2",
    "shutil"
]

os.makedirs('compile', exist_ok=True)
with open('compile/controller imports.py', 'w') as fd:
    fd.write('hiddenimports = ' + str(hiddenimports))
shutil.copyfile('admin.py', 'compile/admin.py')
convertNotebook('Controller.ipynb', 'compile/Controller.py')
convertNotebook('Bot.ipynb', 'compile/Bot.py')

os.system('pyinstaller "compile/bot.py" --onefile --specpath="compile/" --distpath="compile/" --workpath="compile/" --additional-hooks-dir="compile/hook-data.py"')

shutil.copyfile('compile/bot.exe', 'bot.exe')
shutil.rmtree('compile')