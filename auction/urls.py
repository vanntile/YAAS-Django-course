from django.urls import path, re_path
from . import views


app_name = 'auction'
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('search/', views.search, name='search'),
    path('create/', views.CreateAuction.as_view(), name='create'),
    re_path(r'(create|edit|bid|ban)/success/', views.success, name='success'),
    path('create/error', views.edit_auction_error, name='forbidden'),
    re_path(r'^edit/(\d+)/$', views.EditAuction.as_view(), name='edit'),
    re_path(r'^bid/(\d+)/$', views.bid, name='bid'),
    re_path(r'^ban/(\d+)$', views.ban, name='ban'),
    path('resolve/', views.resolve, name='resolve')
]
