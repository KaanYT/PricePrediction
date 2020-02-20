# MScThesis
Master Thesis Application

## Database 
* Mongo DB
	* Mac OS
		* Install MongoDB `brew install mongodb-community@4.0` 
		* Start the Mongo daemon `brew services start mongodb`
		* Stop the Mongo daemon `brew services stop mongodb`
	* Windows
		* [Download the installer (.msi) ](https://www.mongodb.com/download-center/community?jmp=docs)
		* Double-click the .msi file.
		* [Install MongoDB Compass](https://www.mongodb.com/products/compass)
		* Run the Mongo daemon `"C:\Program Files\MongoDB\Server\4.0\bin\mongo.exe"`
			* As a Service Start `net start MongoDB`
			* As a Service Stop `net stop MongoDB`
			
## Data
* Resources
    * [OECD](https://data.oecd.org)
    * Twitter
    * Wikipedia  
			
## Requirements

### Software
* Package Manager: `Conda 4.6.11`
    * Environment Name : `MScThesis`
* Programming Language : `Python 3.6`
* Database : `MongoDB 4.x`
* IDEA (Recommended) : `IntelliJ - PyCharm`

### Package List
* Package list can accessed from MScThesis.yml
    * Create env. and install packages `conda env create -f MScThesis.yml`
    * Activate Env. `conda activate MScThesis`
    * Remove Env. `conda remove --name MScThesis --all`
* For More Information
    * pymongo
        * MongoDB Access
    * mongolog 
        * Centralized Logging 
    * keras
    * feedparser
    * configparser
    * newspaper3k
        *  Info 
            * Use [NLTK - Natural Language Toolkit](https://www.nltk.org/data.html)
            * Download Corpora ` curl https://raw.githubusercontent.com/codelucas/newspaper/master/download_corpora.py | python3`
            * Corpora List
                * brown - Required for FastNPExtractor
                * punkt - Required for WordTokenizer
                * maxent_treebank_pos_tagger - Required for NLTKTagger
                * movie_reviews - Required for NaiveBayesAnalyzer
                * wordnet - Required for lemmatization and Wordnet
                * stopwords
        * `brew install libxml2 libxslt`
        * `brew install libtiff libjpeg webp little-cms2`
        * `pip3 install newspaper3k` 
            * `conda install -c conda-forge newspaper3k`
            * `import nltk; nltk.download()`
     * `pip install transformers`

## Test Environment

* Test Dependency
    * Run `mnist_cnn.py`

### Helpers

1. MongoDB 
    * Python Examples : `https://github.com/janbodnar/pymongo-examples`
    * 
2. 