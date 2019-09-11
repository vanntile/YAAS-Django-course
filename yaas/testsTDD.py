from django.test import TestCase
from django.contrib import auth
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from freezegun import freeze_time

current_points = 0


class ExampleTest(TestCase):
    def setUp(self):
        # setUp run before every test method
        pass

    def test_something_that_will_pass(self):
        self.assertTrue(True)


class SignUpTests(TestCase):
    """UC1: create user"""

    number_of_passed_tests = 0  # passed tests in this test case
    tests_amount = 3  # number of tests in this suite
    points = 1  # points granted by this use case if all tests pass

    def test_sign_up_with_invalid_data(self):
        """
        Sign up without a password, should return status code 200
        """
        context = {
            "username": "testUser3",
        }

        try:
            response = self.client.post(reverse("signup"), context)
            self.assertEqual(response.status_code, 200)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC1")
        except Exception:
            print("UC1 fails!")

    def test_sign_up_with_valid_data(self):
        """
        Sign up with valid username and password, should return status code 302
        """
        context = {
            "username": "testUser3",
            "password": "333"
        }

        try:
            response = self.client.post(reverse("signup"), context)
            self.assertEqual(response.status_code, 302)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC1")
        except Exception:
            print("UC1 fails!")

    def test_sign_up_with_invalid_username(self):
        """
        Sign up with already taken username, should return status code 400.
        """
        context = {
            "username": "testUser1",
            "password": "333"
        }

        try:
            response1 = self.client.post(reverse("signup"), context)
            # create another user with the same username
            response2 = self.client.post(reverse("signup"), context)
            self.assertEqual(response2.status_code, 400)
            self.assertIn(b"This username has been taken", response2.content)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC1")
        except Exception:
            print("UC1 fails!")


class SignInTests(TestCase):
    def setUp(self):
        userInfo = {
            "username": "testUser1",
            "password": "123"
        }
        # create a user for testing
        self.client.post(reverse("signup"), userInfo)
        self.client.logout()  # because the signup function would signin the user

    def test_sign_in_with_valid_data(self):
        """
        Sign in with valid data, should return a authenticated user
        """
        userInfo = {
            "username": "testUser1",
            "password": "123"
        }

        try:
            self.client.post(reverse("signin"), userInfo)
            user = auth.get_user(self.client)
            self.assertTrue(user.is_authenticated)
        except Exception:
            print("Sign In fails!")

    def test_sign_in_with_invalid_data(self):
        """
        Sign in with invalid data, return an unauthenticated user
        """
        userInfo = {
            "username": "testUser2",
            "password": "321"
        }

        try:
            self.client.post(reverse("signin"), userInfo)
            user = auth.get_user(self.client)
            self.assertFalse(user.is_authenticated)
        except Exception:
            print("Sign In fails!")


class EditProfileTests(TestCase):
    """UC2: edit user"""

    number_of_passed_tests = 0  # passed tests in this test case
    tests_amount = 4  # number of tests in this suite
    points = 1  # points granted by this use case if all tests pass

    def setUp(self):
        user1Info = {
            "username": "testUser1",
            "password": "123",
        }
        user2Info = {
            "username": "testUser2",
            "password": "321",
        }
        # create a user for testing
        self.client.post(reverse("signup"), user1Info)
        self.client.post(reverse("signup"), user2Info)
        self.client.logout()

    def test_get_profile_of_unauthenticated_user(self):
        """
        Get detail of unauthenticated user, return code 302 and redirect to signin page
        """
        try:
            response = self.client.get(reverse("user:editprofile"))
            self.assertEqual(response.status_code, 302)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC2")
        except Exception:
            print("UC2 fails!")

    def test_get_profile_of_authenticated_user(self):
        """
        Get detail of authenticated user, return code 200 authorized
        """
        user1Info = {
            "username": "testUser1",
            "password": "123"
        }
        self.client.post(reverse("signin"), user1Info)

        try:
            response = self.client.get(reverse("user:editprofile"))
            self.assertEqual(response.status_code, 200)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC2")
        except Exception:
            print("UC2 fails!")

    def test_edit_email_and_password_of_an_authenticated_user(self):
        """
        Edit email and password of an authenticated user, the user should have a new email and password
        """
        user1Info = {
            "username": "testUser1",
            "password": "123"
        }
        data = {
            "email": "newemail@dot.com",
            "password": "newpassword",
        }
        self.client.post(reverse("signin"), user1Info)

        try:
            self.client.post(reverse("user:editprofile"), data)
            user = auth.get_user(self.client)
            self.assertEqual(user.email, "newemail@dot.com")

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC2")
        except Exception:
            print("UC2 fails!")

    def test_edit_email_that_already_taken(self):
        """
        Edit email of an authenticated user to the one that already taken, email stays the same
        """
        user1Info = {
            "username": "testUser1",
            "password": "123"
        }
        data1 = {
            "email": "email@yaas.com"
        }

        user2Info = {
            "username": "testUser2",
            "password": "321"
        }
        data2 = {
            "email": "email2@yaas.com"
        }

        # login and create email for user1
        self.client.post(reverse("signin"), user1Info)
        self.client.post(reverse("user:editprofile"), data1)
        # login and create email for user2
        self.client.post(reverse("signin"), user2Info)
        self.client.post(reverse("user:editprofile"), data2)
        # login and edit email of user1 to the email of user2
        self.client.post(reverse("signin"), user1Info)
        self.client.post(reverse("user:editprofile"), data2)

        # get user1 and check if its email still stays the same
        user1 = auth.get_user(self.client)
        try:
            self.assertEqual(user1.email, "email@yaas.com")  # stays the same as old email

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC2")
        except Exception:
            print("UC2 fails!")


