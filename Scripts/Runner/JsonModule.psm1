<# 
    JSON Heper Modules
#>
function Change-Network-Type {
    [CmdletBinding()]
    Param
    (
        [Parameter(Mandatory=$true, Position=0)]
        [string]$ConfigPath,

        [Parameter(Mandatory=$true, Position=0)]
        [string]$Value

        [Parameter(Mandatory=$false, Position=0)]
        [int]$WikiMultiplyFactors

        [Parameter(Mandatory=$false, Position=0)]
        [int]$TweetMultiplyFactors
    )

    # Network Type
    $config = Get-Content $ConfigPath -raw | ConvertFrom-Json
    $config.options.network_type = $Value # News, Wiki, WikiAndTweet
    IF ($Value -eq  "News") {
        $config.options.network_type = $Value   
    }ELSEIF ($Value -eq  "Wiki") {
        $config.options.wiki.enabled = $true
        $config.options.wiki.multiply_factors = $WikiMultiplyFactors
    }ELSEIF ($Value -eq  "WikiAndTweet") {
        $config.options.wiki.enabled = $true
        $config.options.wiki.multiply_factors = $WikiMultiplyFactors
        $config.options.twitter.enabled = $true
        $config.options.twitter.multiply_factors = $TweetMultiplyFactors
    }ELSE{
        Write-Output "Network Type is not recognized"
    }

    $config | ConvertTo-Json -depth 32| set-content $ConfigPath
    Write-Output "Config network type is changed."
}

function Change-Embedded-Network {
    [CmdletBinding()]
    Param
    (
        [Parameter(Mandatory=$true, Position=0)]
        [string]$ConfigPath,

        [Parameter(Mandatory=$true, Position=0)]
        [string]$EmbNetPath

        [Parameter(Mandatory=$true, Position=0)]
        [int]$EmbNetSize
    )

    # Network Type
    $config = Get-Content $ConfigPath -raw | ConvertFrom-Json
    $config.wordEmbedding.path = $EmbNetPath
    $config.wordEmbedding.size = $EmbNetSize
    $config | ConvertTo-Json -depth 32| set-content $ConfigPath
    Write-Output "Config network type is changed."
}

function Change-Network-Settings {
    [CmdletBinding()]
    Param
    (
        [Parameter(Mandatory=$true, Position=0)]
        [string]$ConfigPath,

        [Parameter(Mandatory=$true, Position=0)]
        [string]$EmbNetPath

        [Parameter(Mandatory=$true, Position=0)]
        [int]$EmbNetSize
    )

    # Network Type
    $config = Get-Content $ConfigPath -raw | ConvertFrom-Json
    $config.wordEmbedding.path = $EmbNetPath
    $config.wordEmbedding.size = $EmbNetSize
    $config | ConvertTo-Json -depth 32| set-content $ConfigPath
    Write-Output "Config network type is changed."
}