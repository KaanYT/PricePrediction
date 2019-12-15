//Get Collection
var collection = db.getCollection("FilteredNewsWikiAndTweetForDnn2");

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

// Normalize
collection.find({}).forEach(
function (elem) {
    elem.test = elem.wiki_relatedness * result[0].wikiMin
    collection.save(elem);
});