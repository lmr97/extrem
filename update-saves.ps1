# this script copies the given file to your external drive,
# then saves it to your Google Drive.

# Usage: 
# update-saves.ps1 -File FILE [-Folder FOLDER]

# 
Param (
    [Parameter(Mandatory=$true)]
    [string] $File,

    [string] $Folder
    )

# get configured path to external drive (no need to make it a parameter)
$ExternalDrivePaths = Get-Content '.\utils\external_drive_paths.json' | Out-String | ConvertFrom-Json


# configure external drive path for current OS if it's not there
If($IsWindows -AND !$ExternalDrivePaths.DOSFilePath -OR (($IsMacOS -OR $IsLinux) -AND !$ExternalDrivePaths.UnixFilePath))
{
    python3 .\utils\config_ext_drive.py
}

python3 .\utils\ensure_slashes.py  # check that it's got slashes at the end regardless


If(Test-Path $ExternalDrivePaths.DOSFilePath)
{
    Copy-Item -Path .\$File -Destination $ExternalDrivePaths.DOSFilePath+$Folder
}
Else
{
    $RedMessage   = "**It looks like the external hard drive is not connected.**"
    $WhiteMessage = "  Please check to make sure it's plugged in, and try running this program again."
    Write-Host
    Write-Host " "($RedMessage | ConvertFrom-Markdown -AsVT100EncodedString).VT100EncodedString -ForegroundColor Red
    Write-Host $WhiteMessage
    Write-Host
    Exit 1
}

poetry run python save_to_google_drive.py $File $Folder

Exit 0