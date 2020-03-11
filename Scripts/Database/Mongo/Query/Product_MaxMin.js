db.getCollection("Product").find({
    Date: {
        $gte: ISODate("2014-01-01T00:00:00.000Z"),
        $lt: ISODate("2017-01-01T00:00:00.000Z")
    },
    Key : "BRTUSD",
}).sort({Low:-1}).limit(1);

