@echo off
echo 正在安装PyInstaller...
pip install pyinstaller

echo.
echo 正在编译FTP工具...
pyinstaller --onefile --windowed --name "FTP工具" ftp_gui_complete.py

echo.
echo 编译完成！可执行文件在 dist 文件夹中
pause