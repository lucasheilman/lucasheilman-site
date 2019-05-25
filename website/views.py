from django.shortcuts import get_object_or_404, render

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.template import loader

import re
import datetime

from .models import *


def mobile(request):
	MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)

	if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
		return True
	else:
		return False

def index(request):
	context = {}
	index_page = page.objects.get(page_name = "index")
	context['index'] = index_page
	context['social_medias'] = list(index_page.social_medias.all().order_by('order'))
	context['is_mobile'] = mobile(request)
	context['year'] = datetime.datetime.today().year
	return render(request, 'website/index.html', context)
