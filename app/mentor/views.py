from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from .models import Mentor, MentorSerializer


def mentors(request):
    return TemplateResponse(request, 'mentors.html')


def mentors_fetch(request):
    page = request.GET.get('page', 1)
    size = request.GET.get('size', 10)
    mentors = Mentor.objects.filter(available=True)
    paginator = Paginator(mentors, size)
    try:
        mentors = paginator.page(page)
    except PageNotAnInteger:
        mentors = paginator.page(1)
    except EmptyPage:
        return JsonResponse([])

    mentors_data = []
    for mentor in mentors:
        mentor_data = MentorSerializer(mentor).data
        mentors_data.append(mentor_data)

    return JsonResponse({
        'total_pages': mentors.paginator.num_pages,
        'mentors': mentors_data,
        'success': True
     })


def mentor(request):
    profile = request.user.profile if request.user.is_authenticated else False
    if not profile:
        return handle_not_logged(request)
    mentor = Mentor.objects.filter(profile=profile).first()
    if mentor:
        return redirect_to_mentor(mentor.id)
    if request.method == 'POST':
        mentor = mentor_from_request(request)
        mentor.save(force_insert=True)
        return redirect_to_mentor(mentor.id)
    else:
        mentor = Mentor.objects.filter(profile=profile).first()
    context = {'mentor': mentor, 'time_range_choices': Mentor.TIME_RANGE}
    return TemplateResponse(request, 'mentor.html', context)


def show_mentor(request, mentor_id):
    is_logged_in = bool(request.user.is_authenticated)
    if not is_logged_in:
        return handle_not_logged()
    if request.method == 'POST':
        mentor = mentor_from_request(request)
        mentor.pk = mentor_id
        mentor.save()
    else:
        mentor = Mentor.objects.get(pk=mentor_id)
    context = {'mentor': mentor, 'time_range_choices': Mentor.TIME_RANGE}
    return TemplateResponse(request, 'mentor.html', context)


def handle_not_logged(request):
    return redirect(f'/login/github?next={request.get_full_path()}')


def redirect_to_mentor(mentor_id):
    return HttpResponseRedirect(f"{mentor_id}/profile")


def mentor_from_request(request):
    profile = request.user.profile if request.user.is_authenticated else False
    name = request.POST.get('name')
    email = request.POST.get('email')
    org = request.POST.get('org')
    experience = request.POST.get('experience')
    about = request.POST.get('about')
    skills_offered = request.POST.get('skills_offered').split(',')
    skills_needed = request.POST.get('skills_needed').split(',')
    commitment = request.POST.get('commitment')
    avail_now = bool(request.POST.get('avail_now'))
    return Mentor(profile_id=profile.pk, name=name, email=email, org=org, about=about,
                  experience=experience, skills_needed=skills_needed, skills_offered=skills_offered,
                  available=avail_now, commitment_per_week=commitment)
