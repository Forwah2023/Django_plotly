from django.shortcuts import render
from django.views.generic import TemplateView
from . import sample
# Create your views here.


class HomeView(TemplateView):
	template_name = 'home.html'
    
class AboutView(TemplateView):
    template_name='about.html'