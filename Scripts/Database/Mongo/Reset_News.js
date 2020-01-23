//Get Collection
var collection = db.getCollection("FilteredNews");

//Reset Controlled Items
collection.find({is_controlled:true, is_incorrect:false}).forEach(
function (news) {
    news.is_controlled = false;
    collection.save(news);
});