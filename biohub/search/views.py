from django.shortcuts import render
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import viewsets, mixins, decorators
# Create your views here.


class SearchViewSet(APIView):

    def get(self):
        return 'test'
