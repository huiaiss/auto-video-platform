@echo off
setlocal enabledelayedexpansion
:: API keys are loaded from .env file
:: set VOLC_TTS_API_KEY=YOUR_API_KEY_HERE
set VOLC_TTS_RESOURCE_ID=seed-tts-2.0
cd /d "D:\auto-video-platform"
start /B "" "C:\Python314\python.exe" generators\ark_tts_proxy.py 8791
