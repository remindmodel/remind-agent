param(
    [switch]$Reverse,
    [switch]$Force,
    [string]$RemindPath
)

$ContextDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DefaultRemindPath = "$env:USERPROFILE\remind"
$ContextFiles = @("copilot-instructions.md", "instructions/", "prompts/")

if (-not $RemindPath) { $RemindPath = $DefaultRemindPath }

function Usage {
    Write-Host "Usage: .\copy-context.ps1 [-Reverse] [-Force] [[-IngressPath] <path>]"
    Write-Host ""
    Write-Host "  RemindPath   Path to the REMIND codebase (default: $DefaultRemindPath)"
    Write-Host "  -Reverse      Reverse: copy from REMIND back to ingress-context"
    Write-Host "  -Force        Skip diff check and overwrite without prompting"
    exit 1
}

function Test-DiffCheck {
    param($Src, $Dst)
    if (-not (Test-Path $Dst)) { return }
    $srcItems = Get-ChildItem -Recurse $Src -ErrorAction SilentlyContinue
    $dstItems = Get-ChildItem -Recurse $Dst -ErrorAction SilentlyContinue
    if (-not $srcItems) { return }
    $diff = Compare-Object $srcItems $dstItems -Property Name, Length
    if ($diff) {
        Write-Host "Warning: '$Dst' differs from source."
        $confirm = Read-Host "Overwrite? [y/N]"
        if ($confirm -notmatch '^[yY]$') {
            Write-Host "Aborted."
            exit 1
        }
    }
}

if (-not (Test-Path $RemindPath)) {
    Write-Host "Error: REMIND path '$RemindPath' does not exist"
    exit 1
}

if ($Reverse) {
    Write-Host "Copying context files from $RemindPath back to ingress-context..."
    foreach ($f in $ContextFiles) {
        if (-not $Force) { Test-DiffCheck "$RemindPath\.github\$f" "$ContextDir\$f" }
        Copy-Item -Recurse -Force "$RemindPath\.github\$f" "$ContextDir\"
    }
    Write-Host "Done. Don't forget to commit and push your changes!"
} else {
    Write-Host "Copying context files to $RemindPath"
    foreach ($f in $ContextFiles) {
        if (-not $Force) { Test-DiffCheck "$ContextDir\$f" "$RemindPath\.github\$f" }
        Copy-Item -Recurse -Force "$ContextDir\$f" "$RemindPath\.github\"
    }
    Write-Host "Done."
}