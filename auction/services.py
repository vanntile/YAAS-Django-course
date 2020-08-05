import json
import re
from datetime import datetime
from random import choice, randint

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auction.models import AuctionModel
from auction.utils import AuctionSerializer


class BrowseAuctionApi(APIView):
    def get(self, request):
        auctions = AuctionModel.objects.filter(status=AuctionModel.ACTIVE)
        serializer = AuctionSerializer(auctions, many=True)
        return Response(serializer.data, status=200)


class SearchAuctionApi(APIView):
    def get(self, request, term):
        if term.lower() != '':
            criteria = term.lower().strip()
            auctions = AuctionModel.objects.filter(title__contains=criteria, status=AuctionModel.ACTIVE)
        else:
            auctions = AuctionModel.objects.filter(status=AuctionModel.ACTIVE)

        return Response(AuctionSerializer(auctions, many=True).data, status=200)


class SearchAuctionWithTermApi(APIView):
    def get(self, request):
        if request.GET['term'].lower() != '':
            criteria = request.GET['term'].lower().strip()
            auctions = AuctionModel.objects.filter(title__contains=criteria, status=AuctionModel.ACTIVE)
        else:
            auctions = AuctionModel.objects.filter(status=AuctionModel.ACTIVE)
        return Response(AuctionSerializer(auctions, many=True).data, status=200)


class SearchAuctionApiById(APIView):
    def get(self, request, auction_id):
        try:
            auction = AuctionModel.objects.get(id=int(auction_id))
        except AuctionModel.DoesNotExist:
            auction = None

        return Response(AuctionSerializer(auction).data, status=200)


@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
class BidAuctionApi(APIView):
    def post(self, request, auction_id):
        user = User.objects.get(username=request.user)
        auction = AuctionModel.objects.get(id=auction_id)

        if auction.status != AuctionModel.ACTIVE:
            return Response({"message": "Can only bid on active auction"}, status=400)

        if auction.seller is request.user.id:
            return Response({"message": "Cannot bid on own auction"}, status=400)

        try:
            new_price = float(request.data['new_price'])
            amount = float("{0:.2f}".format(new_price))
        except ValueError:
            return Response({"message": "Bid must be a number"}, status=400)

        if int(amount * 100) < int(auction.highest_bid * 100) + 1:
            return Response({"message": "New bid must be greater than the current bid at least 0.01"}, status=400)

        auction.highest_bid = amount
        auction.highest_bidder = user.id
        auction.save()

        bidders = json.loads(auction.bidders)
        bidders.append(user.id)
        auction.bidders = json.dumps(bidders)

        send_mail(
            'Auction has been bid through API',
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

        response = {
            'message': 'Bid successfully',
            'title': auction.title,
            'description': auction.description,
            'current_price': auction.highest_bid,
            'deadline_date': auction.deadline_date
        }

        return Response(response, status=200)


class GenerateDataAPI(View):
    def get(self, request):
        products_str = "Bacon pork belly bacon short ribs tenderloin strip steak landjaeger biltong meatball flank, " \
                       "kielbasa shank.  Spare ribs venison sirloin short loin pork loin tri-tip, pork chop pork " \
                       "belly tongue.  Beef doner pork chop alcatra cupim.  Pastrami short ribs boudin, corned beef " \
                       "leberkas ribeye buffalo filet mignon prosciutto rump tongue sausage beef ribs bresaola cow. "
        products = re.split('\W+', products_str)

        timestamp = '_' + str(datetime.now().timestamp())[3:10]
        deadline_date = timezone.now() + timezone.timedelta(hours=73)

        usernames_prefix = ['edwin_elric', 'lelouch', 'kira', 'natsu', 'luffy', 'kakashi', 'goku']
        usernames_suffix = ['', '11', '42', '7', '1000', '4k', '420']
        usernames = ['vanntile' + timestamp]

        users = []
        auctions = []

        for prefix in usernames_prefix:
            for suffix in usernames_suffix:
                usernames.append(prefix + suffix + timestamp)

        # create users
        for username in usernames:
            user = User.objects.create_user(username, username + '@yaas.com', username)
            user.save()
            users.append(user)

            # create auctions
            for i in range(1, randint(1, 5)):
                description = ''.join(choice(products_str) for j in range(randint(50, 300)))
                price = randint(1, 100)
                auction = AuctionModel(seller=user.id, title=choice(products), description=description,
                                       minimum_price=price, deadline_date=deadline_date, highest_bid=price)
                auction.save()
                auctions.append(auction)

        # create bids
        for i in range(randint(15, 40)):
            user = User.objects.get(id=randint(users[0].id, users[-1].id))
            auction = AuctionModel.objects.get(id=randint(auctions[0].id, auctions[-1].id))

            auction.highest_bid = auction.highest_bid + randint(10, 100)
            auction.highest_bidder = user.id
            bidders = json.loads(auction.bidders)
            bidders.append(user.id)
            auction.bidders = json.dumps(bidders)
            auction.save()

        return render(request, 'generateData.html', {
            'users': users,
            'auctions': auctions
        }, status=200)
