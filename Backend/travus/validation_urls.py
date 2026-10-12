"""Expose the real travel endpoints to the isolated validation database."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import TravelSpotViewSet

router = DefaultRouter()
router.register("travel-spots", TravelSpotViewSet)
urlpatterns = [path("api/", include(router.urls))]