class CreateAuctionTests(TestCase):
    """UC3: create auction"""

    number_of_passed_tests = 0  # passed tests in this test case
    tests_amount = 4  # number of tests in this suite
    points = 1  # points granted by this use case if all tests pass

    def setUp(self):
        userInfo = {
            "username": "testUser1",
            "password": "123"
        }
        # create a user for testing
        self.client.post(reverse("signup"), userInfo)
        self.client.logout()  # because the signup function would signin the user

    def test_create_auction_with_unauthenticated_user(self):
        """
        Create an auction with an unauthenticated user, should return a redirection status.
        """
        try:
            response = self.client.post(reverse("auction:create"))
            self.assertEqual(response.status_code, 302)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC3")
        except Exception:
            print("UC3 fails!")

    def test_create_auction_with_invalid_deadline_date(self):
        """
        Create auction with deadline date is earlier than current date, show error message
        """
        userInfo = {
            "username": "testUser1",
            "password": "123"
        }

        data = {
            "title": "newItem",
            "description": "something",
            "minimum_price": 10,
            "deadline_date": (timezone.now() - timezone.timedelta(hours=24)).strftime("%d.%m.%Y %H:%M:%S")  # 1 day ago
        }

        self.client.post(reverse("signin"), userInfo)
        try:
            response = self.client.post(reverse("auction:create"), data, follow=True)
            self.assertIn(b"The deadline date should be at least 72 hours from now", response.content)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC3")
        except Exception:
            print("UC3 fails!")

    def test_create_auction_with_invalid_minimum_price(self):
        """
        Create auction with invalid minimum price, the auction should not be created, response contains error message
        """
        userInfo = {
            "username": "testUser1",
            "password": "123"
        }

        data = {
            "title": "newItem",
            "description": "something",
            "minimum_price": 0,
            "deadline_date": (timezone.now() + timezone.timedelta(days=5)).strftime("%d.%m.%Y %H:%M:%S")
        }

        self.client.post(reverse("signin"), userInfo)
        try:
            response = self.client.post(reverse("auction:create"), data, follow=True)
            self.assertIn(b"0.01", response.content)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC3")
        except Exception:
            print("UC3 fails!")

    def test_create_auction_with_valid_data(self):
        """
        Create auction with valid data, show success message.
        """
        userInfo = {
            "username": "testUser1",
            "password": "123"
        }

        data = {
            "title": "newItem",
            "description": "something",
            "minimum_price": 10,
            "deadline_date": (timezone.now() + timezone.timedelta(days=5)).strftime("%d.%m.%Y %H:%M:%S")
        }
        self.client.post(reverse("signin"), userInfo)
        try:
            response = self.client.post(reverse("auction:create"), data, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, b"Auction has been created successfully")

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC3")
        except Exception:
            print("UC3 fails!")


