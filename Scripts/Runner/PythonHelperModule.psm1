# Functions
function Run-Python-Script {
    [CmdletBinding()]
    Param
    (
        [Parameter(Mandatory=$true, Position=0)]
        [string]$Path,

        [Parameter(Mandatory=$true, Position=0)]
        [string]$CondaEnv
    )

    # Change Location 
    Set-Location $ConfigPath

    # Change Environment
    conda activate $CondaEnvirment

    Write-Output "Running Script..."
    # Get Start Time Stamp
    $StartDate=(GET-DATE)
    # Run Python Script
    python main.py
    # Get End Time Stamp
    $EndDate=(GET-DATE)
    # Inform User
    Write-Output "Run Statistics:"
    NEW-TIMESPAN –Start $StartDate –End $EndDate
}