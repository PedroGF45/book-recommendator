# This script initializes the database using the existing Docker container

Write-Host "Initializing database using Docker container..." -ForegroundColor Green

function Start-Container {
    Write-Host "Starting PostgreSQL container..." -ForegroundColor Yellow
    docker compose up -d
    Start-Sleep -Seconds 5
}

function Stop-And-Remove-Container {
    Write-Host "Stopping and Deleting PostgreSQL container..." -ForegroundColor Yellow
    docker compose down -v
    Start-Sleep -Seconds 5
}

try {
    $containerStatus = docker inspect book_recommendator_db --format='{{.State.Status}}' 2>$null
    if ($containerStatus) {
        Stop-And-Remove-Container
    }
    Start-Container
    Write-Host "PostgreSQL container is running" -ForegroundColor Green
} catch {
    Write-Host "Docker container not found or error occurred. Starting with docker-compose..." -ForegroundColor Yellow
    Start-Container
}

Write-Host "Creating database if it doesn't exist..." -ForegroundColor Yellow
try {
    docker exec book_recommendator_db psql -U dev_user -d postgres -c "CREATE DATABASE dev_book_recommendator_db IF NOT EXISTS;" 2>$null
    Write-Host "Database created or already exists" -ForegroundColor Green
} catch {
    Write-Host "Database already exists or creation attempted" -ForegroundColor Yellow
}

Write-Host "Creating database schema..." -ForegroundColor Yellow
try {
    docker cp database\schema.sql book_recommendator_db:/tmp/schema.sql
    docker exec book_recommendator_db psql -U dev_user -d dev_book_recommendator_db -f /tmp/schema.sql
    Write-Host "Database schema created successfully!" -ForegroundColor Green
} catch {
    Write-Host "Failed to create database schema" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host "Verifying tables..." -ForegroundColor Yellow
try {
    $output = docker exec book_recommendator_db psql -U dev_user -d dev_book_recommendator_db -c "\dt"
    Write-Host $output
    
    Write-Host ""
    Write-Host "Users table structure:" -ForegroundColor Cyan
    $userTableOutput = docker exec book_recommendator_db psql -U dev_user -d dev_book_recommendator_db -c "\d users"
    Write-Host $userTableOutput
    
    Write-Host ""
    Write-Host "Database initialization completed successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "Failed to verify tables" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}