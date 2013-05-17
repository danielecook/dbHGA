#!/bin/bash

## Thank you Stack Overflow
# This file will download the hg tables and set them up in a mysql database locally.


#####################################################
# Setup Tables from UCSC - Publication Information  #
#####################################################

# Makedir
mkdir data
mkdir sql
mkdir import 

## Set variable of URL where files can be downloaded from.
URL="http://hgdownload.cse.ucsc.edu/goldenPath/hgFixed/database" 

# Download databases
wget --timestamping --directory-prefix=sql "$URL/pubsArticle.sql"
wget --timestamping --directory-prefix=data "$URL/pubsArticle.txt.gz"
wget --timestamping --directory-prefix=sql "$URL/pubsMarkerAnnot.sql"
wget --timestamping --directory-prefix=data "$URL/pubsMarkerAnnot.txt.gz"

## Unzip the tables
gunzip -c "data/pubsArticle.txt.gz" > "import/pubsArticle.txt" -f
gunzip -c "data/pubsMarkerAnnot.txt.gz" > "data/pubsMarkerAnnot.txt" -f

## Exclude 'Gene' and 'Band' features.
grep "\tsnp\t" 'data/pubsMarkerAnnot.txt' > 'data/pubsMarkerAnnot_filtered.txt'

# Remove rs from the SNP column.
sed -e "s/rs\([0-9]\)/\1/1" 'data/pubsMarkerAnnot_filtered.txt' > "import/pubsMarkerAnnot_fixed.txt"

### DEBUG ###
#cat 'import/pubsMarkerAnnot_filtered.txt'  | head -n 5000 | tail -n 5000 > 'import/pubsmarkerannot_filteredx.txt'
#rm 'import/pubsmarkerannot_filtered.txt'
#mv 'import/pubsmarkerannot_filteredx.txt' 'import/pubsmarkerannot_filtered.txt'
#cat 'import/pubsArticle.txt'  | head -n 5000 | tail -n 5000 > 'import/pubsArticlex.txt'
#rm 'import/pubsArticle.txt'
#mv 'import/pubsArticlex.txt' 'import/pubsArticle.txt'

# Create the Database
mysql -u root -e "DROP DATABASE hg_pubs"
mysql -u root -e "CREATE DATABASE IF NOT EXISTS hg_pubs;"

# Load SQL 
mysql -u root -D hg_pubs < "sql/pubsArticle.sql"
mysql -u root -D hg_pubs < "sql/pubsMarkerAnnot.sql"

# Add indices
mysql -u root -D hg_pubs -e 'ALTER TABLE `pubsArticle` ADD INDEX `doi` (`doi`);'
mysql -u root -D hg_pubs -e 'ALTER TABLE `pubsmarkerannot` ADD annot_id INT PRIMARY KEY AUTO_INCREMENT;'

# Rename index of articleId
mysql -u root -D hg_pubs -e 'ALTER TABLE `pubsArticle` CHANGE `articleId` `id` BIGINT(20)  NOT NULL;'

# Speed up Import
myisamchk --key-buffer-size=4294967296

########################
# Setup HGNC Table     #
########################

# Download all of the genes.
wget --timestamping --directory-prefix=sql "http://www.genenames.org/cgi-bin/hgnc_downloads?title=HGNC+output+data&hgnc_dbtag=on&col=gd_hgnc_id&col=gd_app_sym&col=gd_app_name&col=gd_status&col=gd_locus_type&col=gd_prev_sym&col=gd_aliases&col=gd_pub_chrom_map&col=gd_pub_acc_ids&col=gd_pub_eg_id&col=gd_pub_refseq_ids&col=md_mim_id&col=md_refseq_id&col=md_ucsc_id&status=Approved&status=Entry+Withdrawn&status_opt=2&where=&order_by=gd_app_sym_sort&format=text&limit=&submit=submit&.cgifields=&.cgifields=chr&.cgifields=status&.cgifields=hgnc_dbtag" -O hgnc.txt

# Remove the HGNC: prefix
sed 's/HGNC://g' hgnc.txt > "import/hgnc_fixed.txt"

# Create HGNC Table
mysql -u root --local-infile=1 -D hg_pubs < "sql/hgnc.sql"


#!#!# Load tables into mysql database. 
mysql -u root --local-infile=1 -D hg_pubs < "sql/import.sql"
#!#!#

# Create Join Table
mysql -u root -D hg_pubs -e 'CREATE VIEW jpub AS (SELECT * FROM pubsArticle INNER JOIN pubsMarkerAnnot ON pubsArticle.Id = pubsMarkerAnnot.ArticleId);'


#####################################################
# Setup Tables from UCSC - Marker Counts            #
#####################################################

URL="http://hgdownload.cse.ucsc.edu/goldenPath/hg19/database/pubsMakerSnp"
wget --timestamping --directory-prefix=data "$URL/pubsMakerSnp" 



# Load tables into mysql database. 
mysql -u root --local-infile=1 -D hg_pubs < "load_tables.sql"
