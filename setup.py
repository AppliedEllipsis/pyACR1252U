# setup.py
#coding=utf-8
import sys, os
from cx_Freeze import setup, Executable

ANACONDA_INSTALL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.__file__))))
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')


# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

options = {
    'build_exe': {
        'packages': [
          'os',
          ],
        'includes': [
          'PyQt5',
          'smartcard',
          'pyautogui',
          'time',
          'pprint',
          're',
          'ctypes',
          'subprocess',
          ],
        'include_files':[
            'launchNFC.cmd',
            'ui',
            os.path.join(ANACONDA_INSTALL_DIR, 'pkgs', 'qt-5.6.2-vc14_3', 'Library', 'plugins', 'platforms'), # change this for yoru QT version
            # ex: %HOMEPATH%\Anaconda2\pkgs\qt-5.6.2-vc14_3\Library\plugins\platforms
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
            'ui'
         ],
        
    }
}

target = Executable(
    script = 'NFC.pyw',
    base = base,
    icon = 'ui/nfc.ico'
    )


setup(  name = "NFC",
        version = "0.2",
        author="Applied Ellipsis",
        description = "NFC Tool for ACR1252U",
        options=options,
        executables=[target]
      )



# from distutils.core import setup
# import py2exe

# setup(windows=['NFC.pyw'],
#           options = {
#            "py2exe":{
#               "dll_excludes":["MSVCP90.dll"], 
#               "includes":["sip"]
#               }
#            })


\