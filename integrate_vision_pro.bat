@echo off
echo 🚀 Vision Pro Integration Complete - Run Services
echo.

echo Terminal 1 ^(Bridge^):
echo cd bridge
echo npm install
echo npm start
echo.

echo Terminal 2 ^(Dashboard^):
echo cd vision-pro
echo npm install
echo npm run dev
echo ^(Open localhost:3000^)
echo.

echo Terminal 3 ^(Bot^):
echo pip install requests
echo python main_playtech.py
echo.

echo All ready! Dashboard receives realtime signals from bot via bridge.
pause
