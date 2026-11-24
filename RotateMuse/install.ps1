param([Parameter(Mandatory=$true)][string]$Adb,[string]$Serial='')
$ErrorActionPreference='Stop'
$apk=Join-Path $PSScriptRoot 'app\build\outputs\apk\debug\app-debug.apk'
if (!(Test-Path -LiteralPath $apk)) { throw 'Build the APK first.' }
Write-Host 'Install only when finished gaming. This does not launch the app or change HOME.'
$adbArgs=@()
if ($Serial) { $adbArgs=@('-s',$Serial) }
& $Adb @adbArgs install -r $apk
if ($LASTEXITCODE -ne 0) { throw 'ADB installation failed; no uninstall will be attempted.' }
