@echo off
chcp 65001 >nul
set "WORKSPACE=%~dp0"
set "PYTHON=C:\Users\frank\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
echo 正在启动数据岗位 PDCA 工作台...
echo 浏览器会自动打开；关闭这个窗口即可停止工作台。
"%PYTHON%" "%WORKSPACE%scripts\pdca_workbench.py"
pause
