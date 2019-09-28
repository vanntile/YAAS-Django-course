import json
from datetime import datetime, timedelta, timezone

import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import signing
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware
from django.views import View
from django.views.decorators.http import require_POST, require_GET

from auction.models import AuctionModel
from auction.utils import CreateAuctionForm, EditAuctionForm, set_currencies, generate_response
from yaas.settings import LANGUAGE_COOKIE_NAME, CURRENCY_API, CURRENCY_COOKIE_NAME


class Index(View):
    def get(self, request):
        auctions = AuctionModel.objects.filter(status=AuctionModel.ACTIVE)
        currency = set_currencies(request, auctions)

        return render(request, 'index.html', {'auctions': auctions, 'currency': currency}, status=200)


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

    currency = set_currencies(request, auctions)
    return render(request, "index.html", {'auctions': auctions, 'search': True, 'currency': currency}, status=200)


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
                                   minimum_price=minimum_price, deadline_date=make_aware(deadline_date),
                                   highest_bid=minimum_price)
            auction.save()

            signed_url = request.get_host() + reverse('auction:edit_signed', args=(signing.dumps({
                "username": user.username,
                "auction": auction.id
            }),))

            msg = EmailMessage(
                'Auction has been created successfully',
                'Auction has been created successfully. This is the link to your <a href="' +
                signed_url + '">auction</a>',
                'yaas-no-reply@yaas.com',
                [User.objects.get(username=request.user).email]
            )
            msg.content_subtype = "html"
            msg.send()

            return HttpResponseRedirect(reverse('auction:success', args=("create",)), status=302)
        else:
            return render(request, 'createAuction.html', {'form': CreateAuctionForm()}, status=200)


def success(request, param):
    if param == "edit":
        return generate_response("Auction has been updated successfully")
    elif param == "create":
        return generate_response("Auction has been created successfully")
    elif param == "bid":
        return generate_response("You has bid successfully")
    elif param == "ban":
        return generate_response("Ban successfully")


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
                return render(request, 'editAuction.html', {'form': EditAuctionForm(initial={
                    'title': auction.title,
                    'description': auction.description
                }), 'id': auction.id}, status=200)


class EditSigned(View):
    def get(self, request, signature):
        try:
            signed_object = signing.loads(signature)
        except signing.BadSignature:
            return generate_response("You tried to edit a non-existing auction.")

        auction = AuctionModel.objects.get(id=signed_object['auction'])

        return render(request, 'editAuction.html', {'form': EditAuctionForm(initial={
            'title': auction.title,
            'description': auction.description
        }), 'secret': signature}, status=200)

    def post(self, request, signature):
        try:
            signed_object = signing.loads(signature)
        except signing.BadSignature:
            return generate_response("You tried to edit a non-existing auction.")

        auction = AuctionModel.objects.get(id=signed_object['auction'])
        form = EditAuctionForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            auction.description = cd['description']
            auction.save()

            return HttpResponseRedirect(reverse('auction:success', args=("edit",)), status=302)
        else:
            return render(request, 'editAuction.html', {'form': EditAuctionForm(initial={
                'title': auction.title,
                'description': auction.description
            }), 'secret': signature}, status=200)


def edit_auction_error(request):
    return generate_response("That is not your auction to edit.")


@require_POST
@login_required()
def bid(request, auction_id):
    user = User.objects.get(username=request.user)
    auction = AuctionModel.objects.get(id=auction_id)
    amount = float("{0:.2f}".format(float(request.POST['new_price'])))

    if auction.seller is user.id:
        return generate_response("You cannot bid on your own auctions")

    if auction.status != AuctionModel.ACTIVE:
        return generate_response("You can only bid on active auctions")

    if auction.deadline_date < datetime.now(timezone.utc):
        return generate_response("You can only bid on active auctions")

    if int(amount * 100) < int(auction.highest_bid * 100) + 1:
        return generate_response("New bid must be greater than the current bid for at least 0.01")

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

    return HttpResponse(json.dumps({'resolved_auctions': auctions_resolved}), content_type="application/json",
                        status=200)


@require_GET
def changeLanguage(request, lang_code):
    supported_languages = ['en', 'sv']
    if lang_code in supported_languages:

        if lang_code == 'en':
            response = generate_response("Language has been changed to English")
        else:
            response = generate_response("Language has been changed to Swedish")

        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            user.language.language = lang_code
            user.save()

        translation.activate(lang_code)
        response.set_cookie(LANGUAGE_COOKIE_NAME, lang_code)
        return response
    else:
        return HttpResponseRedirect(reverse('index'), status=302)


@require_GET
def changeCurrency(request, currency_code):
    supported_currencies = ['eur', 'usd']
    if currency_code.lower() in supported_currencies:
        if currency_code.lower() == 'eur':
            response = generate_response("Currency has been changed to EUR")
            response.set_cookie(CURRENCY_COOKIE_NAME, "0")
        else:
            response = requests.get(CURRENCY_API)
            rate = response.json()['quotes']['USDEUR']
            response = generate_response("Currency has been changed to USD")
            response.set_cookie(CURRENCY_COOKIE_NAME, rate)

        return response
    else:
        return HttpResponseRedirect(reverse('index'), status=302)
