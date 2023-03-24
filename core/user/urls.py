"""URl mapping for the user API."""

from django.urls import path

from user import views


app_name = 'user'


urlpatterns = [
    path('create/', views.UserCreateAPIView.as_view(), name='create'),
    path('token/', views.CustomObtainAuthToken.as_view(), name='token'),
    path('profile/', views.UserProfileRetrieveUpdateAPIView.as_view(), name='profile'),
]
