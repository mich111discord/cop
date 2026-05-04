@echo off
title filelab setup
echo pobieranie WinRAR i 7Zip...
winget install RARLab.WinRAR
winget install 7zip.7zip
pobieranie processexplorer...
cd %temp% && mkdir filelab && cd filelab
curl -o "ProcessExplorer.zip" https://download.sysinternals.com/files/ProcessExplorer.zip >nul
set temppatch=%temp%\filelab
mkdir %USERPROFILE%\desktop\ProcessExplorer
tar -xf %temppatch%\ProcessExplorer.zip -C %USERPROFILE%\desktop\ProcessExplorer >nul
echo pobieranie RKILL...
cd %USERPROFILE%\desktop
curl -o Rkill.exe https://download.bleepingcomputer.com/dl/df71935c088d3f2cc581c1bfb9a5d50e8b24eeaee46fe73c7058f9f062a69605/69f8b225/windows/security/security-utilities/r/rkill/rkill.exe >nul
echo pobieranie kvrt i innych skanerow...
curl -o KVRT.exe https://devbuilds.s.kaspersky-labs.com/devbuilds/KVRT/latest/full/KVRT.exe >nul
curl -o NPE.exe https://buy-download.norton.com/downloads/premium_services/NPE/6.0/prod/NPE.exe >nul
curl -o HitmanPro_x64.exe https://download.sophos.com/endpoint/clients/HitmanPro_x64.exe >nul
echo gotowe...
pause
exit

