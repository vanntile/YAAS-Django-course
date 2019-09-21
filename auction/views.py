from datetime import datetime, timedelta

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.core.mail import send_mail
from django.contrib.auth.models import User

from utils import *
from auction.models import AuctionModel


class Index(View):
    def get(self, request):
        return render(request, 'index.html', status=200)


def search(request):
    pass


class CreateAuction(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'createAuction.html', {'form': CreateAuctionForm()}, status=200)
        else:
            return HttpResponseRedirect(reverse('signin'), status=302)

    def post(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('signin'), status=302)
        form = CreateAuctionForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            deadline_date = cd['deadline_date']
            minimum_price = cd['minimum_price']

            try:
                deadline_date = datetime.strptime(deadline_date, '%d.%m.%Y %H:%M:%S')
            except ValueError:
                return render(request, 'createAuction.html', {'form': form, 'err': 'format'}, status=200)

            if (datetime.now() + timedelta(hours=72)) > deadline_date:
                return render(request, 'createAuction.html', {'form': form, 'err': 'deadline'}, status=200)

            if minimum_price < 0.01:
                return render(request, 'createAuction.html', {'form': form, 'err': 'min'}, status=200)

            # TODO create AuctionModel()

            send_mail(
                'Auction has been created successfully',
                'Auction has been created successfully.',
                'yaas-no-reply@yaas.com',
                [User.objects.get(username=request.user).email],
                fail_silently=False,
            )

            return HttpResponseRedirect(reverse('auction:success'), status=302)
        else:
            return render(request, 'createAuction.html', {'form': CreateAuctionForm()}, status=200)


def success(request):
    return HttpResponse("Auction has been created successfully", content_type="text/html", status=200)


class EditAuction(View):
    pass


def bid(request, item_id):
    pass


def ban(request, item_id):
    pass


def resolve(request):
    pass


def changeLanguage(request, lang_code):
    pass


def changeCurrency(request, currency_code):
    pass


