# setup.py
#coding=utf-8
# remove port_v3 from pyqt4
from distutils.core import setup
import py2exe

setup(windows=['NFC.pyw'],
          options = {
           "py2exe":{"dll_excludes":["MSVCP90.dll"], "includes":["sip"]}})

