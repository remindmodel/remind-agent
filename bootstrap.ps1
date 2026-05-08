param(
    [string]$RemindPath = (Get-Location).Path,
    [string]$RepoUrl = $(if ($env:REMIND_CONTEXT_URL) { $env:REMIND_CONTEXT_URL } else { "https://github.com/tonnrueter/remind-context.git" })
)

# Bootstrap remind-context inside a REMIND checkout.
#
# - Adds remind-context as a git submodule at <remind>/remind-context
# - Writes two pointer files so Copilot and Claude Code pick up the context:
#     <remind>\AGENT.md                          -> @remind-context/AGENT.md
#     <remind>\.github\copilot-instructions.md   -> @../remind-context/AGENT.md
#
# The submodule, .gitmodules, and the pointer files are intentionally NOT
# committed to REMIND.

$ErrorActionPreference = "Stop"

if (-not (Test-Path "$RemindPath\.git")) {
    Write-Error "'$RemindPath' is not a git repository."
    exit 1
}

Push-Location $RemindPath
try {
    if (-not (Test-Path "remind-context\.git")) {
        Write-Host "Adding remind-context submodule from $RepoUrl ..."
        git submodule add $RepoUrl remind-context
        git submodule update --init --recursive
    } else {
        Write-Host "remind-context submodule already present — updating ..."
        git submodule update --init --recursive --remote remind-context
    }

    if (-not (Test-Path ".github")) { New-Item -ItemType Directory -Path ".github" | Out-Null }

    if (-not (Test-Path "AGENT.md")) {
        Set-Content -Path "AGENT.md" -Value "@remind-context/AGENT.md" -NoNewline
        Write-Host "Wrote AGENT.md"
    }

    if (-not (Test-Path ".github\copilot-instructions.md")) {
        Set-Content -Path ".github\copilot-instructions.md" -Value "@../remind-context/AGENT.md" -NoNewline
        Write-Host "Wrote .github\copilot-instructions.md"
    }

    Write-Host ""
    Write-Host "Done."
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  - Pull updates later:  git submodule update --remote remind-context"
    Write-Host "  - Edit context:        cd remind-context; git checkout main; ..."
    Write-Host "  - Do NOT commit remind-context/, .gitmodules, AGENT.md, or"
    Write-Host "    .github\copilot-instructions.md to REMIND."
}
finally {
    Pop-Location
}
