//Get Collection
var collection = db.getCollection("Product");
//Get Destination Collection
var toCollection = db.getCollection("NewProduct");

//Reset Controlled Items
collection.find().forEach(
function (news) {
    news.Open = parseFloat(news.Open); // parseFloat, parseInt, Number, NumberDecimal
    news.High = parseFloat(news.High);
    news.Low = parseFloat(news.Low);
    news.Close = parseFloat(news.Close);
    toCollection.save(news);
});