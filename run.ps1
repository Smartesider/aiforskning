# AI Ethics Testing Framework - PowerShell Setup and Runner
# Usage: .\run.ps1 [command]

param(
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "🧠 AI Ethics Testing Framework" -ForegroundColor Blue
    Write-Host "================================" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Available commands:" -ForegroundColor Yellow
    Write-Host "  setup    - Install dependencies and initialize database"
    Write-Host "  test     - Run framework tests"
    Write-Host "  demo     - Run demonstration"
    Write-Host "  web      - Launch web dashboard"
    Write-Host "  init     - Initialize database only"
    Write-Host "  help     - Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\run.ps1 setup"
    Write-Host "  .\run.ps1 demo"
    Write-Host "  .\run.ps1 web"
}

function Install-Dependencies {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    
    # Check if Python is available
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Found Python: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
        exit 1
    }
    
    # Install Flask
    Write-Host "Installing Flask..." -ForegroundColor Yellow
    python -m pip install flask
    
    Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
}

function Initialize-Database {
    Write-Host "🗄️ Initializing database..." -ForegroundColor Yellow
    python main.py init
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database initialized successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Database initialization failed!" -ForegroundColor Red
        exit 1
    }
}

function Run-Tests {
    Write-Host "🧪 Running framework tests..." -ForegroundColor Yellow
    python test_framework.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ All tests passed!" -ForegroundColor Green
    } else {
        Write-Host "❌ Some tests failed!" -ForegroundColor Red
        exit 1
    }
}

function Run-Demo {
    Write-Host "🎭 Running demonstration..." -ForegroundColor Yellow
    python demo.py
}

function Start-WebDashboard {
    Write-Host "🌐 Starting web dashboard..." -ForegroundColor Yellow
    Write-Host "Dashboard will be available at: http://localhost:5000" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    python main.py web
}

# Main execution
switch ($Command.ToLower()) {
    "setup" {
        Install-Dependencies
        Initialize-Database
        Write-Host ""
        Write-Host "🎉 Setup complete! Try running:" -ForegroundColor Green
        Write-Host "  .\run.ps1 test"
        Write-Host "  .\run.ps1 demo"
        Write-Host "  .\run.ps1 web"
    }
    
    "test" {
        Run-Tests
    }
    
    "demo" {
        Run-Demo
    }
    
    "web" {
        Start-WebDashboard
    }
    
    "init" {
        Initialize-Database
    }
    
    "help" {
        Show-Help
    }
    
    default {
        Write-Host "❌ Unknown command: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
        exit 1
    }
}
