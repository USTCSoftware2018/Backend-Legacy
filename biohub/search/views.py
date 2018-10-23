from django.shortcuts import render
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, mixins, decorators
# Create your views here.
from .engine import Engine
from .keyword import Keyword


@decorators.api_view(['GET', 'POST'])
def search(request):
    s = request.GET.get('s') or request.data.get('s')
    engine = Engine(s)
    result = engine.data()
    return Response(result)

@decorators.api_view(['GET', 'POST'])
def keywords(request):
    keyword = Keyword()
    data = {
        'keywords': keyword.get_keywords()
    }
    return Response(data)
