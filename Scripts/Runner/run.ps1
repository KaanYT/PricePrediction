# Settings
[string]$CondaEnvirment = "MSThesis"
[string]$Location = "C:\Users\kaaneksen\MSThesis\"

# Internal Settings
[string]$DNNConfig = "Predictor\NewsDnnGeneral\config_w.json"
[string]$ConfigPath = -join("$Location", "$DNNConfig");

# Import Modules
Import-Module "JsonModule.psm1";
Import-Module "PythonHelperModule.psm1";

# Change Settings
Change-Network-Type -ConfigPath $ConfigPath -Value "News" -WikiMultiplyFactors 10 -TweetMultiplyFactors 10
Change-Embedded-Network -ConfigPath $ConfigPath -EmbNetPath "C:\Users\kaaneksen\" -EmbNetSize 300

# Change-Embedded-Network -ConfigPath $ConfigPath -EmbNetPath "C:\Users\kaaneksen\" -EmbNetSize 300 -WikiMultiplyFactors 10

# Run Script
Run-Python-Script -Path $Location -CondaEnv $CondaEnvirment