class EditAuctionTests(TestCase):
    """UC4: edit auction description"""

    number_of_passed_tests = 0  # passed tests in this test case
    tests_amount = 4  # number of tests in this suite
    points = 2  # points granted by this use case if all tests pass

    def setUp(self):
        userInfo = {
            "username": "testUser1",
            "password": "123"
        }

        data = {
            "title": "item1",
            "description": "something",
            "minimum_price": 10,
            "deadline_date": (timezone.now() + timezone.timedelta(days=5)).strftime("%d.%m.%Y %H:%M:%S")
        }
        # create a user and an auction
        self.client.post(reverse("signup"), userInfo)
        self.client.post(reverse("signin"), userInfo)
        self.client.post(reverse("auction:create"), data)
        self.auction_id = 1
        self.client.logout()

    def test_get_an_auction_of_other_user(self):
        """
        Get an auction of other user, show the error message
        """
        user2Info = {
            "username": "testUser2",
            "password": "321"
        }

        data = {
            "description": "new content"
        }

        # login to user2 account
        self.client.post(reverse("signup"), user2Info)
        self.client.post(reverse("signin"), user2Info)
        try:
            response = self.client.get(reverse("auction:edit", args=(self.auction_id,)), data, follow=True)
            self.assertIn(b"That is not your auction", response.content)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC4")
        except Exception:
            print("UC4 fails!")

    def test_get_an_auction_successfully(self):
        """
        An user gets his auction successfully,
        """
        userInfo = {
            "username": "testUser1",
            "password": "123"
        }

        data = {
            "title": "item1",
            "description": "new content"
        }

        self.client.post(reverse("signin"), userInfo)
        try:
            response = self.client.get(reverse("auction:edit", args=(self.auction_id,)), data, follow=True)
            self.assertEqual(response.status_code, 200)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC4")
        except Exception:
            print("UC4 fails!")

    def test_edit_an_auction_of_other_user(self):
        """
        Get an auction of other user, show the error message
        """
        user2Info = {
            "username": "testUser2",
            "password": "321"
        }

        data = {
            "description": "new content"
        }

        # login to user2 account
        self.client.post(reverse("signup"), user2Info)
        self.client.post(reverse("signin"), user2Info)
        try:
            response = self.client.post(reverse("auction:edit", args=(self.auction_id,)), data, follow=True)
            self.assertIn(b"That is not your auction", response.content)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC4")
        except Exception:
            print("UC4 fails!")

    def test_edit_auction_with_valid_description(self):
        """
        Edit an auction with valid description, response contains success message
        """
        userInfo = {
            "username": "testUser1",
            "password": "123"
        }

        data = {
            "title": "item1",
            "description": "new content"
        }

        self.client.post(reverse("signin"), userInfo)
        try:
            response = self.client.post(reverse("auction:edit", args=(self.auction_id,)), data, follow=True)
            self.assertIn(b"Auction updated successfully", response.content)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC4")
        except Exception:
            print("UC4 fails!")


class BrowseAndSearchTests(TestCase):
    """UC5: browse and search auctions"""

    number_of_passed_tests = 0  # passed tests in this test case
    tests_amount = 2  # number of tests in this suite
    points = 1  # points granted by this use case if all tests pass

    def setUp(self):
        userInfo = {
            "username": "testUser1",
            "password": "123"
        }

        data = {
            "title": "item1",
            "description": "something",
            "minimum_price": 10,
            "deadline_date": (timezone.now() + timezone.timedelta(days=5)).strftime("%d.%m.%Y %H:%M:%S")
        }
        # create a user and an auction
        self.client.post(reverse("signup"), userInfo)
        self.client.post(reverse("signin"), userInfo)
        self.client.post(reverse("auction:create"), data)
        self.client.logout()

    def test_browse_for_active_auctions(self):
        """
        Test browse for active auctions, should return a list of active auctions
        """
        try:
            response = self.client.get(reverse("auction:index"))
            self.assertIsNotNone(response.context["auctions"])

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC5")
        except Exception:
            print("UC5 fails!")

    def test_search_for_auctions_by_title(self):
        """
        Test search for auctions by a title, should return a list of auctions which titles contain the term
        """
        args = {
            "term": "item1"
        }
        try:
            response = self.client.get(reverse("auction:search"), args)
            self.assertIsNotNone(response.context["auctions"])

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC5")
        except Exception:
            print("UC5 fails!")


