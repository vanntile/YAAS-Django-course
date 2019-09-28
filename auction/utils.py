from django import forms
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import serializers

from auction.models import AuctionModel
from yaas.settings import CURRENCY_COOKIE_NAME


class CreateAuctionForm(forms.Form):
    title = forms.CharField(max_length=256)
    description = forms.CharField(max_length=3000, widget=forms.Textarea(attrs={'cols': 50}), required=False)
    minimum_price = forms.FloatField(initial=0.01)
    deadline_date = forms.CharField(initial=(timezone.now() + timezone.timedelta(hours=73)).strftime('%d.%m.%Y %H:%M:%S'))


class EditAuctionForm(forms.Form):
    title = forms.CharField(max_length=256, label="Do not edit the title")
    description = forms.CharField(max_length=3000, widget=forms.Textarea(attrs={'cols': 50}))


class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuctionModel
        fields = ('title', 'description', 'minimum_price', 'deadline_date')


def generate_response(message):
    return HttpResponse('<p>' + message + "</p> <p>You can check out the <a href='/'>homepage</a>.</p>", content_type="text/html", status=200)


def set_currencies(request, auctions):
    if CURRENCY_COOKIE_NAME in request.COOKIES and float(request.COOKIES[CURRENCY_COOKIE_NAME]) != 0:
        rate = float(request.COOKIES[CURRENCY_COOKIE_NAME])
        currency = 'usd'
    else:
        rate = 0
        currency = 'eur'

    if rate:
        for auction in auctions:
            auction.highest_bid = auction.highest_bid / rate
            auction.minimum_price = auction.minimum_price / rate

    return currency
