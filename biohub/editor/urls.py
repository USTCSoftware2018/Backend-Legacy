from rest_framework.routers import DefaultRouter
from biohub.core.routes import register_api, register_default, url
from . import views

router = DefaultRouter()
router.register('step', views.StepViewSet)
router.register('subroutine', views.SubRoutineViewSet)
router.register('report', views.ReportViewSet)

register_api(r'^editor/', router.urls, '')
