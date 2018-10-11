from django.http import HttpResponse
from django.db.models import F
from rest_framework import decorators, viewsets, permissions, generics, pagination, mixins
from rest_framework.response import Response

from biohub.accounts.models import User

from biohub.editor.models import Report
from biohub.editor.serializers import ReportInfoSerializer, UserInfoSerializer

from biohub.community.models import Star, Collection
from biohub.community.serializers import StarRequestSerializer, CollectRequestSerializer
from biohub.community.serializers import CollectionSerializer


class StarViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # Route: GET /users/favorites/
    def list(self, request):
        user = request.user
        queryset = Report.objects.filter(star__starrer=user)
        return Response(ReportInfoSerializer(queryset, many=True).data)

    # Route: POST /users/favorites/
    def create(self, request):
        user = request.user
        serializer = StarRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report_id = serializer.data['id']
        Star.objects.get_or_create(starrer=user, starred_report_id=report_id)
        return HttpResponse('true', status=200)

    # Route: POST /users/favorites/unstar/
    @decorators.list_route(methods=['post'])
    def unstar(self, request):
        user = request.user
        serializer = StarRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report_id = serializer.data['id']
        queryset = Star.objects.filter(starrer=user, starred_report_id=report_id)
        if queryset:
            queryset.delete()
        return HttpResponse('true', status=200)


class CollectionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CollectionSerializer

    def get_queryset(self):
        user = self.request.user
        return Collection.objects.filter(collector=user)


@decorators.api_view(['post'])
@decorators.permission_classes([permissions.IsAuthenticated])
def collect(request):
    user = request.user
    serializer = CollectRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    id = serializer.validated_data['id']
    name = serializer.validated_data['collection']
    try:
        collection, _ = Collection.objects.get_or_create(collector=user, name=name)
        report = Report.objects.get(id=id)
        collection.reports.add(report)
        collection.save()
    except KeyError:
        return HttpResponse(status=400)
    except Report.DoesNotExist:
        return HttpResponse('{"detail": "report with id %d does not exist"}' % id, status=404)
    return Response(CollectionSerializer(collection).data)


@decorators.api_view(['post'])
@decorators.permission_classes([permissions.IsAuthenticated])
def uncollect(request):
    user = request.user
    serializer = CollectRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    id = serializer.validated_data['id']
    name = serializer.validated_data['collection']
    try:
        collection, _ = Collection.objects.get_or_create(collector=user, name=name)
        report = Report.objects.get(id=id)
        collection.reports.remove(report)
        collection.save()
    except KeyError:
        return HttpResponse(status=400)
    except Report.DoesNotExist:
        return HttpResponse('{"detail": "report with id %d does not exist"}' % id, status=404)
    return Response(CollectionSerializer(collection).data)


class ActiveUsersViewSet(generics.ListAPIView):
    serializer_class = UserInfoSerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        sorter = F('report') * 10 + F('comment') * 2 + F('followers')
        sorter = sorter.desc()
        return User.objects.order_by(sorter)
