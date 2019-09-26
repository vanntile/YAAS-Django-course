from datetime import datetime, timedelta, timezone

import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import translation
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST, require_GET
from django.utils.translation import gettext as _

import settings
from auction.models import AuctionModel
from utils import *


class Index(View):
    def get(self, request):
        auctions = AuctionModel.objects.filter(status=AuctionModel.ACTIVE)
        return render(request, 'index.html', {'auctions': auctions}, status=200)


def search(request):
    if request.GET['term'].lower() != '':
        criteria = request.GET['term'].lower().strip()
        if request.user.is_superuser:
            auctions = AuctionModel.objects.filter(title__contains=criteria)
        else:
            auctions = AuctionModel.objects.filter(title__contains=criteria, status=AuctionModel.ACTIVE)
    else:
        if request.user.is_superuser:
            auctions = AuctionModel.objects.all()
        else:
            auctions = AuctionModel.objects.filter(status=AuctionModel.ACTIVE)

    return render(request, "index.html", {'auctions': auctions, 'search': True}, status=200)


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
            auction = AuctionModel(seller=user.id, title=cd['title'], description=cd['description'],
                                   minimum_price=minimum_price, deadline_date=deadline_date, highest_bid=minimum_price)
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
    elif param == "create":
        return HttpResponse("Auction has been created successfully", content_type="text/html", status=200)
    elif param == "bid":
        return HttpResponse("You has bid successfully", content_type="text/html", status=200)
    elif param == "ban":
        return HttpResponse("Ban successfully", content_type="text/html", status=200)


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


@require_POST
@login_required()
def bid(request, auction_id):
    user = User.objects.get(username=request.user)
    auction = AuctionModel.objects.get(id=auction_id)
    amount = float("{0:.2f}".format(float(request.POST['new_price'])))

    if auction.seller is user.id:
        return HttpResponse("You cannot bid on your own auctions", content_type="text/html", status=200)

    if auction.status != AuctionModel.ACTIVE:
        return HttpResponse("You can only bid on active auctions", content_type="text/html", status=200)

    if auction.deadline_date < datetime.now(timezone.utc):
        return HttpResponse("You can only bid on active auctions", content_type="text/html", status=200)

    if int(amount * 100) < int(auction.highest_bid * 100) + 1:
        return HttpResponse("New bid must be greater than the current bid for at least 0.01", content_type="text/html",
                            status=200)

    auction.highest_bid = amount
    auction.highest_bidder = user.id
    bidders = json.loads(auction.bidders)
    bidders.append(user.id)
    auction.bidders = json.dumps(bidders)
    auction.save()

    send_mail(
        'Auction has been bid',
        'Auction #' + str(auction.id) + ' has a new highest bid',
        'yaas-no-reply@yaas.com',
        [User.objects.get(id=auction.seller).email],
        fail_silently=False,
    )

    send_mail(
        'You have bid an auction',
        'You have the highest bid to auction #' + str(auction.id),
        'yaas-no-reply@yaas.com',
        [User.objects.get(id=user.id).email],
        fail_silently=False,
    )

    return HttpResponseRedirect(reverse('auction:success', args=("bid",)), status=302)


@require_POST
@login_required()
def ban(request, auction_id):
    user = User.objects.get(username=request.user)
    auction = AuctionModel.objects.get(id=auction_id)

    if not user.is_superuser:
        return HttpResponseRedirect(reverse('index'), status=302)

    auction.status = AuctionModel.BANNED
    bidders = json.loads(auction.bidders)
    bidders.append(auction.seller)
    for user_id in bidders:
        send_mail(
            'Auction banned',
            'Auction #' + str(auction.id) + ' has been banned',
            'yaas-no-reply@yaas.com',
            [User.objects.get(id=user_id).email],
            fail_silently=False,
        )
    auction.save()

    return HttpResponseRedirect(reverse('auction:success', args=("ban",)), status=302)


def resolve(request):
    auctions_active = AuctionModel.objects.filter(status=AuctionModel.ACTIVE)
    auctions_resolved = []

    for auction in auctions_active:
        if auction.deadline_date < datetime.now(timezone.utc):
            bidders = json.loads(auction.bidders)
            bidders.append(auction.seller)
            for user_id in bidders:
                send_mail(
                    'Auction banned',
                    'Auction #' + str(auction.id) + ' has been banned',
                    'yaas-no-reply@yaas.com',
                    [User.objects.get(id=user_id).email],
                    fail_silently=False,
                )

            if auction.highest_bidder == -1:
                auction.status = AuctionModel.DUE
            else:
                auction.status = AuctionModel.ADJUDECATED
            auction.save()
            auctions_resolved.append(auction.title)

    return HttpResponse(json.dumps({'resolved_auctions': auctions_resolved}), content_type="application/json", status=200)


@require_GET
def changeLanguage(request, lang_code):
    supported_languages = ['en', 'sv']
    if lang_code in supported_languages:

        if lang_code == 'en':
            response = HttpResponse("Language has been changed to English", content_type="text/html", status=200)
        else:
            response = HttpResponse("Language has been changed to Swedish", content_type="text/html", status=200)

        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            user.language.language = lang_code
            user.save()

        translation.activate(lang_code)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
        return response
    else:
        return HttpResponseRedirect(reverse('index'), status=302)

    # n = request.REQUEST.get('next', None)
    # if not n:
    #     n = request.META.get('HTTP_REFERER', None)
    # if not n:
    #     n = '/'
    # response = HttpResponseRedirect(n)
    #


def changeCurrency(request, currency_code):
    pass


