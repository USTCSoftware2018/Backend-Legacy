from django.db import models
from django.conf import settings
from biohub.accounts.models import User


class Report(models.Model):

    title = models.CharField(max_length=256)
    authors = models.ManyToManyField(User)
    introduction = models.TextField()
    label = models.ManyToManyField('Label', related_name='reports_related')
    ntime = models.DateTimeField(auto_now_add=True)
    mtime = models.DateTimeField(auto_now=True)
    result = models.TextField()       # json
    subroutines = models.TextField()  # json
    envs = models.TextField(null=True)         # json
    html = models.TextField()         # html

    # See comments in Comment model!
    # See praises(likes in the doc) in User model

    def __str__(self):
        return 'id:{}, title:{}'.format(self.pk, self.title)


class Step(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='steps', on_delete=models.CASCADE)
    content_json = models.TextField()
    yield_method = models.TextField()

    def __str__(self):
        return 'id:{}'.format(self.pk)


class SubRoutine(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='subroutines', on_delete=models.CASCADE)
    content_json = models.TextField()
    yield_method = models.TextField()

    def __str__(self):
        return 'id:{}'.format(self.pk)


class Label(models.Model):
    label_name = models.CharField(max_length=64, unique=True)
    users = models.ManyToManyField(User)

    def __str__(self):
        return 'id:{}, name:{}'.format(self.pk, self.label_name)


class Graph(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='report_graphs')
    graph = models.ImageField(upload_to='report_graph', null=True, blank=True)


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    time = models.DateTimeField(auto_now=True)
    to_report = models.ForeignKey(Report, on_delete=models.CASCADE, db_index=True, related_name='comments')

    # @property
    # def all_sub_comments(self):
    #     return self.sub_comments.all().order_by('time')

    def __str__(self):
        return '{}, {}'.format(self.user, self.text)


class CommentReply(Comment):
    reply_to = models.OneToOneField(Comment, on_delete=models.CASCADE, default=None, blank=True, null=False,
                                    related_name='replied_by')
    # super_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, default=None, blank=True, null=True,
    #                                   related_name='sub_comments')


