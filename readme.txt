CREATE VIEW jpub AS (SELECT * FROM pubsArticle JOIN pubsMarkerAnnot ON pubsArticle.id = pubsMarkerAnnot.ArticleId);


# Inner Join or just join?
CREATE VIEW jpub AS (SELECT * FROM pubsArticle INNER JOIN pubsMarkerAnnot ON pubsArticle.Id = pubsMarkerAnnot.ArticleId);