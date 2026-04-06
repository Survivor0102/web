@echo off
echo 启动前端开发服务器...
echo.

cd frontend

echo 安装依赖...
call npm install

echo.
echo 启动开发服务器...
call npm run dev

pause