@echo off
echo 正在使用 PyInstaller 打包项目...

REM 进入脚本所在目录
cd /d %~dp0

REM 打包命令（添加图标目录）
pyinstaller --noconsole --onefile --add-data "icons;icons" main.py

echo 打包完成！请查看 dist 文件夹。
pause