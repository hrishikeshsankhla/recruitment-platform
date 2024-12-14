from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmailTemplateViewSet, EmailCampaignViewSet, EmailDraftViewSet

router = DefaultRouter()
router.register(r'templates', EmailTemplateViewSet, basename='email-template')
router.register(r'campaigns', EmailCampaignViewSet, basename='email-campaign')
router.register(r'drafts', EmailDraftViewSet, basename='email-draft')

urlpatterns = [
    path('', include(router.urls)),
]
