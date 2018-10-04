from rest_framework.routers import DefaultRouter
from biohub.core.routes import register_api, register_default, url
from . import views

router = DefaultRouter()
router.register('step', views.StepViewSet, base_name='step')
router.register('subroutine', views.SubRoutineViewSet, base_name='subroutine')
router.register('report', views.ReportViewSet, base_name='report')
router.register('label', views.LabelViewSet, base_name='label')

register_api(r'^editor/', router.urls)
register_api(r'^', [
    url(r'^users/labels/(?P<user_id>[0-9]+)/$', views.LabelViewSet.list_user_labels),
    url(r'^users/popular-reports-list/?$', views.ReportViewSet.get_popular_reports),
    url(r'^users/popular-reports-list/(?P<user_id>[0-9]+)/?$', views.ReportViewSet.get_user_popular_reports),
    url(r'^users/reports/archives/(?P<user_id>[0-9]+)/?$', views.ReportViewSet.get_user_archives),
    url(r'^users/reports/(?P<user_id>[0-9]+)/?$', views.ReportViewSet.list_user_reports, name='list_reports'),
], '')
