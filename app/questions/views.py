from django.shortcuts import render
from django.template.response import TemplateResponse
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Question, Answer, QuestionSerializer, AnswerSerializer
from dashboard.models import Tip
from django.http import Http404, JsonResponse

import json

@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def questions(request):
    if request.method == 'GET':
        questions = Question.objects.order_by('-created_on').all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def ask_question(request):
    data = json.loads(request.body)
    for k in ['owner', 'text']:
        if not data.get(k):
            print('key {} not found or empty: {}'.format(k, data.get(k)))
            return JsonResponse({'error': 'missing data'}, status=400)
    Question.objects.create(owner_id=data.get('owner'),
                            text=data.get('text'),
                            value_in_eth=data.get('value_in_eth', 0.0))
    return JsonResponse({'success': 'true'}, status=201)


def accept_answer(request):
    data = json.loads(request.body)
    for k in ['answer_id']:
        if not data.get(k):
            print('key {} not found or empty: {}'.format(k, data.get(k)))
            return JsonResponse({'error': 'missing data'}, status=400)
    answer = Answer.objects.get(id=answer_id);
    if answer.question.owner != request.user.profile:
        return JsonResponse({'error': 'not your question'}, status=400)
    answer.is_accepted = True
    answer.save()
    return JsonResponse({'success': 'true'}, status=200)

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


def attach_tip_to_question(request, question_id):
    data = json.loads(request.body)
    for k in ['tip_txid', 'question_id']:
        if not data.get(k):
            print('key {} not found or empty: {}'.format(k, data.get(k)))
            return JsonResponse({'error': 'missing data'}, status=400)
    tip = Tip.objects.get(txid=data['tip_txid'])
    question = Question.objects.get(id=question_id)
    question.tip = tip
    question.save()
    return JsonResponse({'success': 'true'}, status=200)


def questions_index(request):
    return TemplateResponse(request, 'questions_index.html', {})
