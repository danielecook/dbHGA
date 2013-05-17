DROP TABLE IF EXISTS `hgnc`;
CREATE TABLE `hgnc` (
  `HGNC ID` int(11) DEFAULT NULL,
  `approved_symbol` varchar(30) DEFAULT NULL,
  `approved_name` varchar(75) DEFAULT NULL,
  `status` enum('Entry Withdrawn','Approved','Symbol Withdrawn') DEFAULT NULL,
  `locus_type` varchar(25) DEFAULT NULL,
  `previous_symbols` varchar(255) DEFAULT NULL,
  `synonyms` varchar(255) DEFAULT NULL,
  `chromosome` varchar(11) DEFAULT NULL,
  `accessionnumbers` varchar(11) DEFAULT NULL,
  `entrez_gene_id` int(11) DEFAULT NULL,
  `refseq_id` varchar(11) DEFAULT NULL,
  `omim_id` int(11) DEFAULT NULL,
  `refseq` varchar(11) DEFAULT NULL,
  `ucsd_id` varchar(11) DEFAULT NULL,
  PRIMARY KEY (`HGNC ID`),
  KEY `approved_symbol` (`approved_symbol`),
  KEY `previous_symbols` (`previous_symbols`),
  KEY `synonyms` (`synonyms`),
  KEY `entez_gene_id` (`entrez_gene_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
