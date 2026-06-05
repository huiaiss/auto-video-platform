@echo off
setlocal enabledelayedexpansion

:: HUNYUAN_SECRET_ID and KEY are loaded from .env file
:: set HUNYUAN_SECRET_ID=YOUR_SECRET_ID_HERE
:: set HUNYUAN_SECRET_KEY=YOUR_SECRET_KEY_HERE

cd /d "D:\auto-video-platform"
start /B "" "C:\Python314\python.exe" generators\hunyuan_proxy.py 8789
