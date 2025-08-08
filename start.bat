@echo off
echo 🚀 Starting Credit Approval System...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

REM Build and start the application
echo 📦 Building and starting containers...
docker-compose up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Check if the web service is running
docker-compose ps | findstr "web.*Up" >nul
if errorlevel 1 (
    echo ❌ Application failed to start. Check logs with:
    echo    docker-compose logs
    pause
    exit /b 1
) else (
    echo ✅ Application is running!
    echo 🌐 API: http://localhost:8000/api/
    echo 🔧 Admin: http://localhost:8000/admin/
    echo.
    echo 📊 To ingest data, run:
    echo    docker-compose exec web python manage.py ingest_data
    echo.
    echo 🧪 To test the API, run:
    echo    python test_api.py
    echo.
    echo 📋 To view logs, run:
    echo    docker-compose logs -f
)

pause 