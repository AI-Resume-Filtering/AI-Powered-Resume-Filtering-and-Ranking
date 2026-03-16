$ErrorActionPreference = "Stop"

function Test-MongoListening {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $async = $client.BeginConnect("127.0.0.1", 27017, $null, $null)
        $ok = $async.AsyncWaitHandle.WaitOne(1200)
        if (-not $ok) {
            $client.Close()
            return $false
        }
        $client.EndConnect($async)
        $client.Close()
        return $true
    } catch {
        return $false
    }
}

function Ensure-MongoRunning {
    if (Test-MongoListening) {
        Write-Host "MongoDB is already running on 127.0.0.1:27017"
        return
    }

    $mongodPath = "C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe"
    $dbPath = "D:\AI_POWER_RESUME_FILERTRING\mongodb-data"

    if (-not (Test-Path $mongodPath)) {
        throw "mongod.exe not found at $mongodPath. Install MongoDB Server or update path in start_backend.ps1"
    }

    if (-not (Test-Path $dbPath)) {
        New-Item -ItemType Directory -Path $dbPath | Out-Null
    }

    Write-Host "Starting MongoDB process..."
    Start-Process -FilePath $mongodPath -ArgumentList @(
        "--dbpath", $dbPath,
        "--bind_ip", "127.0.0.1",
        "--port", "27017"
    ) | Out-Null

    Start-Sleep -Seconds 2

    if (-not (Test-MongoListening)) {
        throw "MongoDB did not start correctly. Check mongod logs and dbpath permissions."
    }

    Write-Host "MongoDB started successfully."
}

Ensure-MongoRunning

$backendRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendRoot

$pythonExe = "D:\AI_POWER_RESUME_FILERTRING\.venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    throw "Python executable not found at $pythonExe"
}

Write-Host "Starting backend API..."
& $pythonExe "run.py"
