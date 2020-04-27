//Get Collection
var collection = db.getCollection("FilteredNewsGeneralNoTagES");

//Find Max Min
var result = collection.aggregate({
    $group : {
        _id: null,
        tweetMin: { $min : "$tweet_count" },
        tweetMax: { $max : "$tweet_count" }
    }
}).toArray();

// Normalize
collection.find({}).forEach(
function (elem) {
    elem.tweet_count_nor = ((elem.tweet_count - result[0].tweetMin)/(result[0].tweetMax-result[0].tweetMin));
    collection.save(elem);
});