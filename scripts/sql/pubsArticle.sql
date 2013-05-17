-- MySQL dump 10.11
--
-- Host: localhost    Database: hgFixed
-- ------------------------------------------------------
-- Server version	5.0.67

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `pubsArticle`
--

DROP TABLE IF EXISTS `pubsArticle`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `pubsArticle` (
  `articleId` bigint(20) NOT NULL,
  `extId` varchar(255) NOT NULL,
  `pmid` bigint(20) NOT NULL,
  `doi` varchar(255) NOT NULL,
  `source` varchar(255) NOT NULL,
  `citation` varchar(2000) default NULL,
  `year` int(11) NOT NULL,
  `title` varchar(6000) default NULL,
  `authors` varchar(12000) default NULL,
  `firstAuthor` varchar(255) default NULL,
  `abstract` varchar(32000) NOT NULL,
  `url` varchar(1000) default NULL,
  `dbs` varchar(500) default NULL,
  PRIMARY KEY  (`articleId`),
  KEY `extIdx` (`extId`),
  FULLTEXT KEY `citation` (`citation`,`title`,`authors`,`abstract`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2012-05-09  6:51:37
