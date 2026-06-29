param([string]$InstallDir)

$dir = $InstallDir.TrimEnd('\').TrimEnd('/')

$ws = New-Object -ComObject WScript.Shell

$desktop = [Environment]::GetFolderPath('Desktop')
$s = $ws.CreateShortcut("$desktop\Claude Usage Widget.lnk")

# Prefer pythonw.exe (no console window) — fall back to launch.bat
$pythonCmd = Get-Command "pythonw.exe" -ErrorAction SilentlyContinue
if ($pythonCmd) {
    $s.TargetPath = $pythonCmd.Source
    $s.Arguments = "`"$dir\main.py`""
} else {
    $s.TargetPath = "$dir\launch.bat"
}

$s.WorkingDirectory = $dir
$s.Description = "Claude Usage Widget - shows your Claude.ai usage in real time"
$s.Save()

Write-Host "Desktop shortcut created: Claude Usage Widget"