class BidAuctionTests(TestCase):
    """UC6: bid"""

    number_of_passed_tests = 0  # passed tests in this test case
    tests_amount = 5  # number of tests in this suite
    points = 3  # points granted by this use case if all tests pass

    def setUp(self):
        user1Info = {
            "username": "testUser1",
            "password": "123"
        }

        adminInfo = {
            "username": "admin",
            "password": "admin"
        }

        activeItemInfo = {
            "title": "item1",
            "description": "something",
            "minimum_price": 10,
            "deadline_date": (timezone.now() + timezone.timedelta(days=5)).strftime("%d.%m.%Y %H:%M:%S")
        }
        bannedItemInfo = {
            "title": "item2",
            "description": "something",
            "minimum_price": 15,
            "deadline_date": (timezone.now() + timezone.timedelta(days=8)).strftime("%d.%m.%Y %H:%M:%S")
        }

        # create a user and an auction
        self.client.post(reverse("signup"), user1Info)
        self.client.post(reverse("signin"), user1Info)
        self.client.post(reverse("auction:create"), activeItemInfo)
        self.client.post(reverse("auction:create"), bannedItemInfo)
        # create an admin user
        self.client.post(reverse("signup"), adminInfo)
        self.client.post(reverse("signin"), adminInfo)
        try:
            adm = auth.get_user(self.client)
            adm.is_superuser = True
            adm.save()
        except NotImplementedError:
            print("UC6 fails!!")

        # common variables
        self.active_item_id = 1
        self.banned_item_id = 2

        # ban 1 item
        try:
            self.client.post(reverse("auction:ban", args=(self.banned_item_id,)))
        except ValueError:
            print("UC6 fails!!!")

        self.client.logout()

    def test_bid_by_its_seller(self):
        """
        A seller bid on own auction, response contains error message
        """
        user1Info = {
            "username": "testUser1",
            "password": "123"
        }
        # signup and signin to other user to bid
        self.client.post(reverse("signup"), user1Info)
        self.client.post(reverse("signin"), user1Info)

        bidInfo = {
            "newBid": 12
        }

        try:
            response = self.client.post(reverse("auction:bid", args=(self.active_item_id,)), bidInfo, follow=True)
            self.assertIn(b"A seller cannot bid on own auctions", response.content)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC6")
        except Exception:
            print("UC6 fails!")

    def test_bid_by_unauthenticated_user(self):
        """
        Unauthenticated user bid on an auction, return code 302 redirect
        """

        bidInfo = {
            "newBid": 12
        }

        try:
            response = self.client.post(reverse("auction:bid", args=(self.active_item_id,)), bidInfo)
            self.assertEqual(response.status_code, 302)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC6")
        except Exception:
            print("UC6 fails!")

    def test_bid_on_inactive_auction(self):
        """
        Bid on an inactive auction, bid value does not change, return error message
        """
        user2Info = {
            "username": "testUser2",
            "password": "321"
        }
        # signup and signin to other user to bid
        self.client.post(reverse("signup"), user2Info)
        self.client.post(reverse("signin"), user2Info)
        try:
            response = self.client.post(reverse("auction:bid", args=(self.banned_item_id,)), follow=True)
            self.assertIn(b"You can only bid on active auction", response.content)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC6")
        except Exception:
            print("UC6 fails!")

    def test_bid_with_invalid_amount(self):
        """
        Bid on an auction with invalid amount, should return error message
        """
        user2Info = {
            "username": "testUser2",
            "password": "321"
        }
        # signup and signin to other user to bid
        self.client.post(reverse("signup"), user2Info)
        self.client.post(reverse("signin"), user2Info)

        bidInfo = {
            "newBid": 9
        }

        try:
            response = self.client.post(reverse("auction:bid", args=(self.active_item_id,)), bidInfo, follow=True)
            self.assertIn(b"New bid must be greater than the current bid for at least 0.01", response.content)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC6")
        except Exception:
            print("UC6 fails!")

    def test_bid_with_valid_data(self):
        """
        Bid on an auction with valid data, response contains success message
        """
        user2Info = {
            "username": "testUser2",
            "password": "321"
        }
        # signup and signin to other user to bid
        self.client.post(reverse("signup"), user2Info)
        self.client.post(reverse("signin"), user2Info)

        bidInfo = {
            "newBid": 12
        }

        try:
            response = self.client.post(reverse("auction:bid", args=(self.active_item_id,)), bidInfo, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, b"You has bid successfully for the auction")

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC6")
        except Exception:
            print("UC6 fails!")


