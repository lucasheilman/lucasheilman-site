from django.shortcuts import get_object_or_404, render

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.template import loader

from .models import *

def index(request):
	context = {}
	index_page = page.objects.get(page_name = "index")
	context['index'] = index_page
	context['social_medias'] = list(index_page.social_medias.all().order_by('order'))
	return render(request, 'website/index.html', context)
