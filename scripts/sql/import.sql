# Import data into database.


SET foreign_key_checks = 0;
SET unique_checks= 0;
SET sql_log_bin=0;
SET bulk_insert_buffer_size = 4294967296; # Allocate 4 GB
SET myisam_sort_buffer_size = 1073741824; # Allocate 1 GB
SET sort_buffer_size = 4294967296; # Allocate 4 GB

LOCK TABLES `pubsArticle` WRITE, `pubsmarkerannot` WRITE, `hgnc` WRITE;
ALTER TABLE pubsArticle DISABLE KEYS;
ALTER TABLE pubsMarkerAnnot DISABLE KEYS;

LOAD DATA LOCAL INFILE 'import/pubsArticle.txt'
INTO TABLE pubsArticle
 FIELDS TERMINATED BY '\t'
  LINES TERMINATED BY '\n';

LOAD DATA LOCAL INFILE 'import/pubsMarkerAnnot_fixed.txt' 
INTO TABLE pubsMarkerAnnot
 FIELDS TERMINATED BY '\t' 
  LINES TERMINATED BY '\n';

LOAD DATA LOCAL INFILE 'import/hgnc_fixed.txt' 
INTO TABLE `hgnc`
 FIELDS TERMINATED BY '\t'
  LINES TERMINATED BY '\n';

# Remove Markertype; Not needed.
ALTER TABLE `pubsmarkerannot` DROP `markerType`;


ALTER TABLE `pubsMarkerAnnot` MODIFY COLUMN `annot_id` INT(11) NOT NULL AUTO_INCREMENT FIRST;
ALTER TABLE pubsArticle ENABLE KEYS;
ALTER TABLE pubsMarkerAnnot ENABLE KEYS;
UNLOCK TABLES;


SET foreign_key_checks = 1;
SET unique_checks = 1;
SET sql_log_bin = 1;
