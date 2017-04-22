# pyACR1252U
Windows Tool to Read/Write/Manipulate GoToTags NFC ACR1252U NTAG213/NTAG216 NXP MIFARE Ultralight Tags

**[Check Release Section](https://github.com/AppliedEllipsis/pyACR1252U/releases)** for Exe/Binary release you can use without an Python Environment and includes dependencies.

**[How to setup your environment](how%20to%20setup%20your%20environment.md)** 


**It currently performs:**
* Reads and Writes 4 character pins to NFC.
  * **To write**, open the window, type in a code and press enter or program.
    * Hold the card against the reader/writer until it says it's been programmed.
  * **To read**, just have the application loaded in the tray and have a keyboard input box in focus.
    * Hold the card against the reader/writer until it writes out the code followed by an enter.
    * This is good for pin input in POS devices when you don't want others to see you type in the code.
* QT Gui App that sits in the Windows Tray Icon
  * Click the icon to show the window, right click (maybe 2x), to show exit window.
  * minimizes to the tray icon, the X shows a prompt to really quit, clicking no will minimize to tray.
  * The tray icon may be hidden in the more tray icons section in Windows.
* Only run 1 instance of the application.
* When it reads, it types the characters into whatever window has focus, followed by an enter.
* It was orignally written for Python 2 using PyQT4, but it's now Python 2/3 compatiable using PyQT5. I plan on only coding it against Python 3 and PyQT5 from now on, so backwards compatibality may break.  Exe's were originally packaged using py2exe. However, it is not compatiable with Python 3.5, so I moved to cx_freeze.



#### Links to depends not installed with pip or conda
[libusb's download, source, and licenses](http://libusb.info/)

[pyscard's source, and licenses](https://pyscard.sourceforge.io/)

[pyscard's binaries](https://ci.appveyor.com/project/LudovicRousseau/pyscard), click a release, and then artifacts. I recommend using the whl file with pip.

