@echo off
echo 启动后端服务器...
echo.

cd backend

echo 激活Python虚拟环境...
call C:\Users\ASUS\anaconda3\Scripts\activate.bat web

echo 安装Python依赖...
pip install -r requirements.txt

echo.
echo 启动后端服务器...
python run.py

pause