from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.core.mail import send_mail
from django.contrib.auth.models import User

from utils import *
from auction.models import AuctionModel


class Index(View):
    def get(self, request):
        auctions = AuctionModel.objects.all()
        print(auctions)
        return render(request, 'index.html', {'auctions': auctions}, status=200)


def search(request):
    if request.GET['term'].lower() != '':
        criteria = request.GET['term'].lower().strip()
        auctions = AuctionModel.objects.filter(title__contains=criteria, status=AuctionModel.ACTIVE)
    else:
        auctions = AuctionModel.objects.filter(status=AuctionModel.ACTIVE)

    return render(request, "searchresults.html", {'auctions': auctions})


@method_decorator(login_required, name='dispatch')
class CreateAuction(View):
    def get(self, request):
        return render(request, 'createAuction.html', {'form': CreateAuctionForm()}, status=200)

    def post(self, request):
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

            user = User.objects.get(username=request.user)
            auction = AuctionModel(seller=user.id, title=cd['title'], description=cd['description'], minimum_price=minimum_price, deadline_date=deadline_date)
            auction.save()

            send_mail(
                'Auction has been created successfully',
                'Auction has been created successfully.',
                'yaas-no-reply@yaas.com',
                [User.objects.get(username=request.user).email],
                fail_silently=False,
            )

            return HttpResponseRedirect(reverse('auction:success', args=("create",)), status=302)
        else:
            return render(request, 'createAuction.html', {'form': CreateAuctionForm()}, status=200)


def success(request, param):
    if param == "edit":
        return HttpResponse("Auction has been updated successfully", content_type="text/html", status=200)
    else:
        return HttpResponse("Auction has been created successfully", content_type="text/html", status=200)


@method_decorator(login_required, name='dispatch')
class EditAuction(View):
    def get(self, request, auction_id):
        user = User.objects.get(username=request.user)
        auction = AuctionModel.objects.get(id=auction_id)

        if auction.seller is not user.id:
            return HttpResponseRedirect(reverse('auction:forbidden'), status=302)
        else:
            return render(request, 'editAuction.html', {'form': EditAuctionForm(initial={
                'title': auction.title,
                'description': auction.description
            }), 'id': auction.id}, status=200)

    def post(self, request, auction_id):
        user = User.objects.get(username=request.user)
        auction = AuctionModel.objects.get(id=auction_id)

        if auction.seller is not user.id:
            return HttpResponseRedirect(reverse('auction:forbidden'), status=302)
        else:
            form = EditAuctionForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                auction.description = cd['description']
                auction.save()

                return HttpResponseRedirect(reverse('auction:success', args=("edit",)), status=302)
            else:
                render(request, 'editAuction.html', {'form': EditAuctionForm(initial={
                    'title': auction.title,
                    'description': auction.description
                }), 'id': auction.id}, status=200)


def edit_auction_error(request):
    return HttpResponse("<p>That is not your auction to edit.</p>\
     You can see all <a href='/'>auctions</a>", content_type="text/html", status=200)


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


