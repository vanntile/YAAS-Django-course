from django.db import models


class AuctionModel(models.Model):
    ACTIVE = 'AC'
    BANNED = 'BN'
    DUE = 'DU'
    ADJUDECATED = 'AD'
    STATUSES = [
        (ACTIVE, 'Active'),
        (BANNED, 'Banned'),
        (DUE, 'Due'),
        (ADJUDECATED, 'Adjudecated')
    ]
    seller = models.IntegerField()
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=3000)
    minimum_price = models.FloatField()
    deadline_date = models.DateTimeField()
    status = models.CharField(max_length=12, choices=STATUSES, default=ACTIVE)
    highest_bid = models.FloatField(default=0)
    highest_bidder = models.IntegerField(default=-1)
    bidders = models.TextField(default="[]")
    version = models.IntegerField(default=0)
