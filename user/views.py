from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from user.utils import *


class SignUp(View):
    def get(self, request):
        return render(request, 'signupform.html', {
            'form': CreateSignupForm(),
            'email_taken': False,
            'username_taken': False
        }, status=200)

    def post(self, request):
        form = CreateSignupForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            try:
                User.objects.get(username=cd['username'])
                print("username taken")
                return render(request, 'signupform.html', {
                    'form': CreateSignupForm(),
                    'email_taken': False,
                    'username_taken': True
                }, status=400)
            except User.DoesNotExist:
                try:
                    User.objects.get(email=cd['email'])
                    return render(request, 'signupform.html', {
                        'form': CreateSignupForm(),
                        'email_taken': True,
                        'username_taken': False
                    }, status=400)
                except User.DoesNotExist:
                    user = User.objects.create_user(cd['username'], cd['email'], cd['password'])
                    user.save()

                    return HttpResponseRedirect(reverse('index'), status=302)
        else:
            return render(request, 'signupform.html', {
                'form': CreateSignupForm(),
                'email_taken': False,
                'username_taken': False
            }, status=200)


class SignIn(View):
    def get(self, request):
        return render(request, 'sigininform.html', {
            'form': CreateSigninForm(),
            'wrong': False
        }, status=200)

    def post(self, request):
        form = CreateSigninForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('index'), status=302)
            else:
                return render(request, 'sigininform.html', {
                    'form': CreateSigninForm(),
                    'wrong': True
                }, status=401)
        else:
            return render(request, 'sigininform.html', {
                'form': CreateSigninForm(),
                'wrong': False
            }, status=401)


def signout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'), status=302)


class EditProfile(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'profile.html', {'form': CreateEditAccountForm()}, status=200)
        else:
            return HttpResponseRedirect(reverse('signin'), status=302)

    def post(self, request):
        form = CreateEditAccountForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            if cd['email']:
                try:
                    User.objects.get(email=cd['email'])
                    return render(request, 'profile.html', {'form': CreateEditAccountForm()}, status=200)
                except User.DoesNotExist:
                    user = User.objects.get(username=request.user)
                    user.email = cd['email']
                    user.save()

            if cd['password']:
                user = User.objects.get(username=request.user)
                user.set_password(cd['password'])
                user.save()
                update_session_auth_hash(request, user)

            return HttpResponseRedirect(reverse('user:user'), status=302)

        return render(request, 'profile.html', {'form': CreateEditAccountForm()}, status=200)