class BanAuctionTests(TestCase):
    """UC7: ban auction"""

    number_of_passed_tests = 0  # passed tests in this test case
    tests_amount = 2  # number of tests in this suite
    points = 1  # points granted by this use case if all tests pass

    def setUp(self):
        userInfo = {
            "username": "testUser1",
            "password": "123"
        }

        adminInfo = {
            "username": "admin",
            "password": "admin"
        }

        data = {
            "title": "item1",
            "description": "something",
            "minimum_price": 10,
            "deadline_date": (timezone.now() + timezone.timedelta(days=5)).strftime("%d.%m.%Y %H:%M:%S")
        }
        # create a user and an auction
        self.client.post(reverse("signup"), userInfo)
        self.client.post(reverse("signin"), userInfo)
        self.client.post(reverse("auction:create"), data)
        # create an admin user
        self.client.post(reverse("signup"), adminInfo)
        self.client.post(reverse("signin"), adminInfo)
        try:
            adm = auth.get_user(self.client)
            adm.is_superuser = True
            adm.save()
        except NotImplementedError:
            print("UC7 fails")

        self.client.logout()

    def test_normal_user_ban_auction(self):
        """
        Normal user bans an auction, auction should remain
        """
        userInfo = {
            "username": "testUser1",
            "password": "123"
        }
        self.client.post(reverse("signin"), userInfo)
        try:
            self.client.post(reverse("auction:ban", args=(1,)))
            # get a list of active auctions, the testing auction should be in the list
            response = self.client.get(reverse("auction:index"))
            self.assertEqual(len(response.context["auctions"]), 1)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC7")
        except Exception:
            print("UC7 fails!")

    def test_admin_ban_auction(self):
        """
        Admin user bans an auction, auction should be banned
        """
        adminInfo = {
            "username": "admin",
            "password": "admin"
        }
        self.client.post(reverse("signin"), adminInfo)
        try:
            self.client.post(reverse("auction:ban", args=(1,)))
            # get a list of active auctions, the testing auction should not be in the list
            response = self.client.get(reverse("auction:index"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context["auctions"]), 0)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC7")
        except Exception:
            print("UC7 fails!")


class ResolveAuctionTests(TestCase):
    """UC8: Resolve auction"""

    number_of_passed_tests = 0  # passed tests in this test case
    tests_amount = 1  # number of tests in this suite
    points = 2  # points granted by this use case if all tests pass

    def setUp(self):
        self.user1Info = {
            "username": "testUser1",
            "password": "123"
        }

        self.user2Info = {
            "username": "testUser2",
            "password": "321"
        }

        # create user1 and use it to create 2 auctions
        self.client.post(reverse("signup"), self.user1Info)
        self.client.post(reverse("signin"), self.user1Info)

        with freeze_time("2019-9-5"):
            item1Info = {
                "title": "item1",
                "description": "something",
                "minimum_price": 10,
                "deadline_date": (timezone.now() + timezone.timedelta(hours=80)).strftime("%d.%m.%Y %H:%M:%S")
            }

            item2Info = {
                "title": "item2",
                "description": "something else",
                "minimum_price": 9,
                "deadline_date": (timezone.now() + timezone.timedelta(hours=78)).strftime("%d.%m.%Y %H:%M:%S")
            }
            self.client.post(reverse("auction:create"), item1Info)
            self.client.post(reverse("auction:create"), item2Info)

        # create user2 to bid on item1
        self.client.post(reverse("signup"), self.user2Info)
        self.client.post(reverse("signin"), self.user2Info)
        try:
            with freeze_time("2019-9-6"):
                self.client.post(reverse("auction:bid", args=(1,)), {"newBid": 12}, follow=True)
        except Exception:
            print("UC8 fails!")

        self.client.logout()

    def test_resolve_auction_with_bid(self):
        """
        Resolve auctions that have bid, the len of list of active auctions should be 0
        """
        try:
            # call the resolve
            self.client.post(reverse("auction:resolve"))
            # check if the auction is not in the list of active auctions
            response = self.client.get(reverse("auction:index"))
            self.assertEqual(len(response.context["auctions"]), 0)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC8")
        except Exception:
            print("UC8 fails")


