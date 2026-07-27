Write-Host "Stopping and removing Docker containers..." -ForegroundColor Green

function Stop-And-Remove-Container {
    Write-Host "Stopping and Deleting PostgreSQL container..." -ForegroundColor Yellow
    docker compose down -v
    Start-Sleep -Seconds 5
}

try {
    $containerStatus = docker inspect book_recommendator_db --format='{{.State.Status}}' 2>$null
    if ($containerStatus) {
        Stop-And-Remove-Container
        Write-Host "PostgreSQL container stopped and removed successfully!" -ForegroundColor Green
    } else {
        Write-Host "No running PostgreSQL container found." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Docker container not found or error occurred." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}