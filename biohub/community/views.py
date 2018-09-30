from django.http import HttpResponse
from rest_framework import decorators, viewsets, permissions
from rest_framework.response import Response

from biohub.editor.models import Report
from biohub.editor.serializers import ReportSerializer

from biohub.community.models import Star
from biohub.community.serializers import StarRequestSerializer


class StarViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # Route: GET /users/favorites/
    def list(self, request):
        user = request.user
        queryset = Report.objects.filter(star__starrer=user)
        return Response(ReportSerializer(queryset, many=True).data)

    # Route: POST /users/favorites/
    def create(self, request):
        user = request.user
        serializer = StarRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report_id = serializer.data['id']
        _, created = Star.objects.get_or_create(starrer=user, starred_report_id=report_id)
        if created:
            # TODO: should we notify the starree here?
            return HttpResponse('true', status=201)
        else:
            return HttpResponse('true', status=200)

    # Route: POST /users/favorites/unstar
    @decorators.list_route(methods=['post'])
    def unstar(self, request):
        user = request.user
        serializer = StarRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report_id = serializer.data['id']
        queryset = Star.objects.filter(starrer=user, starred_report_id=report_id)
        if queryset:
            for star in queryset:
                star.delete()
            return HttpResponse('true', status=202)
        else:
            return HttpResponse('true', status=200)
