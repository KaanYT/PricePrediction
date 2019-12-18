# Functions
function Run-Python-Script {
    [CmdletBinding()]
    Param
    (
        [Parameter(Mandatory=$true, Position=0)]
        [string]$ScriptPath,

        [Parameter(Mandatory=$true, Position=0)]
        [string]$CondaEnv
    )
    
    # Change Environment
    conda activate $CondaEnv
    Write-Output "Script is running..."
    # Get Start Time Stamp
    $StartDate=(GET-DATE)
    # Run Python Script
    python $ScriptPath\main.py
    # Get End Time Stamp
    $EndDate=(GET-DATE)
    Write-Output "Script is finished..."
    # Inform User
    Write-Output "Run Statistics:"
    NEW-TIMESPAN $StartDate $EndDate
}
