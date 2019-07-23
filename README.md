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
			
## Requirements

### Software
* Package Manager: `Conda 4.6.11`
    * Environment Name : `MScThesis`
* Programming Language : `Python 3.6`
* Database : `MongoDB 4.x`
* IDEA : `IntelliJ - PyCharm`

### Package List
* pymongo
* keras

## Test Environment

* Test Dependency
    * Run `mnist_cnn.py`
