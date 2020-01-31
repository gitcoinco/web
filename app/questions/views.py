from django.shortcuts import render
from django.template.response import TemplateResponse
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Question, Answer, QuestionSerializer, AnswerSerializer
from django.http import Http404, JsonResponse

import json

@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def questions(request):
    if request.method == 'GET':
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        if request.user.profile != request.POST.get('owner'):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def question_answers(request, question_id):
    print('received query')
    if request.method == 'GET':
        question = Question.objects.get(id=question_id)
        serializer = AnswerSerializer(question.answers, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = json.loads(request.body)
        for k in ['owner', 'text', 'question_id']:
            if not data.get(k):
                print('key {} not found or empty: {}'.format(k, data.get(k)))
                return JsonResponse({'error': 'missing data'}, status=400)
        Answer.objects.create(owner_id=data.get('owner'),
                              text=data.get('text'),
                              question_id=data.get('question_id'))
        return JsonResponse({'success': 'true'}, status=201)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

def questions_index(request):
    return TemplateResponse(request, 'questions_index.html', {})
