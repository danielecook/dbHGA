from django.db import models

# Create your models here.

class pubs(models.Model):
	articleid = models.BigIntegerField(primary_key=True, db_column='id') # Field name made lowercase.
	extid = models.CharField(max_length=765, db_column='extId') # Field name made lowercase.
	pmid = models.BigIntegerField()
	doi = models.CharField(max_length=765)
	source = models.CharField(max_length=765)
	citation = models.CharField(max_length=6000, blank=True)
	year = models.IntegerField()
	title = models.CharField(max_length=18000, blank=True)
	authors = models.CharField(max_length=36000, blank=True)
	firstauthor = models.CharField(max_length=765, db_column='firstAuthor', blank=True) # Field name made lowercase.
	abstract = models.CharField(max_length=96000)
	url = models.CharField(max_length=3000, blank=True)
	dbs = models.CharField(max_length=1500, blank=True)
	
	class Meta:
		db_table = u'pubsArticle'
		managed = False

	def __unicode__(self):
		return u'%s - %s' % (self.pmid, self.doi)

class pubsanno(models.Model):
	annot_id = models.IntegerField(primary_key=True)
	articleid = models.ForeignKey('pubs',db_column='articleId') # Field name made lowercase.
	fileid = models.IntegerField(db_column='fileId') # Field name made lowercase.
	annotid = models.IntegerField(db_column='annotId') # Field name made lowercase.
	filedesc = models.CharField(max_length=6000, db_column='fileDesc') # Field name made lowercase.
	markerid = models.CharField('snp_ref', max_length=20, db_column='markerId') # Field name made lowercase.
	section = models.CharField(max_length=33, blank=True)
	snippet = models.CharField(max_length=15000)
	
	class Meta:
		db_table = u'pubsMarkerAnnot'
		managed = False

	def __unicode__(self):
		return u'%s' % (self.markerid)


class hgnc(models.Model):
	# hgnc table of genes.
	hgnc_id = models.IntegerField(primary_key=True, db_column='HGNC ID') # Field renamed to remove spaces. Field name made lowercase.
	approved_symbol = models.CharField(max_length=33, blank=True)
	approved_name = models.CharField(max_length=150, blank=True)
	status = models.CharField(max_length=48, blank=True)
	locus_type = models.CharField(max_length=75, blank=True)
	previous_symbols = models.CharField(max_length=765, blank=True)
	synonyms = models.CharField(max_length=765, blank=True)
	chromosome = models.CharField(max_length=33, blank=True)
	accessionnumbers = models.CharField(max_length=33, blank=True)
	entrez_gene_id = models.IntegerField(null=True, blank=True, unique=True)
	refseq_id = models.CharField(max_length=33, blank=True)
	omim_id = models.IntegerField(null=True, blank=True)
	refseq = models.CharField(max_length=33, blank=True)
	ucsd_id = models.CharField(max_length=33, blank=True)
	class Meta:
		db_table = u'hgnc'


class snp_ref(models.Model):
	# Contains more information regarding SNPs.
	snp_id = models.AutoField(primary_key=True)
	rs = models.CharField(max_length=45,unique=True)
	gene = models.ForeignKey('hgnc')
	build = models.IntegerField(blank=True,null=True)
	chromosome = models.CharField(max_length = 2,blank=True)
	position = models.IntegerField(blank=True,null=True)
	chrom_position = models.CharField(max_length=45,blank=True,null=True) # For sorting purposes.



	class Meta:
		db_table = u'snp'

	def __unicode__(self):
		return u'rs%s' % (self.rs)
