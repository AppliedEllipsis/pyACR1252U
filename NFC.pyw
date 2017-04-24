#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function  

# Designed fro GoToTags NFC ACR1252U
# Using NTAG213/NTAG216
# encodes 4 character code for NXP MIFARE Ultralight tags
# uses data track, not NDEF
# uses a  tracks (5 and 6) in a single track 5 write
# NFC Forum Type 2

# see "how to setup your environment.md"


import sys, ctypes, datetime, time, re, subprocess

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox

from smartcard.scard import *
import smartcard.util
# from smartcard.System import readers
import pyautogui

from pprint import pprint

# fixes icon from being pythonw's in tray
import ctypes
myappid = u'com.professionalsounding.nfc-tool' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


qtCreatorFile = "ui/nfc.ui"  # Edit the UI with QTDesigner (\Anaconda3\Library\bin\designer.exe)

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
       QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
       menu = QtWidgets.QMenu(parent)
       showAction = menu.addAction("Show")
       menu.addSeparator()
       exitAction = menu.addAction("Exit")
       self.setContextMenu(menu)

       self.window = MyApp(self)
       self.window.start_nfc_thread()
       

       showAction.triggered.connect(self.show_window)
       exitAction.triggered.connect(self.exit)
       #QtCore.QObject.connect(showAction,QtCore.SIGNAL('triggered()'), self.showit)
       #QtCore.QObject.connect(exitAction,QtCore.SIGNAL('triggered()'), self.exit)
       # add double click and more events
       # QtCore.QObject.connect(self,QtCore.SIGNAL('activated(QSystemTrayIcon::ActivationReason)'), self.showit)
       # self.connect(self.icon, SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self.iconClicked)
       self.activated.connect(self.handle_activated)

    def show_window(self):
      print('tray show_window()')
      self.window.showNormal()

    def handle_activated(self, reason):
      print('tray handle_activated()', reason)
      if reason == QtWidgets.QSystemTrayIcon.Trigger:
          # self.window.showNormal()
          ''
      elif reason == QtWidgets.QSystemTrayIcon.DoubleClick:
          self.show_window()
      elif reason == QtWidgets.QSystemTrayIcon.Context:
        ''
        # self.window.showNormal()
      
  
    def exit(self):
      reply = QMessageBox.question(
          self.window,
          'NFC Tool',"Are you sure to quit?",
          QMessageBox.Yes | QMessageBox.No,
          QMessageBox.No)

      if reply == QMessageBox.Yes:
          self.hide()
          QtCore.QCoreApplication.exit()
          #QCoreApplication.instance().quit()
          


      


