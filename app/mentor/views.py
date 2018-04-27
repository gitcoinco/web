from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from dashboard.models import Profile
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MentorSerializer


class MentorsList(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        page = request.GET.get('page', 1)
        size = request.GET.get('size', 10)
        term = request.GET.get('term', None)
        exp = request.GET.get('exp', None)
        skills_filter = Q(skills_offered__overlap=term.split()) if term else ~Q(pk=None)
        org_filter = Q(org__in=term.split()) if term else ~Q(pk=None)
        exp_filter = Q(experience__in=exp.split(',')) if exp else ~Q(pk=None)
        mentors = Profile.objects.filter(Q(available=True), exp_filter, skills_filter | org_filter).order_by('id')
        paginator = Paginator(mentors, size)
        mentors = paginator.page(page)
        serializer = MentorSerializer(mentors, many=True)
        return Response({
                         'total_pages': mentors.paginator.num_pages,
                         'mentors': serializer.data,
        })


class MentorDetail(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (AllowAny,)

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'mentor.html'

    def get(self, request, pk):
        profile = get_object_or_404(Profile, pk=pk)
        print(profile)
        serializer = MentorSerializer(profile)
        return Response({'serializer': serializer, 'mentor': profile})

    def post(self, request, pk):
        profile = get_object_or_404(Profile, pk=pk)
        serializer = MentorSerializer(profile, data=request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer, 'mentor': profile})
        serializer.save()
        return Response({'serializer': serializer, 'mentor': profile})


def mentors(request):
    return TemplateResponse(request, 'mentors.html')


def handle_not_logged(request):
    # TODO: handle not logged
    return redirect(f'/login/github?next={request.get_full_path()}')
