from biohub.core.routes import register_api, url
from rest_framework.routers import DefaultRouter

from .views import SearchViewSet

router = DefaultRouter()

router.register(r'^search', SearchViewSet, base_name='search')


register_api('', [

] + router.urls, 'search')