class ChangeLanguageTests(TestCase):
    """UC9: Language switching"""

    number_of_passed_tests = 0  # passed tests in this test case
    tests_amount = 2  # number of tests in this suite
    points = 2  # points granted by this use case if all tests pass

    def test_change_language_to_swedish(self):
        """
        Change language to Swedish, response contains message
        """
        lang_code = "sv"
        try:
            response = self.client.post(reverse("changeLanguage", args=(lang_code,)))
            self.assertIn(b"Language changed to Swedish", response.content)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC9")
        except Exception:
            print("UC9 fails!")

    def test_change_language_to_english(self):
        """
        Change language to Swedish, response contains message
        """
        lang_code = "en"
        try:
            response = self.client.post(reverse("changeLanguage", args=(lang_code,)))
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Language changed to English", response.content)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC9")
        except Exception:
            print("UC9 fails!")


class BidConcurrencyTests(TestCase):
    """UC10: Concurrency"""

    number_of_passed_tests = 0  # passed tests in this test case
    tests_amount = 2  # number of tests in this suite
    points = 2  # points granted by this use case if all tests pass

    def setUp(self):
        self.user1Info = {
            "username": "testUser1",
            "password": "123"
        }

        self.user2Info = {
            "username": "testUser2",
            "password": "321"
        }

        self.user3Info = {
            "username": "testUser3",
            "password": "213"
        }

        activeItemInfo = {
            "title": "item1",
            "description": "something",
            "minimum_price": 10,
            "deadline_date": (timezone.now() + timezone.timedelta(days=5)).strftime("%d.%m.%Y %H:%M:%S")
        }

        # create user1 and use it to create an auction
        self.client.post(reverse("signup"), self.user1Info)
        self.client.post(reverse("signin"), self.user1Info)
        self.client.post(reverse("auction:create"), activeItemInfo)

        # create 2 other users to test concurrent requests
        self.client.post(reverse("signup"), self.user2Info)
        self.client.post(reverse("signup"), self.user3Info)

        # common variables
        self.auction_id = 1

        self.client.logout()

    def test_bid_concurrently(self):
        """
        2 users bid on an auction concurrently, should return conflict message
        """
        try:
            # user2 bid on the auction, its bid and version have changed
            self.client.post(reverse("signin"), self.user2Info)
            response1 = self.client.post(reverse("auction:bid", args=(self.auction_id,)), {"newBid": 15})

            # user3 bid on the old version of the auction, conflict happens
            self.client.post(reverse("signin"), self.user3Info)
            response2 = self.client.post(reverse("auction:bid", args=(self.auction_id,)), {"newBid": 12})
            self.assertEqual(response1.status_code, 302)
            self.assertEqual(response2.status_code, 200)
            self.assertIn(b"The auction information has been changed", response2.content)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC10")
        except Exception:
            print("UC10 fails!")

    def test_bid_on_changed_description_auction(self):
        """
        An auction has a change in description while bidding, should return conflict message
        """
        data = {
            "title": "item1",
            "description": "new content"
        }
        try:
            self.client.post(reverse("signin"), self.user1Info)
            response1 = self.client.post(reverse("auction:edit", args=(self.auction_id,)), data)

            self.client.post(reverse("signin"), self.user2Info)
            response2 = self.client.post(reverse("auction:bid", args=(self.auction_id,)), {"newBid": 15})
            self.assertEqual(response1.status_code, 302)
            self.assertEqual(response2.status_code, 200)
            self.assertIn(b"The auction information has been changed", response2.content)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC10")
        except Exception:
            print("UC10 fails!")


