@echo off
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
title Signal Books - Telegram Web App Bot

echo ======================================================
echo          Signal Books Telegram Boti Ishga Tushmoqda...
echo ======================================================

if not exist venv (
    echo [1/2] Virtual muhit yaratilmoqda...
    py -m venv venv
    echo [2/2] Kutubxonalar o'rnatilmoqda...
    call .\venv\Scripts\pip install -r requirements.txt
)

echo.
echo Bot ishga tushirilmoqda...
call .\venv\Scripts\python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ------------------------------------------------------
    echo Bot to'xtadi yoki xatolik yuz berdi.
    echo Iltimos, yuqoridagi xabarni va .env faylini tekshiring.
    echo ------------------------------------------------------
    pause
)
