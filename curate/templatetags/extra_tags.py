from django import template

register = template.Library()

@register.filter    
def subtract(value, arg):
	try:
		return int(value) - int(arg)
	except:
		return 0

register.filter('subtract',subtract)


@register.filter()
def highlight(value, word):
	try:
		replace = re.compile(re.escape(word), re.IGNORECASE)
		return  replace.sub("<span class='label label-info'>" + str(word) + "</span>", str(value))
	except:
		return value

register.filter('highlight',highlight)

@register.filter(is_safe=True)
def to_ul(value):
	 return "<ul><li>" + "</li><li>".join(value.split(",")) + "</li></ul>"

register.filter('to_ul',to_ul)
