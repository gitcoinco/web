from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import resolve, reverse

from dashboard.models import Profile
from rest_framework.test import APIRequestFactory, force_authenticate
from test_plus.test import TestCase

from .commands.mentors_match import Command
from .mails import mentors_match
from .models import MentorSerializer
from .views import MentorDetail, MentorsList


class MentorsListTest(TestCase):


    @staticmethod
    def test_get_by_term_1_mentor():
        profile = Profile.objects.create(email="test@test.com", org="Gitcoin", about="Gitting coins..",
                               experience="15_20", available=True, commitment_per_week="5_10", data={})
        profile.skills_offered.add("Python")
        profile.skills_offered.add("Django")
        profile.skills_needed.add("Solidity")
        profile.skills_needed.add("Ethereum")
        factory = APIRequestFactory()
        view = MentorsList.as_view()
        url = reverse('mentor_fetch')
        request = factory.get(url, {'page':1, 'size':10,'term':"Python Django"})
        response = view(request)

        assert response.data['total_pages'] == 1
        assert len(response.data['mentors']) == 1

        request = factory.get(url, {'page':1, 'size':10,'term':"Gitcoin"})
        response = view(request)

        assert response.data['total_pages'] == 1
        assert len(response.data['mentors']) == 1



    @staticmethod
    def test_get_by_term_0_mentor():
        profile = Profile.objects.create(email="test@test.com", org="Gitcoin", about="Gitting coins..",
                               experience="15_20", available=True, commitment_per_week="5_10", data={})
        factory = APIRequestFactory()
        view = MentorsList.as_view()
        url = reverse('mentor_fetch')
        request = factory.get(url, {'page':1, 'size':10,'term':"Java"})
        response = view(request)

        assert response.data['total_pages'] == 1
        assert response.data['mentors'] == []


    @staticmethod
    def     test_get_by_term_and_exeprience_1_mentor():
        profile = Profile.objects.create(email="test@test.com", org="Gitcoin", about="Gitting coins..",
                               experience="15_20", available=True, commitment_per_week="5_10", data={})
        profile.skills_offered.add("Python")
        profile.skills_offered.add("Django")
        profile.skills_needed.add("Solidity")
        profile.skills_needed.add("Ethereum")
        factory = APIRequestFactory()
        view = MentorsList.as_view()
        url = reverse('mentor_fetch')
        request = factory.get(url, {'page':1, 'size':10,'term':"Python",'exp':'15_20,1_5'})
        response = view(request)

        assert response.data['total_pages'] == 1
        assert len(response.data['mentors']) == 1

class MentorDetailTest(TestCase):


    @staticmethod
    def test_get_200():
        profile = Profile.objects.create(email="test@test.com", org="Gitcoin", about="Gitting coins..",
                               experience="15_20", skills_offered=["Python", "Django"],
                               skills_needed=["Solidity", "Ethereum"], available=True,
                               commitment_per_week="5_10", data={})
        factory = APIRequestFactory()
        view = MentorDetail.as_view()
        url = reverse('mentor_details', kwargs={'pk':profile.id})
        request = factory.get(url)
        response = view(request, profile.id)
        assert response.status_code == 200


    @staticmethod
    def test_get_404():
        factory = APIRequestFactory()
        view = MentorDetail.as_view()
        url = reverse('mentor_details', kwargs={'pk':7776})
        request = factory.get(url)
        response = view(request, 7776)
        assert response.status_code == 404


    @staticmethod
    def test_post():
        user = User.objects.create_user(username='john',
                                 email='jlennon@beatles.com',
                                 password='glass onion')
        profile = Profile.objects.create(email="test@test.com", org="Gitcoin", about="Gitting coins..",
                               experience="15_20", skills_offered=["Python", "Django"],
                               skills_needed=["Solidity", "Ethereum"], available=True,
                               commitment_per_week="5_10", data={}, user=user)
        factory = APIRequestFactory()
        view = MentorDetail.as_view()
        url = reverse('mentor_details', kwargs={'pk':profile.id})
        request = factory.post(url, {"org": "Slack"})
        force_authenticate(request, user=user)
        response = view(request, profile.id)
        assert response.status_code == 200

class UrlsTest(TestCase):


    def test_mentor_list_reverse(self):
        self.assertEqual(reverse('mentors'), '/mentor/')

    def test_mentor_list_resolve(self):
        self.assertEqual(resolve('/mentor/').view_name, 'mentors')

    def test_mentor_fetch_reverse(self):
        self.assertEqual(reverse('mentor_fetch'), '/mentor/fetch')

    def test_mentor_fetch_resolve(self):
        self.assertEqual(resolve('/mentor/fetch').view_name, 'mentor_fetch')

    def test_mentor_details_reverse(self):
        self.assertEqual(reverse('mentor_details', args=[1]), '/mentor/1')

    def test_mentor_details_resolve(self):
        self.assertEqual(resolve('/mentor/1').view_name, 'mentor_details')


class MailsTest(TestCase):


    @staticmethod
    def test_mentors_match():
        match = Profile.objects.create(email="test@test.com", org="Gitcoin", about="Gitting coins..",
                               experience="15_20", available=True, commitment_per_week="5_10",
                               data={'name': "Reksio"})
        profile = Profile.objects.create(email="profile@test.com", org="Gitcoin", about="aint no stressin",
                               experience="15_20", available=True, commitment_per_week="5_10",
                               data={'name': "Pluto"})

        match.skills_offered.add("Python")
        match.skills_offered.add("Django")
        match.skills_needed.add("Solidity")
        match.skills_needed.add("Ethereum")
        profile.skills_offered.add("Ethereum")
        mentors_match([match], profile)


class MentorsMatchCommandTest(TestCase):


    @patch('mentor.commands.mentors_match.mentors_match')
    def test_handle(self, mock_func):
        profile = Profile.objects.create(email="test1@test.com", org="Gitcoin", about="Gitting coins..",
                               experience="15_20", available=True, commitment_per_week="5_10", data={})
        profile.skills_offered.add("Python")
        profile.skills_offered.add("Django")
        profile.skills_needed.add("Solidity")
        profile.skills_needed.add("Ethereum")
        match = Profile.objects.create(email="test2@test.com", org="Gitcoin", about="Gitting coins..",
                               experience="15_20", available=True, commitment_per_week="5_10", data={})
        match.skills_offered.add("Solidity")
        match.skills_offered.add("Django")
        match.skills_needed.add("Solidity")
        match.skills_needed.add("Ethereum")
        Command().handle()
        mock_func.assert_called_once_with([match], profile)
