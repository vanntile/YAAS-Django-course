from django.db import models


class AuctionModel(models.Model):
    seller = models.CharField(max_length=64)
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=3000)
    minimum_price = models.FloatField()
    deadline_date = models.DateTimeField()
