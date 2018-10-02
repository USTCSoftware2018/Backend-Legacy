from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save

from biohub.notices.models import Notice
from biohub.notices.tool import Dispatcher

from biohub.accounts.models import User
from biohub.accounts.user_defined_signals import follow_user_signal, unfollow_user_signal

from biohub.editor.models import Report, Comment

from biohub.community.models import Star


community_dispatcher = Dispatcher('Community')


@receiver(pre_delete, sender=Report)
def remove_report_notices(instance, using, **kwargs):
    Notice.objects.filter(report=instance).delete()


@receiver(follow_user_signal, sender=User)
def send_notice_to_followed_user(instance, target_user, **kwargs):
    community_dispatcher.send(
        target_user,
        '{{actor.username|url:actor}} started following you',
        actor=instance,
        target_slug='follow'
    )


@receiver(unfollow_user_signal, sender=User)
def remove_notices_on_unfollow(instance, target_user, **kwargs):
    Notice.objects.filter(
        user=target_user,
        actor=instance,
        target_slug__in=['new_post', 'follow']
    ).delete()


@receiver(post_save, sender=Star)
def send_notice_to_starred_report_author(instance, raw, created, using, update_fields, **kwargs):
    if created:
        starrer = instance.starrer
        report = instance.starred_report
        author = report.author
        community_dispatcher.send(
            author,
            '{{actor.username|url:actor}} starred your report {{report.title|url:report}}',
            actor=starrer,
            report=report,
            target_slug='star'
        )


@receiver(pre_delete, sender=Star)
def remove_notices_on_unstar(instance, using, **kwargs):
    Notice.objects.filter(
        user=instance.starred_report.author,
        actor=instance.starrer,
        report=instance.starred_report,
        target_slug='star'
    )


@receiver(post_save, sender=Comment)
def send_notice_to_commented_report_author(instance, raw, created, using, update_fields, **kwargs):
    if created:
        commenter = instance.user
        report = instance.to_report
        community_dispatcher.send(
            report.author,
            '{{actor.username|url:actor}} commented on your report {{report.title|url:report}}',
            actor=commenter,
            report=report,
            target_slug='comment'
        )


@receiver(pre_delete, sender=Comment)
def remove_notices_on_delete_comment(instance, using, **kwargs):
    report = instance.to_comment
    Notice.objects.filter(
        user=report.author,
        actor=instance.user,
        report=report,
        target_slug='comment'
    )


@receiver(post_save, sender=Report)
def send_new_report_notice_to_followers(instance, raw, created, **kwargs):
    if created:
        author = instance.author
        for follower in author.followers.all():
            community_dispatcher.send(
                follower,
                '{{actor.username|url:actor}} wrote a new report {{report.title|url:report}}',
                actor=author,
                report=instance,
                target_slug='new_report'
            )
