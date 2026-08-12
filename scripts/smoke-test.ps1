$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Internal Developer Platform - Smoke Test"
Write-Host "========================================"
Write-Host ""

Write-Host "Validating Docker Compose configuration..."
docker compose config | Out-Null

Write-Host "Starting platform..."
docker compose up -d --build

$services = @(
    @{
        Name = "Platform API"
        Url = "http://localhost:8000/health"
    },
    @{
        Name = "Service Catalog"
        Url = "http://localhost:8001/health"
    },
    @{
        Name = "Template Engine"
        Url = "http://localhost:8002/health"
    },
    @{
        Name = "Workflow Engine"
        Url = "http://localhost:8003/health"
    },
    @{
        Name = "Developer Portal API"
        Url = "http://localhost:8004/health"
    },
    @{
        Name = "Identity Service"
        Url = "http://localhost:8005/health"
    },
    @{
        Name = "Policy Engine"
        Url = "http://localhost:8006/health"
    },
    @{
        Name = "Event Platform"
        Url = "http://localhost:8007/health"
    }
)

foreach ($service in $services) {
    $healthy = $false

    for ($attempt = 1; $attempt -le 30; $attempt++) {
        try {
            $response = Invoke-RestMethod `
                -Uri $service.Url `
                -Method Get `
                -TimeoutSec 3

            if ($response.status -eq "ok") {
                $healthy = $true
                break
            }
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }

    if (-not $healthy) {
        Write-Host ""
        Write-Host "$($service.Name) failed health validation."
        docker compose ps
        docker compose logs --tail=100
        exit 1
    }

    Write-Host "$($service.Name): OK"
}

Write-Host ""
Write-Host "Running end-to-end provisioning journey..."

$serviceName = "smoke-api-$([Guid]::NewGuid().ToString('N').Substring(0,8))"

$payload = @{
    name = $serviceName
    owner = "platform-team"
    repository = "https://github.com/example/$serviceName"
    description = "Smoke test service"
    template = "backend-service"
    environment = "development"
} | ConvertTo-Json

$result = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/provision/services" `
    -Method Post `
    -ContentType "application/json" `
    -Body $payload

if ($result.status -ne "provisioning") {
    throw "Provisioning workflow failed."
}

if ($result.policy -ne "allowed") {
    throw "Policy validation failed."
}

if ($result.catalog -ne "registered") {
    throw "Catalog registration failed."
}

if ($result.workflow -ne "started") {
    throw "Workflow execution failed."
}

Write-Host ""
Write-Host "Provisioned service: $serviceName"
Write-Host "Policy: $($result.policy)"
Write-Host "Catalog: $($result.catalog)"
Write-Host "Workflow: $($result.workflow)"
Write-Host ""
Write-Host "PLATFORM SMOKE TEST PASSED"
Write-Host ""
