@echo off
chcp 65001 > nul
title GitHub'ga yuklash - Signal Books Bot
echo ======================================================
echo    Signal Books loyihasini GitHub'ga yuklash
echo ======================================================
echo.
echo GitHub hisobingiz bilan avtorizatsiya oynasi ochiladi...
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo ======================================================
    echo   [MUVAFFAQIYATLI] Loyiha GitHub'ga yuklandi!
    echo ======================================================
) else (
    echo ======================================================
    echo   [XATOLIK] Yuklashda muammo yuz berdi.
    echo ======================================================
)
pause
