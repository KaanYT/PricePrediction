db.getCollection("HandpickedNews_Fix2").find({
    date: {
        $gte: ISODate("2013-04-29T00:00:00.000Z"),
        $lt: ISODate("2016-09-01T00:00:00.000Z")
    }
}).count();


