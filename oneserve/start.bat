@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "PYTHON_EXE=C:\Users\PRABATH\AppData\Local\Programs\Python\Python312\python.exe"
set "NODE_DIR=C:\Program Files\nodejs"
set "NPM_CMD=%NODE_DIR%\npm.cmd"

if not exist "%PYTHON_EXE%" (
  echo Python was not found at:
  echo %PYTHON_EXE%
  pause
  exit /b 1
)

if exist "%NPM_CMD%" (
  set "PATH=%NODE_DIR%;%PATH%"
  if not exist "%FRONTEND_DIR%\dist\index.html" (
    echo Frontend build not found. Building frontend...
    pushd "%FRONTEND_DIR%"
    call "%NPM_CMD%" run build
    if errorlevel 1 (
      echo Frontend build failed.
      popd
      pause
      exit /b 1
    )
    popd
  )
) else (
  echo Node.js was not found. Using the last available frontend build if it exists.
)

echo Starting OneServe on http://127.0.0.1:8000
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:8000"

pushd "%BACKEND_DIR%"
"%PYTHON_EXE%" -m uvicorn main:app --host 127.0.0.1 --port 8000
popd

endlocal
