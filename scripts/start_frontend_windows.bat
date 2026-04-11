@echo off
setlocal

cd apps\web
call npm install
set NEXT_PUBLIC_API_URL=http://localhost:8000
call npm run dev

endlocal
