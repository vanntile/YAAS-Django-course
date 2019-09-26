import json

from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail

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


class BidAuctionApi(APIView):
    def post(self, request, auction_id):
        try:
            user = User.objects.get(username=request.user)
        except User.DoesNotExist:
            user = None

        auction = AuctionModel.objects.get(id=auction_id)

        if auction.status != AuctionModel.ACTIVE:
            return Response({"message": "Can only bid on active auction"}, status=400)

        if not user or not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided"}, status=401)

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
