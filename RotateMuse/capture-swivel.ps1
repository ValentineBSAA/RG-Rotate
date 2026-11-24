param([Parameter(Mandatory=$true)][string]$Adb,[string]$Serial='')
$ErrorActionPreference='Stop'
$out=Join-Path $PSScriptRoot 'logs'
New-Item -ItemType Directory -Path $out -Force | Out-Null
Write-Host 'Read-only capture. Manually open/close three times. Press Ctrl+C to stop. No synthetic events are sent.'
$adbArgs=@()
if ($Serial) { $adbArgs=@('-s',$Serial) }
& $Adb @adbArgs shell getevent -lt | Tee-Object -FilePath (Join-Path $out ('swivel-'+(Get-Date -Format 'yyyyMMdd-HHmmss')+'.txt'))
