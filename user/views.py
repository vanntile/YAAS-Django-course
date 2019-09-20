from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.contrib.auth.models import User

from user.utils import CreateSignupForm


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

            print("valid_form")
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
            print("invalid")
            return render(request, 'signupform.html', {
                'form': CreateSignupForm(),
                'email_taken': False,
                'username_taken': False
            }, status=200)


class SignIn(View):
    pass


def signout(request):
    pass


class EditProfile(View):
    pass
