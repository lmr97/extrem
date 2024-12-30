# this script copies the given file to your external drive,
# then saves it to your Google Drive.


# get configured path to external drive (no need to make it a parameter)
$ExternalDrivePaths = Get-Content '.\utils\external_drive_paths.json' | Out-String | ConvertFrom-Json


# configure external drive path for current OS if it's not there
If(($IsWindows -AND ($ExternalDrivePaths.DOSFilePath -Eq "")) -OR (($IsMacOS -OR $IsLinux) -AND ($ExternalDrivePaths.UnixFilePath -Eq "")))
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
# SIG # Begin signature block
# MIIFlAYJKoZIhvcNAQcCoIIFhTCCBYECAQExCzAJBgUrDgMCGgUAMGkGCisGAQQB
# gjcCAQSgWzBZMDQGCisGAQQBgjcCAR4wJgIDAQAABBAfzDtgWUsITrck0sYpfvNR
# AgEAAgEAAgEAAgEAAgEAMCEwCQYFKw4DAhoFAAQUXF9MHUCPFvqsRItjCQcpKOZ5
# equgggMiMIIDHjCCAgagAwIBAgIQaA/0xUIYB6tIVu0ozjiBMzANBgkqhkiG9w0B
# AQsFADAnMSUwIwYDVQQDDBxQb3dlclNoZWxsIENvZGUgU2lnbmluZyBDZXJ0MB4X
# DTI0MTExNzE5NTQyNFoXDTI1MTExNzIwMTQyNFowJzElMCMGA1UEAwwcUG93ZXJT
# aGVsbCBDb2RlIFNpZ25pbmcgQ2VydDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCC
# AQoCggEBAMWjqzSPVCgWKZ1N10ixRqnB5+lZCAbYcA0DLwXUhs9VbCXFMvGSZfOG
# hhQBfewSCSWlmNrbM9vqMKXGbHLnOIkK2jnpOxuZSdeb0WlqeW9T2bVPCnyezLzX
# eCZo7ySypHn4BF+kNHFu2aGXsf1flwFKSsnhqWD5sQUpTIN45EE3/+ZhCOsWxxoV
# VmD7RQkQ03xqOuHJk9L2slvVwUV4v87Hqw17C/SBQmwVpCyEuSROQ8LEbOW3RTZc
# +V+2SgpI49++yh5jSCOHiBoEfVZWp8OJAyd8XIFT7QkdJ9SVbQ1C9MrfEieKllKj
# 7TWE9XPwif4tIP2MoIs2P7lGLbEW5D0CAwEAAaNGMEQwDgYDVR0PAQH/BAQDAgeA
# MBMGA1UdJQQMMAoGCCsGAQUFBwMDMB0GA1UdDgQWBBRibWvKB2pKDmGwaDYHj4qO
# X7xW6jANBgkqhkiG9w0BAQsFAAOCAQEAFhH2+oLn8Ps8t5JzIDUQOH3Otlk350MG
# OXSvF+zaGAN+diFowGIZLX8qg1ZnpGKaiVXZXLTWc4p8vuO7xYm3dTSAY2ml3qg1
# Pn/g9MNAfwD3q1q9PWJUqnXPmUm5rcW3XH9oXf3sewWUAl10wrkTWRKc+kp+Jrqs
# HqkqCAWafRVIqb+nJixx4qAL/YZkwgV9qNAvcLPOO6NP6S1JjgjgwbQ0pMfLUMVL
# E1IMP7gQTt/STggTayly4DU0j9G9oHle8hLa3ebDTImnE6t+UAE/p/iMhinSZM/B
# XMtHfp2YvzmvrzrbCO3xQ7q0Or7pPiNsF671dY2+EAsHg/1uUBrFIDGCAdwwggHY
# AgEBMDswJzElMCMGA1UEAwwcUG93ZXJTaGVsbCBDb2RlIFNpZ25pbmcgQ2VydAIQ
# aA/0xUIYB6tIVu0ozjiBMzAJBgUrDgMCGgUAoHgwGAYKKwYBBAGCNwIBDDEKMAig
# AoAAoQKAADAZBgkqhkiG9w0BCQMxDAYKKwYBBAGCNwIBBDAcBgorBgEEAYI3AgEL
# MQ4wDAYKKwYBBAGCNwIBFTAjBgkqhkiG9w0BCQQxFgQU6PrI44R7v/bwTezMpq4p
# Q26qk+gwDQYJKoZIhvcNAQEBBQAEggEABx+0ZYsPeGPbB0yaTkWFdT1yXi8My1rq
# sNNllvdI0Ru/WZ4zVHbFQGB7jrmEseoYc3TJPm10syUARO1kRm5SDYXP7VCcCZiq
# CrA3niFP9/RjMMXAoQo+i0JVGRvPR4Qb5PFK2VVrS/A6jKN7N6YVRmSGJh6w1dOY
# 6Axy/IurhbOCHkZjiOp80Uw46bF0S0K41Xq5dehwVUrIvrJd//I4anO03XxEoYtA
# qu3hc5GcBE3f0oKiTZZYDsFFyzlO1Cg++yZht91CdR9fyu8Pm+bCOGQhn0mb5qGC
# mOPBfhK4kwpWigccYEw9jFPXavh3/JZsC3b4R1n8iQaRti0762tQ0g==
# SIG # End signature block
