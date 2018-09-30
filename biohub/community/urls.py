from rest_framework.routers import DefaultRouter
from biohub.core.routes import register_api, register_default, url
from biohub.community import views

router = DefaultRouter()
router.register(r'users/favorites', views.StarViewSet, base_name='favorites')

# Place your route definition here.
register_api(r'^', router.urls, 'users/favorites')
