param(
    [string]$MongoDbPath = "",
    [string]$MongoLogPath = "",
    [double]$MongoCacheGB = 0.25,
    [int]$BackendPort = 5000,
    [int]$FrontendPort = 5173,
    [int]$MongoPort = 27017
)

$ErrorActionPreference = "Stop"

$TestPortOpen = {
    param(
        [string]$Address,
        [int]$Port,
        [int]$TimeoutMs = 600
    )

    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $iar = $client.BeginConnect($Address, $Port, $null, $null)
        $ok = $iar.AsyncWaitHandle.WaitOne($TimeoutMs, $false)
        if (-not $ok) {
            $client.Close()
            return $false
        }
        $client.EndConnect($iar)
        $client.Close()
        return $true
    }
    catch {
        return $false
    }
}

function Get-LanIPv4 {
    try {
        $ips = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction Stop |
            Where-Object {
                $_.IPAddress -ne "127.0.0.1" -and
                $_.IPAddress -notlike "169.254.*" -and
                $_.PrefixOrigin -ne "WellKnown"
            }
        if ($ips) {
            return ($ips | Select-Object -First 1).IPAddress
        }
    }
    catch {
    }
    return "127.0.0.1"
}

function Ensure-EnvFile {
    param(
        [string]$EnvPath,
        [string]$ExamplePath,
        [string]$DefaultContent
    )

    if (Test-Path $EnvPath) {
        return
    }

    if (Test-Path $ExamplePath) {
        Copy-Item -Path $ExamplePath -Destination $EnvPath -Force
        Write-Host "Created env file from template: $EnvPath" -ForegroundColor Green
        return
    }

    Set-Content -Path $EnvPath -Value $DefaultContent -Encoding UTF8
    Write-Host "Created fallback env file: $EnvPath" -ForegroundColor Yellow
}

$projectRoot = $PSScriptRoot
$workspaceRoot = Split-Path -Parent $projectRoot
$backendDir = Join-Path $projectRoot "Backend"
$frontendDir = Join-Path $projectRoot "Frontend\react-project"

if (-not (Test-Path $backendDir)) {
    throw "Backend folder not found at: $backendDir"
}
if (-not (Test-Path $frontendDir)) {
    throw "Frontend folder not found at: $frontendDir"
}

$backendEnvPath = Join-Path $backendDir ".env"
$backendEnvExample = Join-Path $backendDir ".env.example"
$backendFallbackEnv = @"
SECRET_KEY=dev-only-change-this-to-a-32-char-or-longer-random-secret
MONGO_URI=mongodb://localhost:27017
MONGO_DB=resume_filtering
FRONTEND_BASE_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
SCORE_THRESHOLD=70
FEEDBACK_RETRAIN_THRESHOLD=50
FEEDBACK_MIN_TRAIN_SAMPLES=20
MAX_CONTENT_LENGTH=20971520
"@
Ensure-EnvFile -EnvPath $backendEnvPath -ExamplePath $backendEnvExample -DefaultContent $backendFallbackEnv

$frontendEnvPath = Join-Path $frontendDir ".env"
$frontendEnvExample = Join-Path $frontendDir ".env.example"
$frontendFallbackEnv = @"
VITE_API_BASE_URL=/api
"@
Ensure-EnvFile -EnvPath $frontendEnvPath -ExamplePath $frontendEnvExample -DefaultContent $frontendFallbackEnv

if (-not $MongoDbPath) {
    $MongoDbPath = Join-Path $workspaceRoot "mongodb-data"
}
if (-not $MongoLogPath) {
    $MongoLogPath = Join-Path $workspaceRoot "mongodb-log\mongod.log"
}

$mongoLogDir = Split-Path -Parent $MongoLogPath
if (-not (Test-Path $MongoDbPath)) {
    New-Item -ItemType Directory -Path $MongoDbPath | Out-Null
}
if (-not (Test-Path $mongoLogDir)) {
    New-Item -ItemType Directory -Path $mongoLogDir | Out-Null
}

$mongodExeCandidates = @(
    "C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe",
    "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe",
    "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe"
)

$mongodExe = $mongodExeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $mongodExe) {
    $mongodCmd = Get-Command mongod -ErrorAction SilentlyContinue
    if ($mongodCmd) {
        $mongodExe = $mongodCmd.Source
    }
}
if (-not $mongodExe) {
    throw "mongod executable not found. Install MongoDB server first."
}

if (-not (& $TestPortOpen -Address "127.0.0.1" -Port $MongoPort)) {
    $mongoArgs = @(
        "--dbpath", $MongoDbPath,
        "--logpath", $MongoLogPath,
        "--logappend",
        "--bind_ip", "127.0.0.1",
        "--port", "$MongoPort",
        "--wiredTigerCacheSizeGB", "$MongoCacheGB"
    )

    Start-Process -FilePath $mongodExe -ArgumentList $mongoArgs -WindowStyle Hidden | Out-Null
    Start-Sleep -Seconds 2

    if (-not (& $TestPortOpen -Address "127.0.0.1" -Port $MongoPort)) {
        throw "MongoDB did not start on port $MongoPort. Check log: $MongoLogPath"
    }

    Write-Host "MongoDB started on port $MongoPort" -ForegroundColor Green
}
else {
    Write-Host "MongoDB already running on port $MongoPort" -ForegroundColor Yellow
}

$pythonCandidates = @(
    "C:\Users\ughad\env\Scripts\python.exe",
    (Join-Path $backendDir ".venv\Scripts\python.exe"),
    (Join-Path $backendDir "venv\Scripts\python.exe")
)
$pythonExe = $pythonCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $pythonExe) {
    $pythonExe = "python"
}

if (-not (& $TestPortOpen -Address "127.0.0.1" -Port $BackendPort)) {
    $backendCmd = "Set-Location '$backendDir'; `$env:PYTHONIOENCODING='utf-8'; & '$pythonExe' run.py"
    Start-Process -FilePath "powershell" -ArgumentList @("-NoExit", "-Command", $backendCmd) | Out-Null
    Write-Host "Backend starting on port $BackendPort" -ForegroundColor Green
}
else {
    Write-Host "Backend already running on port $BackendPort" -ForegroundColor Yellow
}

if (-not (& $TestPortOpen -Address "127.0.0.1" -Port $FrontendPort)) {
    $frontendCmd = "Set-Location '$frontendDir'; npm run dev -- --host 0.0.0.0 --port $FrontendPort"
    Start-Process -FilePath "powershell" -ArgumentList @("-NoExit", "-Command", $frontendCmd) | Out-Null
    Write-Host "Frontend starting on port $FrontendPort" -ForegroundColor Green
}
else {
    Write-Host "Frontend already running on port $FrontendPort" -ForegroundColor Yellow
}

Start-Sleep -Seconds 2

$lanIp = Get-LanIPv4
Write-Host "" 
Write-Host "Dev stack launch complete" -ForegroundColor Cyan
Write-Host "Desktop URL: http://localhost:$FrontendPort" -ForegroundColor Cyan
Write-Host "Mobile URL:  http://$lanIp`:$FrontendPort" -ForegroundColor Cyan
Write-Host "API URL:     http://localhost:$BackendPort/api" -ForegroundColor Cyan
Write-Host "" 
Write-Host "Keep launched terminal windows open while developing." -ForegroundColor DarkCyan
