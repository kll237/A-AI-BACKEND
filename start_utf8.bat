@echo off
chcp 65001 > nul
title AI摄像头系统 (UTF-8模式)
echo ========================================
echo AI摄像头系统 - UTF-8编码启动
echo ========================================
echo.

echo 停止现有进程...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo 设置Python环境...
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set LANG=zh_CN.UTF-8

echo.
echo 启动系统...
echo 请稍候...
echo.
echo 访问地址:
echo   API文档: http://localhost:8000/docs
echo   健康检查: http://localhost:8000/health
echo.
echo ========================================
echo.

"C:\Users\Administrator\miniconda3\envs\pytorch\python.exe" launch_utf8.py

pause
