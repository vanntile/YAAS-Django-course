from django.urls import path
from . import views

app_name = 'user'
urlpatterns = [
    path('profile/', views.EditProfile.as_view(), name='editprofile'),
    path('', views.EditProfile.as_view(), name='user')
]