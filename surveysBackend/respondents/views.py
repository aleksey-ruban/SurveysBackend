from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework import status

from creators.models import Survey, Question, Option
from creators.serializers import SurveySerializer
from accounts.models import User
from .models import SurveyResponse, QuestionResponse, OptionResponse
from django.db import transaction


class SurveyDetailWithCompletionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        if user.role != User.Roles.RESPONDENT:
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

        survey = get_object_or_404(Survey, id=pk)
        serializer = SurveySerializer(survey)

        is_completed = SurveyResponse.objects.filter(user=user, survey=survey).exists()

        return Response({
            'survey': serializer.data,
            'isCompleted': is_completed
        }, status=200)


class SubmitSurveyResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role != User.Roles.RESPONDENT:
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        print(data)

        survey_id = data.get('survey_id')
        answers = data.get('answers')
        user_contact = data.get('user_contact', '')

        if not survey_id or not answers:
            return Response({"error": "surveyId and answers are required"}, status=400)

        survey = get_object_or_404(Survey, id=survey_id)

        if SurveyResponse.objects.filter(user=user, survey=survey).exists():
            return Response({"error": "Survey already completed"}, status=400)

        with transaction.atomic():
            survey_response = SurveyResponse.objects.create(
                user=user,
                survey=survey,
                user_contact=user_contact
            )

            for answer_data in answers:
                question_id = answer_data.get("id")
                answer = answer_data.get("answer")
                question = get_object_or_404(Question, id=question_id, survey=survey)

                question_response = QuestionResponse.objects.create(
                    response=survey_response,
                    question=question
                )

                if question.type == Question.QuestionType.TEXT:
                    question_response.answer_text = answer.get("answer")

                elif question.type == Question.QuestionType.SINGLE_CHOICE:
                    option_id = answer.get("option", {}).get("id")
                    if option_id:
                        option = get_object_or_404(Option, id=option_id)
                        OptionResponse.objects.create(
                            question=question_response,
                            option=option
                        )

                elif question.type == Question.QuestionType.MULTIPLE_CHOICE:
                    options = answer.get("options", [])
                    for opt in options:
                        option_id = opt.get("id")
                        if option_id:
                            option = get_object_or_404(Option, id=option_id)
                            OptionResponse.objects.create(
                                question=question_response,
                                option=option
                            )

                elif question.type == Question.QuestionType.RATING:
                    question_response.scale = answer.get("scale")

                question_response.save()

        return Response({"message": "Survey response submitted"}, status=status.HTTP_201_CREATED)


class SurveysForUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != User.Roles.RESPONDENT:
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

        survey_ids = SurveyResponse.objects.filter(user=user).values_list('survey_id', flat=True)
        surveys = Survey.objects.filter(id__in=survey_ids)

        serializer = SurveySerializer(surveys, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)