from rest_framework.routers import DefaultRouter
from biohub.core.routes import register_api, register_default, url
from . import views

router = DefaultRouter()
router.register('step', views.StepViewSet, base_name='step')
router.register('subroutine', views.SubRoutineViewSet, base_name='subroutine')
router.register('report', views.ReportViewSet, base_name='report')
router.register('label', views.LabelViewSet, base_name='label')

register_api(r'^editor/', [
    url(r'^label/(?P<user_id>[0-9]+)/$', views.LabelViewSet.list_user_labels)
] + router.urls, '')
