from urllib import request
from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone


class MarkersMapView(generic.base.TemplateView):
    template_name = "map.html"


def index(request):
    return HttpResponse(
        """This will be changed to a template for
                         the routerangers index webpage"""
    )
def home(request):
    context = {}
    return render(request, 'Cities.html')

def about(request):
    context = {}
    return render(request, 'about.html')

def Policy(request, context):
    context = {}
    return render(request, 'PolicyMaker_CHI.html', context)

def Survey(request, context):
    context = {}
    return render(request, 'Survey.html', context)

def Feedback(request, context):
    context = {}
    return render(request, 'Feedback.html', context)
