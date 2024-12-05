from django.urls import path
from .views import google_auth, refresh_token

app_name = 'authentication'

urlpatterns = [
    path('google/', google_auth, name='google_auth'),
    path('refresh-token/', refresh_token, name='refresh_token'),
]
