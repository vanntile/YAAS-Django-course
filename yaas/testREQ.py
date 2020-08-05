import re

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from yaas.settings import LANGUAGE_COOKIE_NAME

current_points = 0


class StoreLanguageTest(TestCase):
    """Test for REQ9.3 store language permanently"""

    number_of_passed_tests = 0  # passed tests in this test case
    tests_amount = 3  # number of tests in this suite
    points = 3  # points granted by this use case if all tests pass

    def setUp(self):
        self.user = {
            "username": "testUser1",
            "password": "123",
            "email": "user1@mail.com"
        }

        self.client.post(reverse("signup"), self.user)
        self.client.post(reverse("signin"), self.user)

    @classmethod
    def tearDownClass(cls):
        # check if test case passed or failed
        calculate_points(cls.number_of_passed_tests, cls.tests_amount, cls.points, "TREQ4.1.1")

    def test_setting_the_language_cookie(self):
        lang_code = "sv"
        response = self.client.get(reverse("changeLanguage", args=(lang_code,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.cookies[LANGUAGE_COOKIE_NAME].value, lang_code)

        lang_code = "en"
        response = self.client.get(reverse("changeLanguage", args=(lang_code,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.cookies[LANGUAGE_COOKIE_NAME].value, lang_code)

        # calculate points
        self.__class__.number_of_passed_tests += 1

    def test_persistent_language_requests(self):
        lang_code = "sv"
        response = self.client.get(reverse("changeLanguage", args=(lang_code,)))
        self.assertEqual(response.cookies[LANGUAGE_COOKIE_NAME].value, lang_code)

        # on second request in the same session the language persisted
        response = self.client.get(reverse("index"))
        self.assertEqual(response._headers['content-language'][1], lang_code)

        # calculate points
        self.__class__.number_of_passed_tests += 1

    def test_language_after_logout(self):
        lang_code_sv = "sv"
        lang_code_en = "en"

        # we set the language for the current user
        response = self.client.get(reverse("changeLanguage", args=(lang_code_sv,)))
        self.assertEqual(response._headers['content-language'][1], lang_code_sv)
        self.client.logout()

        # we change the language unlogged
        response = self.client.get(reverse("changeLanguage", args=(lang_code_en,)))
        self.assertEqual(response.cookies[LANGUAGE_COOKIE_NAME].value, lang_code_en)
        self.assertEqual(response._headers['content-language'][1], lang_code_en)

        # on second login the saved language persisted
        response = self.client.post(reverse("signin"), self.user)
        self.assertEqual(response.cookies[LANGUAGE_COOKIE_NAME].value, lang_code_sv)
        self.assertEqual(response._headers['content-language'][1], lang_code_sv)

        # calculate points
        self.__class__.number_of_passed_tests += 1


class AuctionLinkTest(TestCase):
    """Test for REQ3.5 auction link"""

    number_of_passed_tests = 0  # passed tests in this test case
    tests_amount = 3  # number of tests in this suite
    points = 3  # points granted by this use case if all tests pass

    def setUp(self):
        self.pattern = re.compile(r'href="(\S+)"')

        self.item1 = {
            "title": "item1",
            "description": "something",
            "minimum_price": 10,
            "deadline_date": (timezone.now() + timezone.timedelta(days=5)).strftime("%d.%m.%Y %H:%M:%S")
        }

        user = {
            "username": "testUser1",
            "password": "123",
            "email": "user1@mail.com"
        }

        self.client.post(reverse("signup"), user)
        self.client.post(reverse("signin"), user)

    @classmethod
    def tearDownClass(cls):
        # check if test case passed or failed
        calculate_points(cls.number_of_passed_tests, cls.tests_amount, cls.points, "TREQ4.1.2")

    def test_existence_of_link(self):
        response = self.client.post(reverse("auction:create"), self.item1, follow=True)
        self.assertEqual(response.redirect_chain[0][1], 302)  # check redirect
        self.assertEqual(len(mail.outbox), 1)
        message = self.pattern.findall(str(mail.outbox[0].message()))
        self.assertEqual(len(message), 1)
        self.assertTrue("auction/edit" in message[0])

        # calculate points
        self.__class__.number_of_passed_tests += 1

    def test_email_link_get(self):
        self.client.post(reverse("auction:create"), self.item1, follow=True)
        email_link = self.pattern.findall(str(mail.outbox[0].message()))[0]

        response = self.client.get(email_link[10:], follow=True)
        self.assertEqual(response.status_code, 200)

        # calculate points
        self.__class__.number_of_passed_tests += 1

    def test_email_link_post(self):
        data = {
            "title": "item1",
            "description": "new content"
        }

        self.client.post(reverse("auction:create"), self.item1, follow=True)
        email_link = self.pattern.findall(str(mail.outbox[0].message()))[0]

        response = self.client.post(email_link[10:], data, follow=True)
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertContains(response, b"Auction has been updated successfully")

        # calculate points
        self.__class__.number_of_passed_tests += 1


def calculate_points(number_of_passed_tests, amount_of_tests, points_of_the_use_case, use_case_name):
    if number_of_passed_tests < amount_of_tests:
        print("{} fails!".format(use_case_name))
    else:
        global current_points
        current_points += points_of_the_use_case
        message = "{} passed, {} points, Current points: {}/6".format(use_case_name, points_of_the_use_case,
                                                                      current_points)
        print(message)
