"""yaas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include

import auction.services
import auction.views
import user.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auction/', include('auction.urls', namespace='auction')),
    path('user/', include('user.urls', namespace='user')),
    path('', auction.views.Index.as_view(), name='index'),
    path('signup/', user.views.SignUp.as_view(), name='signup'),
    path('signin/', user.views.SignIn.as_view(), name='signin'),
    path('signout/', user.views.signout, name='signout'),
    path('changeLanguage/<lang_code>/', auction.views.changeLanguage, name='changeLanguage'),
    path('changeCurrency/<currency_code>/', auction.views.changeCurrency, name='changeCurrency')
]

urlpatterns += [
    path('api/v1/browse/', auction.services.BrowseAuctionApi.as_view(), name='browseauctionsapi'),
    re_path(r'^api/v1/search/(\w+)/?$', auction.services.SearchAuctionApi.as_view(), name='searchauctionapi'),
    re_path(r'^api/v1/search/\??(?:&?[^=&]*=[^=&]*)*', auction.services.SearchAuctionWithTermApi.as_view(),
            name='searchauctionwithtermapi'),
    re_path(r'^api/v1/searchid/(\d+)/$', auction.services.SearchAuctionApiById.as_view(), name='searchauctionbyidapi'),
    re_path(r'^api/v1/bid/(\d+)/$', auction.services.BidAuctionApi.as_view(), name='bidauctionapi'),
]
