from django import forms
from django.utils import timezone
from rest_framework import serializers

from auction.models import AuctionModel


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
