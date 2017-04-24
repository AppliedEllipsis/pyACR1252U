
**How to setup your Environment**

----------

 - Install 32bit Anaconda3
 - Setup an environment for Python 3.5 Run console from your
   environment section.
    - hit play button open terminal
 - change directory to the dependencies folder, example cmd: **"cd /D
   Z:\projects\NFC\py\dependencies"**
 - conda install pip
 - conda install PyQT
 - pip install pyautogui
 
 - pip install -U nuitka

**For python 3.5**
 - pip install pyscard-1.9.5-cp35-cp35m-win32.whl

**For any other version, or 64bit**
 - Get the version of pyscard for your environment or compile it.  I get
   the pyscard binaries/artifacts from
   https://ci.appveyor.com/project/LudovicRousseau/pyscard
 - click the release for the right python version and architecture, then
   click artifacts tab, download the whl file and install with pip


**For Creating EXE reuirements**
 - pip install cx_freeze

**For Creating EXE**
 - delete the *build* folder
 - update **# change this for yoru QT version** section in setup.py to your QT version folder.
 - change directory to the project folder, example cmd: **"cd /D
   Z:\projects\NFC\py\"**
 - python setup.py build
    - your exe package will be in the *build* folder
- python setup.py bdist_msi
    - your msi install package will be in the *dist* folder
 
