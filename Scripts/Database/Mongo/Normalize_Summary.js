//Get Collection
var collection = db.getCollection("Summary");

function getCollection(toCollectionName){
    if (!db.getCollectionNames().indexOf(toCollectionName) > -1) {
        db.createCollection(toCollectionName, null);
    }
    return db.getCollection(toCollectionName);
}

//Get Collection
var collection2 = getCollection("SummaryLast");

//Find Max Min
var result = collection.aggregate({
    $group : {
        _id: null,
        GBPUSDMin: { $min : "$Cur.GBPUSD" },
        GBPUSDMax: { $max : "$Cur.GBPUSD" },
        DJIMin: { $min : "$Inx.DJI" },
        DJIMax: { $max : "$Inx.DJI" },
        HSIMin: { $min : "$Inx.HSI" },
        HSIMax: { $max : "$Inx.HSI" }
    }
}).toArray();

// Normalize
collection.find().forEach(
function (elem) {
    if (typeof elem.Cur.GBPUSD != "undefined") {
        elem.Cur.GBPUSD = ((elem.Cur.GBPUSD - result[0].GBPUSDMin)/(result[0].GBPUSDMax-result[0].GBPUSDMin))

    }
    if (typeof elem.Inx.DJI != "undefined") {
        elem.Inx.DJI = ((elem.Inx.DJI - result[0].DJIMin)/(result[0].DJIMax-result[0].DJIMin))
    }
    if (typeof elem.Inx.HSI != "undefined") {
        elem.Inx.HSI = ((elem.Inx.HSI - result[0].HSIMin)/(result[0].HSIMax-result[0].HSIMin))
    }
    collection2.save(elem);
});