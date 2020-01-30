from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer


@api_view(['GET', 'POST'])
def questions(request):
    if request.method == 'GET':
        questions = Question.objects.all()
        serializer = QuestionSerializer(snippets, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        if request.user.profile != request.data['owner']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def question_answers(request, question_id):
    if request.method == 'GET':
        question = Question.objects.get(id=question_id)
        serializer = AnswerSerializer(question.answers, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        if request.user.profile != request.data['owner']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