class ChangeCurrencyTests(TestCase):
    """UC11: Currency exchange"""

    number_of_passed_tests = 0  # passed tests in this test case
    tests_amount = 2  # number of tests in this suite
    points = 3  # points granted by this use case if all tests pass

    def test_change_currency_to_usd(self):
        currency_code = "USD"
        try:
            response = self.client.post(reverse("changeCurrency", args=(currency_code,)), follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Currency changed to USD", response.content)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC11")
        except Exception:
            print("UC11 fails!")

    def test_change_currency_to_eur(self):
        currency_code = "EUR"
        try:
            response = self.client.post(reverse("changeCurrency", args=(currency_code,)), follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Currency changed to EUR", response.content)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "UC11")
        except Exception:
            print("UC11 fails!")


class BrowseAndSearchAuctionApiTests(TestCase):
    """WS1: Browse and Search API"""

    number_of_passed_tests = 0  # passed tests in this test case
    tests_amount = 4  # number of tests in this suite
    points = 2  # points granted by this use case if all tests pass

    def setUp(self):
        userInfo = {
            "username": "testUser1",
            "password": "123"
        }

        adminInfo = {
            "username": "admin",
            "password": "admin"
        }

        item1 = {
            "title": "item1",
            "description": "something",
            "minimum_price": 10,
            "deadline_date": (timezone.now() + timezone.timedelta(days=5)).strftime("%d.%m.%Y %H:%M:%S")
        }
        item2 = {
            "title": "item2",
            "description": "something",
            "minimum_price": 15,
            "deadline_date": (timezone.now() + timezone.timedelta(days=10)).strftime("%d.%m.%Y %H:%M:%S")
        }
        # create a user and auctions
        self.client.post(reverse("signup"), userInfo)
        self.client.post(reverse("signin"), userInfo)
        self.client.post(reverse("auction:create"), item1)
        self.client.post(reverse("auction:create"), item2)

        # create an admin user
        self.client.post(reverse("signup"), adminInfo)
        self.client.post(reverse("signin"), adminInfo)
        try:
            adm = auth.get_user(self.client)
            adm.is_superuser = True
            adm.save()
        except NotImplementedError:
            print("WS1 fails")

        # ban 1 item
        try:
            self.client.post(reverse("auction:ban", args=(2,)))
        except ValueError:
            print("WS1 fails")

        self.client.logout()

    def test_browse_active_auctions(self):
        """
        Browse for active auctions, return a list of active auctions
        """
        try:
            response = self.client.get(reverse("browseauctionsapi"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data), 1)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "WS1")
        except Exception:
            print("WS1 fails!")

    def test_search_for_auctions_by_title(self):
        """
        Search for active auctions by title, return list of active auctions that contain that title
        """
        term = "item1"

        try:
            response = self.client.get(reverse("searchauctionapi", args=(term,)))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data), 1)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "WS1")
        except Exception:
            print("WS1 fails!")

    def test_search_for_auctions_by_title_with_term(self):
        """
        Search for active auctions by title, return list of active auctions that contain that title
        """
        args = {
            "term": "item1"
        }

        try:
            response = self.client.get(reverse("searchauctionwithtermapi"), args)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data), 1)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "WS1")
        except Exception:
            print("WS1 fails!")

    def test_search_for_auctions_by_id(self):
        """
        Search for active auctions by id, return an auction of that id
        """
        term = "1"

        try:
            response = self.client.get(reverse("searchauctionbyidapi", args=(term,)))
            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(response.data)

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "WS1")
        except Exception:
            print("WS1 fails!")


