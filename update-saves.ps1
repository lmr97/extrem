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

If(Test-Path D:\exdrive)
{
    Copy-Item -Path .\$File -Destination \home\martinr\$Folder
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