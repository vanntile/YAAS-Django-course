from django.shortcuts import render
from django.views import View


class Index(View):
    def get(self, request):
        return render(request, 'index.html', status=200)


def search(request):
    pass


class CreateAuction(View):
    pass


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


