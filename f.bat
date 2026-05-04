@echo off
set "SEVENZIP=C:\Program Files\7-Zip\7z.exe"
set "CELA=%USERPROFILE%\desktop\Partycja_Potepionych"

echo 🐻 Misiu Zbysiu buduje osobne cele dla każdego szczurka...

for %%i in ("%temppatch%\*.zip") do (
    echo 📥 Wypakowuję: %%~ni...
    :: -o"%CELA%\%%~ni" tworzy folder o nazwie takiej samej jak plik ZIP
    "%SEVENZIP%" x "%%i" -o"%CELA%\%%~ni" -p"infected" -y >nul
)

echo ✅ Wszystkie szczurki siedzą w osobnych celach!
pause
