from django.urls import resolve, reverse

from dashboard.models import Profile
from rest_framework.test import APIRequestFactory
from test_plus.test import TestCase

from .models import MentorSerializer, StringArrayField
from .views import MentorDetail, MentorsList


class StringArrayFieldTest(TestCase):


    @staticmethod
    def test_string_array_field_to_internal_value():
        field = StringArrayField()
        internal_value = field.to_internal_value("Java, Python, Django")
        assert internal_value[0] == "Java"
        assert internal_value[1] == "Python"
        assert internal_value[2] == "Django"


    @staticmethod
    def test_string_array_field_to_representation():
        field = StringArrayField()
        assert field.to_representation(["Java", "Python", "Django"]) == "Java, Python, Django"


class MentorsListTest(TestCase):


    @staticmethod
    def test_get_by_term_1_mentor():
        profile = Profile.objects.create(email="test@test.com", org="Gitcoin", about="Gitting coins..",
                               experience="15_20", skills_offered=["Python", "Django"],
                               skills_needed=["Solidity", "Ethereum"], available=True,
                               commitment_per_week="5_10", data={})
        factory = APIRequestFactory()
        view = MentorsList.as_view()
        url = reverse('mentor_fetch')
        request = factory.get(url, {'page':1, 'size':10,'term':"Python Django"})
        response = view(request)

        assert response.data['total_pages'] == 1
        assert response.data['mentors'] == [MentorSerializer(profile).data]

        request = factory.get(url, {'page':1, 'size':10,'term':"Gitcoin"})
        response = view(request)

        assert response.data['total_pages'] == 1
        assert response.data['mentors'] == [MentorSerializer(profile).data]



    @staticmethod
    def test_get_by_term_0_mentor():
        profile = Profile.objects.create(email="test@test.com", org="Gitcoin", about="Gitting coins..",
                               experience="15_20", skills_offered=["Python", "Django"],
                               skills_needed=["Solidity", "Ethereum"], available=True,
                               commitment_per_week="5_10", data={})
        factory = APIRequestFactory()
        view = MentorsList.as_view()
        url = reverse('mentor_fetch')
        request = factory.get(url, {'page':1, 'size':10,'term':"Java"})
        response = view(request)

        assert response.data['total_pages'] == 1
        assert response.data['mentors'] == []


    @staticmethod
    def test_get_by_term_and_exeprience_1_mentor():
        profile = Profile.objects.create(email="test@test.com", org="Gitcoin", about="Gitting coins..",
                               experience="15_20", skills_offered=["Python", "Django"],
                               skills_needed=["Solidity", "Ethereum"], available=True,
                               commitment_per_week="5_10", data={})
        factory = APIRequestFactory()
        view = MentorsList.as_view()
        url = reverse('mentor_fetch')
        request = factory.get(url, {'page':1, 'size':10,'term':"Python",'exp':'15_20,1_5'})
        response = view(request)

        assert response.data['total_pages'] == 1
        assert response.data['mentors'] == [MentorSerializer(profile).data]

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
        print(url)
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
        profile = Profile.objects.create(email="test@test.com", org="Gitcoin", about="Gitting coins..",
                               experience="15_20", skills_offered=["Python", "Django"],
                               skills_needed=["Solidity", "Ethereum"], available=True,
                               commitment_per_week="5_10", data={})
        factory = APIRequestFactory()
        view = MentorDetail.as_view()
        url = reverse('mentor_details', kwargs={'pk':profile.id})
        request = factory.post(url, {"org": "Slack"})
        response = view(request, profile.id)
        assert response.status_code == 200

class UrlsTest(TestCase):


    def test_mentor_list_reverse(self):
        self.assertEqual(reverse('mentor_list'), '/mentor/')

    def test_mentor_list_resolve(self):
        self.assertEqual(resolve('/mentor/').view_name, 'mentor_list')

    def test_mentor_fetch_reverse(self):
        self.assertEqual(reverse('mentor_fetch'), '/mentor/fetch')

    def test_mentor_fetch_resolve(self):
        self.assertEqual(resolve('/mentor/fetch').view_name, 'mentor_fetch')

    def test_mentor_details_reverse(self):
        self.assertEqual(reverse('mentor_details', args=[1]), '/mentor/1')

    def test_mentor_details_resolve(self):
        self.assertEqual(resolve('/mentor/1').view_name, 'mentor_details')
