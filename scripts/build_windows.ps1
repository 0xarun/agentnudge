param(
    [string]$Version = "0.1.0"
)

$ErrorActionPreference = "Stop"

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

pyinstaller --noconfirm --clean --onefile --noconsole --name "AgentNudgeReminder" main.py

New-Item -ItemType Directory -Path release -Force | Out-Null
Copy-Item -Path dist/AgentNudgeReminder.exe -Destination "release/AgentNudgeReminder-v$Version-windows-x64.exe"

Write-Host "Built: release/AgentNudgeReminder-v$Version-windows-x64.exe"
