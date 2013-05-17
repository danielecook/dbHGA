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

#@cache_page(60 * 60 * 24)
def search(request, search_term):
	if request.method == 'POST':
		# Redirect user to /search/(search term)/ Nice and clean :-)
		return redirect('/search/' + request.POST['q'])
	elif (search_term==""):
		# Send 'em' packing. Have to use a search term.
		return redirect('/')
	else:
		Title = "Search Results : %s" % search_term # Sets title of page itself.

		# Determine the type of query:
		if re.match('rs([0-9]+)',search_term):
			search_type = "SNP"
			snpinfo = get_snp(search_term)
			r = pubsanno.objects.filter(markerid=search_term).values('articleid','markerid','articleid__pmid','articleid__extid','articleid__year','articleid__title','articleid__doi').annotate(c=Count('articleid')).order_by('-c','articleid__title','articleid__pmid')
			for i in r:
				if (i['articleid__pmid'] == 0):
					i['articleid__pmid'] = doi_to_pmid(i['articleid__doi'])
			try:
				num_results = get_counts([search_term])[search_term.replace('rs','')]
			except:
				num_results = 0

		elif re.match('[0-9]+',search_term):
			# Redirect for PMID query
			try:
				r = pubs.objects.get(pmid=search_term)
				return redirect('/pub/' + search_term)
			except ObjectDoesNotExist:
				message = "Not Found"
				search_type = "PMID"
				num_results = 0
				r = None
		elif re.match('PMC[0-9]+',search_term):
			# Redirect for PMC query
			search_type = "PMC"
			try:
				r = pubs.objects.get(extid=search_term)
				return redirect('/pub/' + search_term)
			except ObjectDoesNotExist:
				message = "Not Found"
				search_type = "PMC ID"
				num_results = 0
				r = None
		elif re.match('[A-Z]+[0-9A-Z]{2}[A-Z]*[0-9]{0,3}',search_term):
			# If Gene - Redirect to gene page.
			try:
				q = hgnc.objects.filter(Q(approved_symbol=search_term) | 
										Q(approved_symbol=search_term+"~withdrawn") |
										Q(previous_symbols__icontains=search_term) |
										Q(synonyms__icontains=search_term))
				if len(q) >= 1:
					return redirect('/gene/' + search_term )
				else:
					num_results = 0
					r = None
			except ObjectDoesNotExist:
				num_results = 0
				r = None
			search_type = "Gene"

		else:
			# Most intensive form of search.
			r = pubs.objects.filter(Q(title__icontains=search_term) |
									Q(authors__icontains=search_term) |
									Q(abstract__icontains=search_term)).values('articleid','title','authors')
			search_type = "text"
			num_results = len(r)
		
	if (num_results != 1):
		plural = "s"
	else:
		plural = ""

	if (num_results > 0):
		alert_info = "alert-success"
	else:
		alert_info = "alert-error"

	if r is not None:
		paginator = Paginator(r,50)
		page = request.GET.get('page')
		try:
			r = paginator.page(page)
		except PageNotAnInteger:
			r = paginator.page(1)
		except EmptyPage:
			r = paginator.page(paginator.num_pages)

	message = "Your search for <strong>%s</strong> [%s] returned %s result%s" % (search_term,search_type,num_results,plural)
	return render_to_response('search.txt',locals(),context_instance=RequestContext(request))




def view_pub(request, id):
	if request.method == 'POST':
		v = request.POST.lists()
		#l = parse_snp_data(request.POST)

	# See if link refers to article as Pubmed central.
	if (id[0:3] == "PMC"):
		publication = pubs.objects.get(extid=id)
	else:
		# In some cases - a publication will contain multiple records, so pull both and take the first.
		try:
			publication = pubs.objects.get(pmid=id)
		except:
			publication = pubs.objects.filter(pmid=id)[0]

	# Determine SNPs
	snp_set = pubsanno.objects.filter(articleid=publication.articleid).order_by('markerid').select_related().values()
	

	# Reformat snippets to make them more obvious.
	for i in snp_set:
		i['snippet'] = i['snippet'].replace("<B>","<span class='label label-info'>").replace("</B>","</span>")
		

	u_snp=[]
	if len(snp_set) > 0:
		for snps in snp_set:
			u_snp.append(snps['markerid'].replace('rs',''))
		u_snp  = set(u_snp)
		snp_info = get_snp(u_snp) # Get SNP gene info.
		# Map snp_info to snp_set.
		for snp in snp_set:
			try:
				snp['gene'] = snp_info[snp['markerid'].replace('rs','')]
			except:
				# Add dummy gene variable.
				snp['gene'] = {}
				snp['gene']['gene'] = {}
				snp['gene']['gene']['approved_symbol'] = "-"

	### FORMS
	template_form = """'<tr>
						<td colspan="2">
							<strong>Select Template</strong>
						</td>
							<td td colspan="2">
								<select>
									<option value="odds ratio">Odds Ratio</option>
								</select>
							</td>
						</tr>
						<tr class=' + snp_id + '>
							<td colspan="2">

							</td>
						<td colspan="2">
							<strong>Attribute</strong> <strong>Value</strong>
						</td>
						</tr>
						'""".replace('\n','')
	add_item = """'
				<li class="dd-item" data-id="1">
					<div class="dd-handle dd3-handle">Drag</div><div class="dd3-content"><input type="text" name="attr_' + snp_id +  '_' + rand + '" placeholder="Attribute" class="Attribute" /> <input type="text" class="value" name="val_' + snp_id +  '_' + rand + '" placeholder="Value" /><button type="button" class="btn btn-danger btn-small remove_item  pull-right"><i class="icon-remove"></i></button></div>
				</li>
	'""".replace("\n","").strip()

	add_form = """'
	<tr>
	<td><small>New Record</small></td>
	<td colspan="2">
		<div class="dd">
			<ol class="dd-list">
				<li class="dd-item" data-id="">
					<div class="dd-handle dd3-handle">Drag</div><div class="dd3-content"><input type="text" name="attr_' + snp_id +  '_' + rand + '" placeholder="Attribute" class="Attribute" /> <input type="text" placeholder="Value" class="value" name="val_' + snp_id +  '_' + rand + '" /><button type="button" class="btn btn-danger btn-small remove_item  pull-right"><i class="icon-remove"></i></button></div>
				</li>
			</ol>
		</div>
	   </td>
	   <td>
		<button class="btn add_item" type="button"><i class="icon-plus"></i></button>
	   </td>
	</tr>
'""".replace('\n','').strip()



	return render_to_response('pub.txt',locals(),context_instance=RequestContext(request))
