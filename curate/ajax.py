from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax

@dajaxice_register
def init_form(request):
	dajax = Dajax()
	dajax.assin('.form','innerHTML','Hello')

	return dajax.json()