class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
  threads = []

  def __init__(self, trayicon):
    self.trayicon = trayicon


    QtWidgets.QMainWindow.__init__(self)      
    Ui_MainWindow.__init__(self)
    self.setupUi(self)

    self.service_stop_CertPropSvc_if_running()
    self.txt_code.setEchoMode(QtWidgets.QLineEdit.Password) # set password mask on txt
    # self.txt_code.editingFinished.connect(self.setProgrammingMode)
    self.txt_code.returnPressed.connect(self.setProgrammingMode)
    self.btn_set.clicked.connect(self.setProgrammingMode)
    # self.btn_dl.clicked.connect(self.start_nfc_thread)


  def event(self, event):
      if (event.type() == QtCore.QEvent.WindowStateChange and self.isMinimized()):
          # The window is already minimized at this point.  AFAIK,
          # there is no hook stop a minimize event. Instead,
          # removing the Qt.Tool flag should remove the window
          # from the taskbar.
          self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.Tool)
          # self.tray_icon.show()
          return True
      else:
          return super(MyApp, self).event(event)


  def closeEvent(self, event):
    reply = QMessageBox.question(
        self,
        'NFC Tool',"Are you sure to quit?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No)

    if reply == QMessageBox.Yes:
        self.trayicon.hide()
        event.accept()
    else:
        # self.tray_icon.show()
        self.hide()
        event.ignore()


  def setProgrammingMode(self):
    if self.btn_set.text() == 'Cancel Programming':
      self.threads[0].programming_code = ''
      self.threads[0].programming = False
      self.log("Programming Cancelled..." )
      self.txt_code.setEnabled(True)
      self.btn_set.setText('Program Card')
    else:
      # card_code = int(self.txt_code.text()) # force int?
      card_code = (self.txt_code.text())
      if len(card_code) != 4:
        QMessageBox.warning(self, "NFC Tool", "Error: The code must be 4 characters long.")
        return

      if len(self.threads) > 0:
        self.txt_code.setEnabled(False)
        self.btn_set.setText('Cancel Programming')
        self.threads[0].programming_code = card_code
        self.threads[0].programming = True
        self.log(  "Place card on reader to program... " ) #+ str(card_code) )


  def start_nfc_thread(self):
      nfc_thread = NFC_Thread('')
      nfc_thread.data_update.connect(self.log)
      nfc_thread.data_programming_done.connect(self.on_programming_done)
      nfc_thread.data_critical.connect(self.on_critical)
      self.threads.append(nfc_thread)
      nfc_thread.start()


  def log(self, data):
    ts = '{:%Y-%m-%d %I:%M:%S %p}'.format(datetime.datetime.now())
    print(ts, data)
    # self.listWidget.addItem( ts + ": " + data )
    self.listWidget.insertItem( 0, ts + ":     " + str(data) )
    max_log = 50
    if self.listWidget.count() > max_log:
      while self.listWidget.count() > max_log:
        self.listWidget.takeItem(max_log)

  def on_programming_done(self, data):
    self.log("Programming Done: " + str(data) )
    self.btn_set.setText('Program Card')
    self.txt_code.setText('')
    self.txt_code.setEnabled(True)
    QMessageBox.information(self, "NFC Tool", "The card has been programmed.")


  def on_critical(self, data):
    self.log("Critial Error: " + str(data) )
    QMessageBox.critical(self, "NFC Tool", data)
    #QCoreApplication.instance().quit()
    #QtCore.QCoreApplication.exit()


  def is_admin(self):
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

  def service_check_state(self, service_name):
    try:
      DETACHED_PROCESS = 0x00000008
      res = subprocess.check_output(['sc', 'query', service_name], creationflags=DETACHED_PROCESS, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
      # raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
      return False
    res = res.decode('unicode_escape')
    matchObj = re.search( r'STATE.+\:.*(STOPPED|RUNNING)', res, re.M|re.I)
    if matchObj:
      if matchObj.group(1).upper() == 'RUNNING':
        return True
      else:
        return False
    return False


  def service_stop(self, service_name):
    # runs as admin
    ctypes.windll.shell32.ShellExecuteW(None, "runas", "sc", "stop " + service_name, None, 1)


  def service_stop_CertPropSvc_if_running(self):
    service_name = 'CertPropSvc'

    if self.service_check_state(service_name):
      if not self.is_admin():
        msg = """
The Certificate Propagation service is running...

This creates an device inserted notification for 
"unknown smart card" in windows each time an NFC is touched.

This application is going to attempt to disable it...

You may need to click "yes" and "login" to an 
"user access control" request or rerun this as admin.

You can choose "no" or "not login" and 
this program will still function, 
but it will be very annoying if you have speakers on.
"""
        print(msg)
        QMessageBox.warning(self, "NFC Tool", msg)
      else:
        print('Launched as Admin')
      self.service_stop(service_name)
      running = True
      for i in range(1,10):
        time.sleep(0.5)
        running = self.service_check_state(service_name)
        if not running:
          break
      if running:
        msg = "Certificate Propagation service failed to stop... \nDid you say no to the prompt?"
        print(msg)
        QMessageBox.warning(self, "NFC Tool", msg)
      else:
        print('Successfully stopped the Certificate Propagation service.')



class NFC_Thread(QtCore.QThread):

  data_update = QtCore.pyqtSignal(object)
  data_programming_done = QtCore.pyqtSignal(object)
  data_critical = QtCore.pyqtSignal(object)

  programming = False
  programming_code = ''

  def __init__(self, url):
      QtCore.QThread.__init__(self)
      self.card_present_ = {}


  def nfc_process_state(self, state):
    reader, eventstate, atr = state
    readerid = reader + " " + smartcard.util.toHexString(atr, smartcard.util.HEX)
    # print(readerid)
    if reader not in self.card_present_:
      self.card_present_[reader] = 0

    # print(readerid, self.card_present_[readerid])
    # if eventstate & SCARD_STATE_ATRMATCH:
    #     print('\tCard found')
    # if eventstate & SCARD_STATE_UNAWARE:
    #     print('\tState unware')
    # if eventstate & SCARD_STATE_IGNORE:
    #     print('\tIgnore reader')
    # if eventstate & SCARD_STATE_UNAVAILABLE:
    #     print('\tReader unavailable')
    if eventstate & SCARD_STATE_EMPTY:
      # print('\tReader empty')
      if self.card_present_[reader] != 0:
        self.data_update.emit( "Card removed from reader: " + str(reader) )
        self.card_present_[reader] = 0
    if eventstate & SCARD_STATE_PRESENT and (self.card_present_[reader] == 0):
      self.card_present_[reader] = 1
      # print('\tCard present in reader')
      self.data_update.emit( "Card present in reader: " + str(reader) )
      r=smartcard.System.readers()
      raI = -1
      for ra in r:
        raI += 1
        if str(ra) == str(reader):
          # print(ra)
          connection = r[raI].createConnection()
          connection.connect()
          if self.programming:
            self.programming = False
            self.data_update.emit("nfc_process_state Programming Mode Found for code: " + str(self.programming_code) )
            # update binary block
            data, sw1, sw2 = connection.transmit(  [ 0xFF, 0xD6, 0x00, 0x5, 0x10] + toDec("!~" + str(self.programming_code) + "~!") )
            self.data_programming_done.emit("Done programming... ") # + str(self.programming_code) )
            # print("%x %x" % (sw1, sw2))
            # print(data)
            # characters = [chr(n) for n in data]
            # print(characters) 
          else:
            # read binary block
            data, sw1, sw2 = connection.transmit( [ 0xFF, 0xB0, 0x00, 0x5, 0x10 ] )
            # print("%x %x" % (sw1, sw2))
            # print(data)
            characters = [chr(n) for n in data]
            msg = ''.join(characters[0:8])
            print(msg)
            matchObj = re.search( r'!~(.*)~!', msg, re.M|re.I)
            if matchObj:
              # print(matchObj.group(1))
              self.data_update.emit( "\tFound Valid Code" ) #           76543210                   repeat
              data, sw1, sw2 = connection.transmit( [0xff, 0x0, 0x40, 0b10001010, 0x04, 0x00, 0x01, 0x01, 0x02] )
              # self.data_update.emit( matchObj.group(1) )
              pyautogui.typewrite(matchObj.group(1) + "\n")
              return
    # if eventstate & SCARD_STATE_EXCLUSIVE:
    #     print('\tCard allocated for exclusive use by another application')
    # if eventstate & SCARD_STATE_INUSE:
    #     print('\tCard in used by another application but can be shared')
    # if eventstate & SCARD_STATE_MUTE:
    #     print('\tCard is mute')
    # if eventstate & SCARD_STATE_CHANGED:
    #    print('\tState changed')
    # if eventstate & SCARD_STATE_UNKNOWN:
    #     print('\tState unknowned')


  def send_control_code(self, hcard, command):
    self.data_update.emit( "send_control_code" )
    print(command)
    hresult, response = SCardControl(hcard, SCARD_CTL_CODE(3500), command)
    if hresult != SCARD_S_SUCCESS:
      raise(error, 'SCardControl(): ' + SCardGetErrorMessage(hresult))
    print(''.join('{:02X} '.format(x) for x in response))
    # print(''.join('{0:b} '.format(x) for x in response))
    return response

  def beep(self, hcard, duration):
    self.data_update.emit( "beep")
    self.send_control_code(hcard, [0xE0, 0x0, 0x0, 0x28, 0x01, duration])


  def get_led(self, hcard):
    pprint('get_led()')
    resp = self.send_control_code(hcard, [0xE0, 0x0, 0x0, 0x29, 0x00])
    if resp[-1] == 0b11:
      return 'orange'
    elif resp[-1] == 0b1:
      return 'red'
    elif resp[-1] == 0b01:
      return 'green'
    else:
      return 'off'


  def set_led(self, hcard, color):
    if color == 'orange':
      color=0b11
    elif color == 'red':
      color=0b1
    elif color == 'green':
      color=0b01
    else:
      color=0b0
    self.send_control_code(hcard, [0xE0, 0x0, 0x0, 0x29, 0x01, color])


  def run(self):
    try:




      hresult, hcontext_cmd = SCardEstablishContext(SCARD_SCOPE_USER)
      if hresult != SCARD_S_SUCCESS:
        self.data_critical.emit( 'Failed to establish context: ' + SCardGetErrorMessage(hresult))
        raise error( 'Failed to establish context: ' + SCardGetErrorMessage(hresult))
      # print('Context established!')
      self.data_update.emit('Context established!')

      try:
        hresult, readers_cmd = SCardListReaders(hcontext_cmd, [])
        if hresult != SCARD_S_SUCCESS:
            self.data_critical.emit('Failed to list readers: ' + SCardGetErrorMessage(hresult) )
            raise error( 'Failed to list readers: ' + SCardGetErrorMessage(hresult) )
        
        # print('PCSC Readers:', readers_cmd)
        # msg = 'PCSC Readers:'
        # for i in range(len(readers_cmd)):
        #   self.data_update.emit( 'Reader: ' + str(readers_cmd[i]) )
        

        self.reader_hcard_ = {}
        for i in range(len(readers_cmd)):
          hresult, hcard, dwActiveProtocol = SCardConnect(hcontext_cmd, readers_cmd[i], SCARD_SHARE_DIRECT, 0)
          if hresult != SCARD_S_SUCCESS:
            raise(error, 'SCardConnect(): ' + SCardGetErrorMessage(hresult))
          # pprint(self.reader_hcard_)
          self.send_control_code(hcard, [0xE0, 0x0, 0x0, 0x21, 0x01, 0b11100100]) # disable led unless contact, then make it orange, disable beeps unless we beep it
          self.beep(hcard, 0x03)
          time.sleep(0.1)

      except (KeyboardInterrupt, SystemExit):
          raise
      except error as e:
        print(e)
      finally:
        ''
        hresult = SCardReleaseContext(hcontext_cmd)
        if hresult != SCARD_S_SUCCESS:
            self.data_critical.emit( 'Failed to release context: ' + SCardGetErrorMessage(hresult))
            raise error( 'Failed to release context: ' + SCardGetErrorMessage(hresult))
        print('Released context.')
        self.data_update.emit('Released context.')










      hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
      if hresult != SCARD_S_SUCCESS:
        self.data_critical.emit( 'Failed to establish context: ' + SCardGetErrorMessage(hresult))
        raise error( 'Failed to establish context: ' + SCardGetErrorMessage(hresult))
      # print('Context established!')
      self.data_update.emit('Context established!')

      try:
        hresult, readers = SCardListReaders(hcontext, [])
        if hresult != SCARD_S_SUCCESS:
            self.data_critical.emit('Failed to list readers: ' + SCardGetErrorMessage(hresult) )
            raise error( 'Failed to list readers: ' + SCardGetErrorMessage(hresult) )
        
        print('PCSC Readers:', readers)
        msg = 'PCSC Readers:'
        for i in range(len(readers)):
          self.data_update.emit( 'Reader: ' + str(readers[i]) )


        reader_states = []
        for i in range(len(readers)):
            reader_states += [(readers[i], SCARD_STATE_UNAWARE)]

        # get initial state
        hresult, newstates = SCardGetStatusChange(hcontext, 0, reader_states)

        while True:
            # try:
            #     if not isRunningFunc() :
            #         self.data_update.emit( "Stopped!" )
            #         return
            # except : pass 
            # print('----- Please insert or remove a card ------------')
            try:
            # if True:
                hresult, newstates = SCardGetStatusChange(
                                        hcontext,
                                        1000, # INFINITE,
                                        newstates)


                # print('----- New reader and card states are: -----------')
                # print(self.card_present_)
                for i in newstates:
                    self.nfc_process_state(i)
            except : pass 

        # hresult, newstates = SCardGetStatusChange(hcontext, 0, reader_states)
        # for i in newstates:
        #     self.nfc_process_state(i)
      except (KeyboardInterrupt, SystemExit):
          raise
      except error as e:
        print(e)
      finally:
          hresult = SCardReleaseContext(hcontext)
          if hresult != SCARD_S_SUCCESS:
              self.data_critical.emit( 'Failed to release context: ' + SCardGetErrorMessage(hresult))
              raise error( 'Failed to release context: ' + SCardGetErrorMessage(hresult))
          print('Released context.')
          self.data_update.emit('Released context.')


      import sys
      if 'win32' == sys.platform:
          print('press Enter to continue')
          sys.stdin.read(1)
    except (KeyboardInterrupt, SystemExit):
        raise
    except error as e:
        print(e)


#convert string to hex
def toDec(s):
    lst = []
    for ch in s:
        hv = (ord(ch)) #.replace('0x', '')
        # if len(hv) == 1:
        #     hv = '0'+hv
        lst.append(hv)
    
    return lst #reduce(lambda x,y:x+y, lst)

#convert string to hex
def toHex(s):
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)
    
    return lst #reduce(lambda x,y:x+y, lst)

#convert hex repr to string
def toStr(s):
    return s and chr(atoi(s[:2], base=16)) + toStr(s[2:]) or ''



def is_process_name_running_more_than_once(process_name):
  try:
    DETACHED_PROCESS = 0x00000008
    res = subprocess.check_output(['wmic', 'process', 'get', 'caption'], creationflags=DETACHED_PROCESS, stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as e:
    # raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    return False
  res = res.decode('unicode_escape')
  # print('already check:', res)
  if res.lower().count(process_name.lower()) > 1:
    return True
  else:
    return False


def main():



  app = QtWidgets.QApplication(sys.argv)

  app_icon = QtGui.QIcon()
  app_icon.addFile('ui/nfc-16.png', QtCore.QSize(16,16))
  app_icon.addFile('ui/nfc-24.png', QtCore.QSize(24,24))
  app_icon.addFile('ui/nfc-32.png', QtCore.QSize(32,32))
  app_icon.addFile('ui/nfc-48.png', QtCore.QSize(48,48))
  app_icon.addFile('ui/nfc-256.png', QtCore.QSize(256,256))
  app.setWindowIcon(app_icon)

  w = QtWidgets.QWidget()

  trayIcon = SystemTrayIcon(QtGui.QIcon("ui/nfc-48.png"), w)
  trayIcon.show()



  sys.exit(app.exec_())

if __name__ == '__main__':
  if is_process_name_running_more_than_once('nfc.exe'):  # this will only work against exe copies
    msg = "Error: There is another copy of this application running.."
    print(msg)
    ctypes.windll.user32.MessageBoxW(None, msg, "NFC", 0x10 | 0 | 0x1000) # flags MB_ICONERROR | MB_OK | MB_SYSTEMMODAL
  else:
    main()


