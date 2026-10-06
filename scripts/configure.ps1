# Generate a local deployment secret without putting it in terminal output or source control.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$envPath = Join-Path $projectRoot '.env'
if (Test-Path -LiteralPath $envPath) { throw 'Root .env already exists; edit it instead of overwriting it.' }
$passwordBytes = New-Object byte[] 32
$random = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$random.GetBytes($passwordBytes)
$random.Dispose()
$password = [BitConverter]::ToString($passwordBytes).Replace('-', '').ToLowerInvariant()
[IO.File]::WriteAllText($envPath, "POSTGRES_PASSWORD=$password`nAPP_PORT=3000`nRAG_EMBEDDING_PROVIDER=deterministic`n", [Text.UTF8Encoding]::new($false))
Write-Output 'Created ignored root .env. Run docker compose up --build -d.'
