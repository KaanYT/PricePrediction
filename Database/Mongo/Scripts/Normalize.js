//Get Collection
var collection = db.getCollection("FilteredNewsGeneral");

//Find Max Min
var result = collection.aggregate({
    $group : {
        _id: null,
        wikiMin: { $min : "$wiki_relatedness" },
        wikiMax: { $max : "$wiki_relatedness" },
        tweetMin: { $min : "$tweet_percentage" },
        tweetMax: { $max : "$tweet_percentage" }
    }
}).toArray();

//Infinity Control
if (result[0].wikiMax == Infinity){
    var max = collection.find({"wiki_relatedness" : { $lt: 10 } }, { wiki_relatedness: 1, _id: 0 }).sort({"wiki_relatedness":-1}).limit(1).toArray()[0]
    result[0].wikiMax = max.wiki_relatedness + 0.000000000000001;
}

// Normalize
collection.find({}).forEach(
function (elem) {
    if (elem.wiki_relatedness == Infinity){
        elem.wiki_relatedness = result[0].wikiMax;
    }
    elem.wiki_relatedness = ((elem.wiki_relatedness - result[0].wikiMin)/(result[0].wikiMax-result[0].wikiMin))
    collection.save(elem);
});