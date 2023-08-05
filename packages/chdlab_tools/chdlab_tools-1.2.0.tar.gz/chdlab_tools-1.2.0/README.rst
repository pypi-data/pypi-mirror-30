INSTALLATION
============

Linux
=====
Nothing to be done for WCCI servers (already in the path)
Other users - simply clone chdlab and add chdlab.py (full path) to your path or as an alias

Windows - experimental
======================
1. Install latest python 2.x from https://www.python.org/downloads/
2. Install Microsoft Visual C++ Compiler for Python7.7 - https://www.microsoft.com/en-us/download/details.aspx?id=44266
3. Open cmd, navigate to c:\python27\scripts
4. pip --proxy http://proxy-iil.intel.com:911 install restkit
5. pip --proxy http://proxy-iil.intel.com:911 install paramiko
6. pip --proxy http://proxy-iil.intel.com:911 install pexpect

Run chdlab.py: cd C:\python27\; python.exe <path to chdlab.py>

ADD A NEW SETUP/BOARD
=====================
Add a new line in setups.conf
