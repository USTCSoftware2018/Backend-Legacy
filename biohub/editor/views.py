from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.conf import settings
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser, FileUploadParser
import json
from django.utils import timezone
from rest_framework import viewsets, decorators, pagination, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from biohub.accounts.models import User
from .models import Graph, SubRoutine, Step, Report, Label, Archive
from .models import Comment
from .serializers import StepSerializer, SubRoutineSerializer, ReportSerializer, LabelSerializer, ArchiveSerializer, \
    GraphSerializer, CommentSerializer
from .serializers import PopularReportSerializer, ReportInfoSerializer
from .permissions import IsOwnerOrReadOnly, IsAuthorOrReadyOnly, IsOwner
# import logging


class StepViewSet(viewsets.ModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        user = self.request.user
        return Step.objects.filter(user=user)


class SubRoutineViewSet(viewsets.ModelViewSet):
    queryset = SubRoutine.objects.all()
    serializer_class = SubRoutineSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        user = self.request.user
        return SubRoutine.objects.filter(user=user)


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadyOnly)
    pagination_class = pagination.PageNumberPagination

    def get_object(self):
        obj = super().get_object()
        obj.viewed()  # increment views counter
        return obj

    @staticmethod
    @decorators.api_view(['get'])
    def list_user_reports(request, user_id):
        queryset = Report.objects.filter(author_id=user_id)
        paginator = pagination.PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ReportInfoSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @staticmethod
    @decorators.api_view(['get'])
    def get_popular_reports(request):
        paginator = pagination.PageNumberPagination()
        queryset = Report.get_popular()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ReportInfoSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @staticmethod
    @decorators.api_view(['get'])
    def get_user_popular_reports(request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'response': 'User id %s does not exist' % str(user_id)
            }, status=404)
        paginator = pagination.PageNumberPagination()
        queryset = Report.get_user_popular(user)
        page = paginator.paginate_queryset(queryset, request)
        serializer = PopularReportSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @staticmethod
    @decorators.api_view(['get'])
    def get_user_archives(request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'response': 'User id %s does not exist' % str(user_id)
            }, status=404)

        archives = Archive.objects.filter(user=user)
        serializer = ArchiveSerializer(archives, many=True)
        return Response(serializer.data)


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    permission_classes = [IsOwner]

    @decorators.api_view()
    def list_user_labels(request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404()

        labels = Label.objects.filter(reports_related__author=user)
        serializer = LabelSerializer(labels, many=True)
        return Response(serializer.data)


class PictureViewSet(viewsets.ModelViewSet):
    serializer_class = GraphSerializer
    queryset = Graph.objects.all()
    # permission_classes = [IsOwnerOrReadOnly]
    parser_classes = (FormParser, JSONParser, MultiPartParser, FileUploadParser)

    @csrf_exempt
    def create(self, request, *args, **kwargs):
        try:
            user_pk = request.user.pk
            user = User.objects.get(pk=user_pk)
            uidb64 = bytes.decode(urlsafe_base64_encode(force_bytes(user.pk)))
        except:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if user and user.is_active:
            picture = request.FILES.get('graph') or request.FILES.get('file')
            if picture is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            print(picture.size)
            if 10000 < picture.size < 409600000:
                picture.name = uidb64 + '_' + timezone.now().strftime('%Y%m%d%H%M%S') + '_' + picture.name
                image = Graph(owner=user, graph=picture)
                image.save()
                s = GraphSerializer(image)
                return Response(s.data, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class CommentPostSingle(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def create(self, request, *args, **kwargs):
        comment_json = request.POST.body.decode()
        comment = json.loads(comment_json)
        report_pk = comment['to_report']
        report = Report.objects.get(pk=report_pk)
        user = request.user
        message = comment['message']  # message
        to_comment = comment['to_comment']  # comment_pk

        if user is not None and user.is_active:

            if to_comment == -1:
                new_comment = Comment()
                new_comment.user = user
                new_comment.text = message
                new_comment.to_report = report
                new_comment.reply_to = None
                new_comment.save()

            else:
                new_comment = Comment()
                new_comment.user = user
                new_comment.text = message
                new_comment.to_report = report
                new_comment.reply_to = Comment.objects.get(pk=to_comment)
                new_comment.save()

            s = CommentSerializer(new_comment)
            return Response(data=s.data, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @decorators.list_route(methods=['get'])
    def get_report_comment(self, request, report_pk=None):
        report = get_object_or_404(Report, pk=report_pk)
        _list = Comment.objects.filter(to_report=report)
        list_s = CommentSerializer(_list, many=True)
        return Response(data=list_s, status=status.HTTP_200_OK)


def comment_post_single(request):

    body = {
        'to_report': 366,  # report id
        'message': "I find it funny",  # comment body
        'to_comment': 32,  # comment id, "to_comment" = -1 if don't have superior one
    }

    if request.method == 'POST':
        comment_json = request.POST.body.decode()
        comment = json.loads(comment_json)
        report_pk = comment['to_report']
        report = Report.objects.get(pk=report_pk)
        user = request.user
        message = comment['message']  # message
        to_comment = comment['to_comment']  # comment_pk

        if user is not None and user.is_active:

            if to_comment == -1:
                new_comment = Comment()
                new_comment.user = user
                new_comment.text = message
                new_comment.to_report = report
                new_comment.reply_to = None
                new_comment.save()

            else:
                new_comment = Comment()
                new_comment.user = user
                new_comment.text = message
                new_comment.to_report = report
                new_comment.reply_to = Comment.objects.get(pk=to_comment)
                new_comment.save()

        else:
            pass
    else:
        pass
