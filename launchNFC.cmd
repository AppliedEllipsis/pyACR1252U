@echo off
rem schtasks /Create /SC ONSTART /TN NFC2 /TR "Z:\projects\NFC\py\build\pyACR1252U_2017-04-24a\launchNFC.cmd" /IT /RL HIGHEST
cd /d %~dp0
start NFC.exe