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
        [string]$Value,

        [Parameter(Mandatory=$true, Position=0)]
        [int]$WikiMultiplyFactors,

        [Parameter(Mandatory=$true, Position=0)]
        [int]$TweetMultiplyFactors,

        [Parameter(Mandatory=$false, Position=0)]
        [string]$TweetColumn
    )

    # Network Type
    $config = Get-Content $ConfigPath -raw | ConvertFrom-Json
    $config.options.network_type = $Value # News, Wiki, WikiAndTweet
    IF ($Value -eq "News") {
        $config.options.wiki.enabled = $false
        $config.options.twitter.enabled = $false
    }ELSEIF ($Value -eq "Wiki") {
        $config.options.wiki.enabled = $true
        $config.options.twitter.enabled = $false
        $config.options.wiki.multiply_factors = $WikiMultiplyFactors
    }ELSEIF ($Value -eq "WikiAndTweet") {
        $config.options.wiki.enabled = $true
        $config.options.twitter.enabled = $true
        $config.options.wiki.multiply_factors = $WikiMultiplyFactors
        $config.options.twitter.multiply_factors = $TweetMultiplyFactors
    }ELSE{
        Write-Output "Network Type is not recognized"
    }

    IF ($PSBoundParameters.ContainsKey('TweetColumn')) {
        $config.options.twitter.tweet_column = $TweetColumn
    }

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
        [int]$Epochs,

        [Parameter(Mandatory=$true, Position=0)]
        [int]$BatchSize,

        [Parameter(Mandatory=$true, Position=0)]
        [int]$SequenceLength,

        [Parameter(Mandatory=$false, Position=0)]
        [string]$Criterion,

        [Parameter(Mandatory=$false, Position=0)]
        [int]$HiddenSize,

        [Parameter(Mandatory=$false, Position=0)]
        [string]$Optimizer,

        [Parameter(Mandatory=$false, Position=0)]
        [bool]$UseGPU
    )

    # Network Type
    $config = Get-Content $ConfigPath -raw | ConvertFrom-Json
    $config.networkConfig.epochs = $Epochs
    $config.networkConfig.batch_size = $BatchSize
    $config.networkConfig.sequence_length = $SequenceLength
    IF ($PSBoundParameters.ContainsKey('Criterion')) {
        $config.networkConfig.criterion = $Criterion
    }
    IF ($PSBoundParameters.ContainsKey('Optimizer')) {
        $config.networkConfig.optimizer = $Optimizer
    }
    IF ($PSBoundParameters.ContainsKey('HiddenSize')) {
        $config.networkConfig.hidden_size = $HiddenSize
    }
    IF ($PSBoundParameters.ContainsKey('UseGPU')) {
        $config.networkConfig.useGPU = $UseGPU
    }
    $config | ConvertTo-Json -depth 32| set-content $ConfigPath
    Write-Output "Config network settings is changed."
}

function Change-WordEmbedding-Settings {
    [CmdletBinding()]
    Param
    (
        [Parameter(Mandatory=$true, Position=0)]
        [string]$ConfigPath,

        [Parameter(Mandatory=$true, Position=0)]
        [string]$EmbNetPath,

        [Parameter(Mandatory=$true, Position=0)]
        [int]$EmbNetSize
    )

    # Network Type
    $config = Get-Content $ConfigPath -raw | ConvertFrom-Json
    $config.wordEmbedding.path = $EmbNetPath
    $config.wordEmbedding.size = $EmbNetSize
    $config | ConvertTo-Json -depth 32| set-content $ConfigPath
    Write-Output "Config word embedding is changed."
}

function Change-Database {
    [CmdletBinding()]
    Param
    (
        [Parameter(Mandatory=$true, Position=0)]
        [string]$ConfigPath,

        [Parameter(Mandatory=$true, Position=0)]
        [string]$DatabaseName,

        [Parameter(Mandatory=$false, Position=0)]
        [string[]]$Category
    )

    # Load JSON
    $config = Get-Content $ConfigPath -raw | ConvertFrom-Json
    $config.database.name = $DatabaseName
    # Remove Category
    IF ( -not ( $config.database.train.query.category -eq $Null ) ) {
        $config.database.train.query = $config.database.train.query | Select-Object * -ExcludeProperty category
        $config.database.validate.query = $config.database.validate.query | Select-Object * -ExcludeProperty category
        $config.database.test.query = $config.database.test.query | Select-Object * -ExcludeProperty category
    }
    IF ($PSBoundParameters.ContainsKey('Category')) {
        $categoryField = @"
        {
          "`$in": [
          ]
        }
"@
        $config.database.train.query | add-member -Name "category" -value (Convertfrom-Json $categoryField) -MemberType NoteProperty
        $config.database.train.query.category.'$in' += $Category
        $config.database.validate.query | add-member -Name "category" -value (Convertfrom-Json $categoryField) -MemberType NoteProperty
        $config.database.validate.query.category.'$in' += $Category
        $config.database.test.query | add-member -Name "category" -value (Convertfrom-Json $categoryField) -MemberType NoteProperty
        $config.database.test.query.category.'$in' += $Category
    }
    $config | ConvertTo-Json -depth 32| set-content $ConfigPath
    Write-Output "Config Database is changed."
}

function Change-Price-Settings {
    [CmdletBinding()]
    Param
    (
        [Parameter(Mandatory=$true, Position=0)]
        [string]$ConfigPath,

        [Parameter(Mandatory=$false, Position=0)]
        [string]$Start,

        [Parameter(Mandatory=$false, Position=0)]
        [string]$End,

        [Parameter(Mandatory=$true, Position=0)]
        [double]$BufferPercent
    )

    # Network Type
    $config = Get-Content $ConfigPath -raw | ConvertFrom-Json

    IF ($PSBoundParameters.ContainsKey('Start')) {
        $config.database.price.start = $Start
    }

    IF ($PSBoundParameters.ContainsKey('End')) {
        $config.database.price.end = $End
    }
    $config.database.price.buffer_percent = $BufferPercent
    $config | ConvertTo-Json -depth 32| set-content $ConfigPath
    Write-Output "Config price is changed."
}