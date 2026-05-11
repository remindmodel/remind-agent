param(
    [string]$RemindPath = (Get-Location).Path,
    [string]$RepoUrl = $(if ($env:REMIND_CONTEXT_URL) { $env:REMIND_CONTEXT_URL } else { 'https://github.com/tonnrueter/remind-context.git' })
)

# Bootstrap remind-context inside a REMIND checkout.
#
# remind-context is cloned as a plain (untracked) subdirectory of REMIND:
#
#   <remind>/remind-context/   <- this repo
#   <remind>/AGENT.md          <- pointer: @remind-context/AGENT.md
#   <remind>/.github/
#       copilot-instructions.md <- pointer: @../remind-context/AGENT.md
#
# Run once per REMIND checkout. To update: git -C remind-context pull

$ErrorActionPreference = 'Stop'

if (-not (Test-Path "$RemindPath\.git")) {
    Write-Error "'$RemindPath' is not a git repository."
    exit 1
}

Push-Location $RemindPath
try {
    if (-not (Test-Path 'remind-context\.git')) {
        Write-Host "Cloning remind-context from $RepoUrl ..."
        git clone $RepoUrl remind-context
    }
    else {
        Write-Host 'remind-context already present - pulling ...'
        git -C remind-context pull
    }

    # Keep remind-context/ out of git status without touching committed .gitignore
    $exclude = '.git\info\exclude'
    if (-not (Select-String -Path $exclude -Pattern 'remind-context/' -Quiet)) {
        Add-Content -Path $exclude -Value 'remind-context/'
    }

    if (-not (Test-Path '.github')) { New-Item -ItemType Directory -Path '.github' | Out-Null }

    if (-not (Test-Path 'AGENT.md')) {
        Set-Content -Path 'AGENT.md' -Value '@remind-context/AGENT.md' -NoNewline
        Write-Host 'Wrote AGENT.md'
    }

    if (-not (Test-Path '.github\copilot-instructions.md')) {
        Set-Content -Path '.github\copilot-instructions.md' -Value '@../remind-context/AGENT.md' -NoNewline
        Write-Host 'Wrote .github\copilot-instructions.md'
    }

    Write-Host ''
    Write-Host 'Done.'
    Write-Host ''
    Write-Host 'Next steps:'
    Write-Host '  - Pull updates later:  git -C remind-context pull'
    Write-Host '  - Repeat bootstrap for each REMIND checkout you use.'
    Write-Host '  - Do NOT commit remind-context, AGENT.md, or'
    Write-Host '    .github/copilot-instructions.md to REMIND.'
}
finally {
    Pop-Location
}
