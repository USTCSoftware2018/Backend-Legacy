from django.http import HttpResponse, Http404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
from django.utils import timezone
from rest_framework import mixins, viewsets, decorators
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from biohub.accounts.models import User
from .models import Graph, SubRoutine, Step, Report, Label
from .models import Comment, CommentReply
from .serializers import StepSerializer, SubRoutineSerializer, ReportSerializer
from .permissions import IsOwnerOrReadOnly, IsAuthorOrReadyOnly


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

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Report.objects.filter(authors=user)
        else:
            return Report.objects.all()


class LabelViewSet(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):
        try:
            return Response(request.user.labels)
        except:
            raise Http404()

    @decorators.api_view()
    def list_user_labels(request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404()

        labels = []
        for report in Report.objects.filter(authors=user):
            labels += report.label.all()
        return Response(l.label_name for l in labels)


@require_http_methods(['POST', 'GET', 'DELETE'])
def report_html(request, id):
    user = request.user
    try:
        report = Report.objects.get(id=id)
    except Report.DoesNotExist:
        return Http404()

    if request.method == 'GET':
        return HttpResponse(report.html)
    elif request.method == 'POST':
        if not user or not user.is_authenticated or user not in report.authors:
            return Http404()
        report.html = request.data
        return HttpResponse()
    elif request.method == 'DELETE':
        if not user or not user.is_authenticated or user not in report.authors:
            return Http404()
        report.html = ""
        return HttpResponse()


def post_picture(request):
    if request.method == 'POST' or 'OPTIONS':
        user_pk = request.user.pk
        user = User.objects.get(pk=user_pk)
        uidb64 = bytes.decode(urlsafe_base64_encode(force_bytes(user.pk)))
        if user and user.is_active:
            try:
                picture = request.FILES.get('file')
            except:
                err_msg = {
                    'meta': {
                        'success': False,
                        'message': 'No Picture Updated',
                    },
                    'data': None
                }
                response = HttpResponse(content_type="application/json")
                response.write(json.dumps(err_msg))
                return response

            if 10000 < picture.size < 409600000:
                picture.name = uidb64 + '_' + timezone.now().strftime('%Y%m%d%H%M%S') + '_' + picture.name
                image = Graph(owner=user, graph=picture)
                image.save()
                msg = {
                    'meta': {
                        'success': True,
                        'message': 'Success',
                    },
                    'data': settings.MEDIA_ROOT + image.graph.url
                }
                response = HttpResponse(content_type="application/json")
                response.write(json.dumps(msg))
                return response
                # return HttpResponse(json.dumps(msg))
            else:
                err_msg = {
                    'meta': {
                        'success': False,
                        'message': 'Picture Is Too Large Or Too Small',
                    },
                    'data': str(picture.size/1000) + 'kb'
                }
                response = HttpResponse(content_type="application/json")
                response.write(json.dumps(err_msg))
                return response
        else:
            err_msg = {
                'meta': {
                    'success': False,
                    'message': 'Identify Error',
                },
                'data': None,
            }
            response = HttpResponse(content_type="application/json")
            response.write(json.dumps(err_msg))
            return response
    else:
        err_msg = {
            'meta': {
                'success': False,
                'message': 'Method Error',
            },
            'data': None,
        }
        response = HttpResponse(content_type="application/json")
        response.write(json.dumps(err_msg))
        return response


# def comment_post(request):
#     """
#     This is comment_post upload function, request need a json in the body. Return a json. Second ranks!
#     :param request:
#                 body = {
#                     'to_report': 366,  # report id
#                     'message': "I find it funny",  # comment body
#                     'to_comment': {
#                     'type': 'master',  # One of "master", "main", "else"
#                     'value': -1,  # One of -1(if master), super_comment's id(if main), the_comment_you_reply's id(if else)
#                 }
#             }
#     :return:
#     """
#
#     body = {
#         'to_report': 366,  # report id
#         'message': "I find it funny",  # comment body
#         'to_comment': {
#             'type': 'master',  # One of "master", "main", "else"
#             'value': -1,  # One of -1(if master), super_comment's id(if main), the_comment_you_reply's id(if else)
#         }
#     }
#     if request.method == 'POST':
#         comment_json = request.POST.body.decode()
#         comment = json.loads(comment_json)
#         # comment_json = request.POST.get('comment', '')
#         # comment = json.loads(comment_json)
#         report_pk = comment['to_report']
#         report = Report.objects.get(pk=report_pk)
#         user = request.user
#         message = comment['message']  # message
#         to_comment = comment['to_comment']  # comment_pk
#         # to_comment = json.loads(to_comment)
#
#         if user is not None and user.is_active:
#
#             if to_comment['type'] == 'master':
#                 new_comment = Comment()
#                 new_comment.user = user
#                 new_comment.text = message
#                 new_comment.to_report = report
#                 new_comment.save()
#             elif to_comment['type'] == 'main':
#                 new_comment = CommentReply()
#                 new_comment.user = user
#                 new_comment.text = message
#                 new_comment.to_report = report
#                 new_comment.reply_to = None
#                 super_comment = Comment.objects.get(id=to_comment['value'])
#                 new_comment.super_comment = super_comment
#                 new_comment.save()
#             else:
#                 new_comment = CommentReply()
#                 new_comment.user = user
#                 new_comment.text = message
#                 new_comment.to_report = report
#                 reply_to = CommentReply.objects.get(id=to_comment['value'])
#                 super_comment = reply_to.super_comment
#                 new_comment.reply_to = reply_to
#                 new_comment.super_comment = super_comment
#                 new_comment.save()
#
#         else:
#             pass


def comment_post_single(request):
    """
    This is for single ranked comment.
    :param request:
    :return:
    """

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
                new_comment.save()

            else:
                new_comment = CommentReply()
                new_comment.user = user
                new_comment.text = message
                new_comment.to_report = report
                new_comment.reply_to = Comment.objects.get(pk=to_comment)
                new_comment.save()

        else:
            pass
    else:
        pass
