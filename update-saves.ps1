# this script copies the given file to your external drive,
# then saves it to your Google Drive.


# get configured path to external drive (no need to make it a parameter)
$ExternalDrivePaths = Get-Content '.\utils\external_drive_paths.json' | Out-String | ConvertFrom-Json


# configure external drive path for current OS if it's not there
If($IsWindows -AND !$ExternalDrivePaths.DOSFilePath -OR (($IsMacOS -OR $IsLinux) -AND !$ExternalDrivePaths.UnixFilePath))
{
    $ProperSysPath = Convert-Path -LiteralPath "./utils/config_ext_drive.py"
    python3 $ProperSysPath
}

$ProperSysPath = Convert-Path -LiteralPath "./utils/ensure_slashes.py"
python3 $ProperSysPath  # check that it's got slashes at the end regardless, in case of change

# refresh data after slash check
$ExternalDrivePaths = Get-Content '.\utils\external_drive_paths.json' | Out-String | ConvertFrom-Json



Write-Host
Write-Host "Enter the file name you'd like to save, with its path (e.g. C:\Documents\MyFile.pdf)"
$File = Read-Host
Write-Host
Write-Host "Now enter the name of the folder where you'd like to put the file"
Write-Host "in both your external drive and your Google Drive."
Write-Host "(this is optional; just press Enter if you don't need it in a folder.)"
$Folder = Read-Host

# if the relevant, configured path exists
If($IsWindows -AND (Test-Path $ExternalDrivePaths.DOSFilePath) -OR `
  (($IsMacOS -OR $IsLinux) -AND (Test-Path $ExternalDrivePaths.UnixFilePath)))
{
    If ($IsWindows)
    {
        Copy-Item -Path $File -Destination ($ExternalDrivePaths.DOSFilePath+$Folder)
    }

    ElseIf ($IsMacOS -OR $IsLinux)
    {
        Copy-Item -Path $File -Destination ($ExternalDrivePaths.UnixFilePath+$Folder+"/")
    }
    Else 
    {
        Write-Host "Operating system not supported. Exiting..."
        Return 1
    }

    Write-Host
    Write-Host "Saved to external drive!" -ForegroundColor Green
}
Else
{
    $RedMessage   = "**It looks like the external hard drive is not connected.**"
    $WhiteMessage = "  Please check to make sure it's plugged in, and try running this program again."
    Write-Host
    Write-Host " "($RedMessage | ConvertFrom-Markdown `
        -AsVT100EncodedString).VT100EncodedString -ForegroundColor Red
    Write-Host $WhiteMessage
    Write-Host
    Return
}

Write-Host "Saving to Google Drive now..." -ForegroundColor White  # resetting color
poetry run python save_to_google_drive.py $File $Folder

Return