class BidAuctionApiTests(TestCase):
    """WS2: bid API"""

    number_of_passed_tests = 0  # passed tests in this test case
    tests_amount = 5  # number of tests in this suite
    points = 2  # points granted by this use case if all tests pass

    def setUp(self):
        self.client = APIClient()
        # create user for testing purpose
        user1Info = {
            "username": "testUser1",
            "password": "123"
        }

        adminInfo = {
            "username": "admin",
            "password": "admin"
        }

        activeItemInfo = {
            "title": "item1",
            "description": "something",
            "minimum_price": 10,
            "deadline_date": (timezone.now() + timezone.timedelta(days=5)).strftime("%d.%m.%Y %H:%M:%S")
        }
        bannedItemInfo = {
            "title": "item2",
            "description": "something",
            "minimum_price": 15,
            "deadline_date": (timezone.now() + timezone.timedelta(days=8)).strftime("%d.%m.%Y %H:%M:%S")
        }

        # create a user and an auction
        self.client.post(reverse("signup"), user1Info)
        self.client.post(reverse("signin"), user1Info)
        self.client.post(reverse("auction:create"), activeItemInfo)
        self.client.post(reverse("auction:create"), bannedItemInfo)
        # create an admin user
        self.client.post(reverse("signup"), adminInfo)
        self.client.post(reverse("signin"), adminInfo)
        try:
            adm = auth.get_user(self.client)
            adm.is_superuser = True
            adm.save()
        except NotImplementedError:
            print("WS2 fails")

        # common variables
        self.active_item_id = 1
        self.banned_item_id = 2
        # ban 1 item
        try:
            self.client.post(reverse("auction:ban", args=(self.banned_item_id,)))
        except ValueError:
            print("WS2 fails")

        self.client.logout()

    def test_bid_on_own_auction(self):
        """
        Bid on own auction, return error code 400
        """
        user1Info = {
            "username": "testUser1",
            "password": "123"
        }
        data = {
            "bid": 12
        }
        self.client.post(reverse("signin"), user1Info)
        self.client.force_authenticate(user=auth.get_user(self.client))
        try:
            response = self.client.post(reverse("bidauctionapi", args=(self.active_item_id,)), data)
            self.assertEqual(response.status_code, 400)
            self.assertIn("Cannot bid on own auction", response.data["message"])

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "WS2")
        except Exception:
            print("WS2 fails!")

    def test_bid_on_banned_auction(self):
        """
        Bid on banned auction, return code 400
        """
        user2Info = {
            "username": "testUser2",
            "password": "321"
        }
        data = {
            "bid": 12
        }
        self.client.post(reverse("signin"), user2Info)
        self.client.post(reverse("signup"), user2Info)
        self.client.force_authenticate(user=auth.get_user(self.client))
        try:
            response = self.client.post(reverse("bidauctionapi", args=(self.banned_item_id,)), data)
            self.assertEqual(response.status_code, 400)
            self.assertIn("Can only bid on active auction", response.data["message"])

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "WS2")
        except Exception:
            print("WS2 fails!")

    def test_bid_with_invalid_amount(self):
        """
        Bid with a new bid is the same with the old bid, return code 400
        """
        user2Info = {
            "username": "testUser2",
            "password": "321"
        }
        data = {
            "bid": 10
        }
        self.client.post(reverse("signup"), user2Info)
        self.client.post(reverse("signin"), user2Info)
        self.client.force_authenticate(user=auth.get_user(self.client))
        try:
            response = self.client.post(reverse("bidauctionapi", args=(self.active_item_id,)), data)
            self.assertEqual(response.status_code, 400)
            self.assertIn("New bid must be greater than the current bid at least 0.01", response.data["message"])

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "WS2")
        except Exception:
            print("WS2 fails!")

    def test_bid_with_invalid_data(self):
        """
        Bid with invalid data, return code 400
        """
        user2Info = {
            "username": "testUser2",
            "password": "321"
        }
        data = {
            "bid": "text"
        }
        self.client.post(reverse("signup"), user2Info)
        self.client.post(reverse("signin"), user2Info)
        self.client.force_authenticate(user=auth.get_user(self.client))
        try:
            response = self.client.post(reverse("bidauctionapi", args=(self.active_item_id,)), data)
            self.assertEqual(response.status_code, 400)
            self.assertIn("Bid must be a number", response.data["message"])
            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "WS2")
        except Exception:
            print("WS2 fails!")

    def test_bid_successfully(self):
        """
        Bid on other auction successfully, return code 200
        """
        user2Info = {
            "username": "testUser2",
            "password": "321"
        }
        data = {
            "bid": 12
        }
        self.client.post(reverse("signup"), user2Info)
        self.client.post(reverse("signin"), user2Info)
        self.client.force_authenticate(user=auth.get_user(self.client))
        try:
            response = self.client.post(reverse("bidauctionapi", args=(self.active_item_id,)), data)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Bid successfully", response.data["message"])

            # calculate points
            self.__class__.number_of_passed_tests += 1
            calculate_points(self.__class__.number_of_passed_tests, self.__class__.tests_amount, self.__class__.points, "WS2")
        except Exception:
            print("WS2 fails!")


def calculate_points(number_of_passed_tests, amount_of_tests, points_of_the_use_case, use_case_name):
    global current_points
    if number_of_passed_tests == amount_of_tests:
        current_points += points_of_the_use_case
        message = "{} passed, {} points, Current points: {}/30".format(use_case_name, points_of_the_use_case, current_points)
        print(message)
