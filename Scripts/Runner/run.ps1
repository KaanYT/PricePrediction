# Settings
[string]$CondaEnvirment = "MScThesis"
[string]$Location = "C:\Users\eksen\Documents\GitHub\MScThesis"
[string]$WordEmbGoogle = "I:\Glove\GoogleNews-vectors-negative300.bin"
[string]$WordEmbGoogleSize = 300
[string]$WordEmbGlove = "I:\Glove\glove.6B.100d.w2v.txt"
[string]$WordEmbGloveSize = 100

# Internal Settings
[string]$DNNConfig = "Predictor\NewsDnnGeneral\config_w.json"
[string]$ConfigPath = Join-Path $Location $DNNConfig -Resolve
[string[]]$BussinesCategories = @(
    "Business"
    "Politics"
    "Economics"
    "Money"
    "Economy"
)

# Import Modules
Import-Module $PSScriptRoot\"JsonModule.psm1";
Import-Module $PSScriptRoot\"PythonHelperModule.psm1";
Import-Module $PSScriptRoot\"ShoutdownModule.psm1";

# Change Settings
<#  Example
    Change-Network-Type -ConfigPath $ConfigPath -Value "News" -WikiMultiplyFactors 10 -TweetMultiplyFactors 10 -TweetColumn "tweet_percentage" #News ,Wiki, WikiAndTweet
    Change-WordEmbedding-Settings -ConfigPath $ConfigPath -EmbNetPath $WordEmbGoogle -EmbNetSize $WordEmbGoogleSize
    Change-Network-Settings -ConfigPath $ConfigPath -Epochs 100 -BatchSize 100 -SequenceLength 100 -Criterion "100" -Optimizer "100" -UseGPU $true
    Change-Database -ScriptPath $ConfigPath -DatabaseName "FilteredNewsGeneral" -Category $BussinesCategories
#>

#First Test
Change-WordEmbedding-Settings -ConfigPath $ConfigPath -EmbNetPath $WordEmbGoogle -EmbNetSize $WordEmbGoogleSize
Change-Network-Type -ConfigPath $ConfigPath -Value "WikiAndTweet" -WikiMultiplyFactors 30 -TweetMultiplyFactors 30 -TweetColumn "tweet_percentage" #News ,Wiki, WikiAndTweet
Change-Network-Settings -ConfigPath $ConfigPath -Epochs 5 -BatchSize 20 -SequenceLength 200 -Criterion "NLLLoss" -Optimizer "Adam" -UseGPU $false
Change-Database -ConfigPath $ConfigPath -DatabaseName "FilteredNewsGeneralNoTag" -Category $BussinesCategories
Run-Python-Script -ScriptPath $Location -CondaEnv $CondaEnvirment

