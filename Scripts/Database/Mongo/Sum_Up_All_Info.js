Date.prototype.addHours = function(hours) {
  this.setTime(this.getTime() + (hours*60*60*1000));
  return this;
};

function addMonthsToDates(date, month){
    let newDate = new Date(date.getTime());
    newDate.setMonth(newDate.getMonth() + month);
    return newDate;
}

function getCollection(toCollectionName){
    if (!db.getCollectionNames().indexOf(toCollectionName) > -1) {
        db.createCollection(toCollectionName, null);
        db.getCollection(toCollectionName).createIndex({"Date" : -1},{"name" : "Index_Date"});
    }
    return db.getCollection(toCollectionName);
}

function getEconomicalIndicator(collection, date){
    return db.getCollection("EconomicalIndicator").find({
        date: {
            $gt: ISODate(addMonthsToDates(date,-1).toISOString()),
            $lte: ISODate(date.toISOString())
        },
        country_code : "USA"
    })
}

function getCurrency(collection, date){
    let endDate = new Date(date.getTime());
    endDate.addHours(-1);
    return collection.find({
        Date: {
            $gt: ISODate(endDate.toISOString()),
            $lte: ISODate(date.toISOString())
        }
    })
}

function getIndex(collection, date){
    let endDate = new Date(date.getTime());
    endDate.addHours(-1);
    return collection.find({
        Date: {
            $gt: ISODate(endDate.toISOString()),
            $lte: ISODate(date.toISOString())
        }
    })
}

//Get Destination Collection
var toCollection = getCollection("Summary");

//Get Product Collection
let collection = db.getCollection("Product");
let productFilter = {"Key" : "BRTUSD"};

//Get Economical Indicator Collection
var infoCollection = db.getCollection("EconomicalIndicator");

//Get Currency Collection
var infoCurrency = db.getCollection("Currency");

//Get Index Collection
var infoIndex = db.getCollection("Index");

//Reset Controlled Items
collection.find(productFilter).forEach(function (news) {
    let eidata= {};
    let cdata= {};
    let idata= {};
    getEconomicalIndicator(infoCollection,news.Date).forEach(function (ei) {
        eidata[ei.title] = ei.value
    });

    getCurrency(infoCurrency, news.Date).forEach(function (ei) {
        cdata[ei.Key] = parseFloat(ei.Open)
    });
    
    getIndex(infoIndex, news.Date).forEach(function (ei) {
        idata[ei.Key] = parseFloat(ei.Open)
    });

    let doc = {};
    doc._id = news._id;
    doc.Open = Number(news.Open); // parseFloat, parseInt, Number
    doc.High = Number(news.High);
    doc.Low = Number(news.Low);
    doc.Close = Number(news.Close);
    doc.Date = news.Date;
    doc.EI = eidata;
    doc.Cur = cdata;
    doc.Inx = idata;
    toCollection.save(doc);
});