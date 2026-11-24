param([string]$Sdk=$env:ANDROID_HOME,[string]$Jdk=$env:JAVA_HOME,[string]$Gradle='gradle')
$ErrorActionPreference='Stop'
if (!$Sdk -or !(Test-Path -LiteralPath $Sdk)) { throw 'Pass -Sdk with the Android SDK directory.' }
if (!$Jdk -or !(Test-Path -LiteralPath "$Jdk\bin\java.exe")) { throw 'Pass -Jdk with a JDK 17 directory.' }
$env:JAVA_HOME=$Jdk
$env:ANDROID_HOME=$Sdk
$env:PATH="$Jdk\bin;$env:PATH"
Set-Location $PSScriptRoot
Set-Content -LiteralPath 'local.properties' -Value ('sdk.dir='+$Sdk.Replace('\','/')) -Encoding ascii
& $Gradle --no-daemon --max-workers=1 ':app:testDebugUnitTest' ':app:lintDebug' ':app:assembleDebug'
if ($LASTEXITCODE -ne 0) { throw 'Build or tests failed.' }
Get-FileHash -Algorithm SHA256 -LiteralPath 'app\build\outputs\apk\debug\app-debug.apk'
