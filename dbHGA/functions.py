from django.core.exceptions import ObjectDoesNotExist
from curate.models import *
import urllib
import re
import Bio


def doi_to_pmid(doi):
	# Fetch PMID for a doi (document object identifer)
	url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=PubMed&retmode=xml&term=" + doi
	query = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")    
	result = urllib.urlopen(query).read() 

	m = re.search('<Id>([0-9]+)</Id>',result)
	if hasattr(m,'group'):

		# Update database - updates all instances (including duplicates) with doi.
		pubs.objects.filter(doi=doi).update(pmid=m.group(1))

		# Return pmid
		return m.group(1)
	else:
		return 0

def get_counts(snps):
	"""
		This function counts the number of different publications a snp appears in. There is
		some usage of joins/other techniques because of duplicates in the UCSC data.

	"""
	from django.db import connection, transaction
	cursor = connection.cursor()
	snps = "('" + "','".join(snps) + "')"
    # Data modifying operation - commit required
	query =  "SELECT DISTINCT pubsArticle.pmid, markerid, pubsArticle.doi, pubsArticle.extid FROM pubsMarkerAnnot, pubsArticle WHERE markerid IN %s AND (pubsMarkerAnnot.articleid = pubsArticle.articleId);" % (snps,)
	cursor.execute(query)
	d_list = []
	for ii,v,jj,kk in cursor.fetchall():
		d_list.append(v)
	d_set = set(d_list)
	d_tab = {}
	for i in d_set:
		# Remove rs for matching purposes and count list items.
		d_tab[str(i).replace('rs','')] = d_list.count(i)
	return d_tab

def get_snp(q):
	"""
		This function can be further optimized/made more efficient!
		Should also be moved elsewhere.
	"""
	# Download SNP Information.
	## For single string:
	if type(q) == unicode:
		try:
			# If snp already exists in database, return
			return snp_ref.objects.get(rs=q)
		except ObjectDoesNotExist:
			url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=snp&&rettype=docset&retmode=text&id=" + q
			query = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")    
			result = urllib.urlopen(query).read() 

			match = {}

			match_strings = {"rs":'SNP_ID=([0-9]+)',"build":'MODIFIED_BUILD_ID=([0-9]+)',"locus":'LOCUS_ID=([0-9]+)'}
			for k,v in match_strings.items():
				m = re.search(v,result)
				if m is not None:
					match[k] = m.group(1)


			# Chromosome, BP
			m = re.search('CHROMOSOME BASE POSITION=(.*)',result)
			if m is not None:
				m = m.group(1).split(':')
				chromosome = m[0]
				if (len(chromosome)==1 and str(chromosome) not in ['X','Y','MT']):
					chrom_position = "0" + m[0] + ":" + m[1].zfill(15)
				else:
					chrom_position = m[0] + ":" + m[1].zfill(15)
				position = m[1]

			if len(match) > 0:
				try:
					# Try to match on locus id first
					snp_obj = hgnc.objects.get(entrez_gene_id=match['locus'])
				except ObjectDoesNotExist:
					# Attempt to match on symbol
					gene = re.search('GENE=(.*)',result)
					if gene is not None:
						snp_obj = hgnc.objects.get(approved_symbol=gene.group(1).strip())
				except:
					return None
				snp = snp_ref(rs=match['rs'],gene=snp_obj,chromosome=chromosome,position=position,chrom_position=chrom_position,build=match['build'])
				snp.save()
				return snp
			else:
				return None
	else:
		# For arrays:
		fetch_set = []
		snp_set = {}

		q = [str(i) for i in q]
		snp_filter = snp_ref.objects.filter(rs__in=list(q))

		for i in snp_filter:
			snp_set[i.rs] = i

		fetch_set = set(q) - set(snp_set.keys())
		
		if (len(fetch_set) > 0):
			fetch_set = [str(i) for i in fetch_set]
			url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=snp&&rettype=docset&retmode=text&id=" + ",".join(fetch_set)
			query = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")    
			results = urllib.urlopen(query).read() 
			results = results.split('\n\n')
			for result in results:
				match = {}


				match_strings = {"rs":'SNP_ID=([0-9]+)',"build":'MODIFIED_BUILD_ID=([0-9]+)',"locus":'LOCUS_ID=([0-9]+)'}
				for k,v in match_strings.items():
					m = re.search(v,result)
					if m is not None:
						match[k] = m.group(1)


				# Chromosome, BP
				m = re.search('CHROMOSOME BASE POSITION=([0-9|X|Y|MT|M]{1,2}:[0-9]+)',result)
				if m is not None:
					m = m.group(1).split(':')
					chromosome = m[0]
					if (len(chromosome)==1 and str(chromosome) not in ['X','Y','MT']):
						chrom_position = "0" + m[0] + ":" + m[1].zfill(15)
					else:
						chrom_position = m[0] + ":" + m[1].zfill(15)
					position = m[1]


				if m is None:
					# When initially imported - the hgnc database imports the header row. It
					# is used here to reference snps not located in genes.
					# A little dirty - but it works.
					snp_obj = hgnc.objects.get(pk=0) 
				else:
					try:
						snp_obj = hgnc.objects.get(entrez_gene_id=match['locus'])
					except:
						# In some cases the locus is not represented.
						snp_obj = hgnc.objects.get(pk=0)

				if len(match) > 0:
					snp = snp_ref(rs=match['rs'],gene=snp_obj,chromosome=chromosome,position=position,chrom_position=chrom_position,build=match['build'])
					snp_set[snp.rs] = snp
					try:
						snp.save()
					except:
						pass	

	return snp_set