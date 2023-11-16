# script.ps1

# Find the process ID of the process running on port 6570
$port = 6570
$process = Get-NetTCPConnection -LocalPort $port | Select-Object -Property OwningProcess -Unique

# If a process is found, stop it
if ($process) {
    Stop-Process -Id $process.OwningProcess -Force
}

# Navigate to the directory containing your venv
cd ./venv/Scripts/

# Activate the virtual environment
. .\Activate.ps1

# Navigate back to the parent directory
cd ../..

# Run your command
uvicorn main:app --port 6570
