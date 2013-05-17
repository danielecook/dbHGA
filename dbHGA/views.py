from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth import logout, login, authenticate
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import urllib
import re
from curate.models import *
from dbHGA.functions import *
from operator import itemgetter
import csv as csv_w
from django.views.decorators.cache import cache_page

def home(request):

	snp_snippets_c = pubsanno.objects.count()


	snp = pubsanno.objects.all().values_list('markerid')[0:200]
	x = get_snp(snp)

	#pubsanno_c = pubsanno.objects.all().count()

	# Stats of years - for later.
	#years = pubs.objects.values('year').distinct().annotate(Count('year'))

	return render_to_response('home.txt',locals(),context_instance=RequestContext(request))


def static(request,template):
	return render_to_response(template,locals(),context_instance=RequestContext(request))

@cache_page(60 * 60 * 24)
def gene(request,gene,csv):
	# Download SNP info:
	try:
		# Find Gene by previous name, withdrawn, etc.
		r = hgnc.objects.filter(Q(approved_symbol=gene) | 
								Q(approved_symbol=gene+"~withdrawn") |
								Q(previous_symbols__icontains=gene) |
								Q(synonyms__icontains=gene)).order_by('status')

		# Query annotation database to see how many publications gene appears in:
		for i in r:
			i.count = pubsanno.objects.filter(markerid=i.approved_symbol).count()
			# Download SNPs for gene if not done so already.
			
			i.snps = snp_gene.objects.filter(entrez_gene_id=i.entrez_gene_id)
			get_snp(list(i.snps.values_list('rs',flat=True))) # Convert snps to flat list of values.

			# Branch here so snps/gene are only downloaded once.
			i.snps = snp_ref.objects.filter(gene_id=i.hgnc_id).values()
			# Get counts within Snp Annotation.
			
			# Generate list of SNPs
			gene_snp_list = list(i.snps.values_list('rs',flat=True))
			gene_snp_list = ["rs" + str(j) for j in gene_snp_list] # Add rs for querying marker annotation database.

			# Get count of number of different pubs snp appears in:
			counts = get_counts(gene_snp_list)
			
			for j in i.snps:
				try:
					j['pub_count'] = counts[j['rs']]
				except:
					j['pub_count'] = 0
			i.snps = sorted(i.snps, key=itemgetter('pub_count','chrom_position'), reverse=True)


	except ObjectDoesNotExist:
		message = "Not Found"

	### CSV Export Option
	if csv is not None:
		response = HttpResponse(mimetype='text/csv')
		if r.count()>1:
			file_name = "gene_set"
		else:
			file_name = str(i.approved_symbol)
			response['Content-Disposition'] = 'attachment; filename="%s.csv"' % file_name
		writer = csv_w.writer(response)
		writer.writerow(['Gene','SNP', 'CHR:POS', 'Build', 'Pubs'])
		for genes in r:
			for snp in genes.snps:
				if snp['pub_count'] > 0:
					writer.writerow([genes.approved_symbol,"rs" + snp['rs'],snp['chromosome'] + ":" + str(snp['position']),str(snp['build']),str(snp['pub_count'])])
		return response
	else:
		response = None

	return render_to_response('gene.txt',locals(),context_instance=RequestContext(request))

def parse_snp_data(data):
	cleaned_data = [(str(k).split("_"),str(v)) for k,v in data.iterlists() if k != "csrfmiddlewaretoken"]
	keys = [i for i in cleaned_data if i[0][0] == "attr" and len(i[0]) == 4]
	values = [i for i,o in cleaned_data if i[0][0] == "val" and len(i[0]) == 4]
	for i in keys:
		valuables = zip("attr_" + "_".join(data[1:]),"val_" + "_".join(data[1:]))

	for k,v in data.iterlists():
		if k == "csrfmiddlewaretoken":
			break
		vals = {}
		k = k.split("_")
		bin = k[0]
		if (bin=="attr" and k.len == 3):
			vals.append(v)
		elif (bin=="val"):
				zip_vals = zip["attr" + data[v[1:3]],v]
				vals[str(k[3])] = zip_vals
		else:
			pass
		ent = k[1] # snp
		ent_set = k[2] # Entity Set

	return vals

