import os
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings
from creators.serializers import SurveySerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from accounts.models import User
from .models import Survey, Question
from respondents.models import QuestionResponse, OptionResponse


class ImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.role != User.Roles.CREATOR:
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

        file = request.FILES.get('image')

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        if user.last_uploaded_image:
            old_file_path = os.path.join(
                settings.MEDIA_ROOT, 'uploads', user.last_uploaded_image)

            if os.path.exists(old_file_path):
                os.remove(old_file_path)

        extension = file.name.split('.')[-1]
        unique_filename = f"{uuid.uuid4().hex}.{extension}"

        default_storage.save(f"uploads/{unique_filename}", file)

        user.last_uploaded_image = unique_filename
        user.save()

        return Response({"imageUrl": unique_filename}, status=status.HTTP_201_CREATED)


class SurveyCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role != User.Roles.CREATOR:
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

        serializer = SurveySerializer(data=request.data)
        if serializer.is_valid():
            survey = serializer.save(creator=request.user)
            user = request.user
            user.last_uploaded_image = None
            user.save()
            return Response(SurveySerializer(survey).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SurveyResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        if user.role != User.Roles.CREATOR:
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

        survey = get_object_or_404(Survey, id=pk)

        if survey.creator != user:
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

        survey_data = {
            "id": survey.id,
            "title": survey.title,
            "description": survey.description,
            "isAnonymous": survey.is_anonymous,
            "userContact": survey.user_contact,
            "isClosed": survey.is_closed,
            "imageUrl": survey.image_url,
            "questions": []
        }

        for question in survey.questions.order_by('position'):
            responses = QuestionResponse.objects.filter(question=question)

            question_data = {
                "id": question.id,
                "type": question.type,
                "questionText": question.question_text,
                "required": question.required,
                "responses": None
            }

            if question.type == Question.QuestionType.TEXT:
                answers = responses.exclude(answer_text__isnull=True).values_list("answer_text", flat=True)
                question_data["responses"] = {
                    "type": question.type,
                    "answers": list(answers)
                }

            elif question.type == Question.QuestionType.SINGLE_CHOICE:
                options = question.options.all()
                option_counts = []
                for option in options:
                    count = OptionResponse.objects.filter(
                        question__in=responses, option=option
                    ).count()
                    option_counts.append({
                        "option": option.text,
                        "count": count
                    })
                question_data["responses"] = {
                    "type": question.type,
                    "options": option_counts
                }

            elif question.type == Question.QuestionType.MULTIPLE_CHOICE:
                options = question.options.all()
                option_counts = []
                for option in options:
                    count = OptionResponse.objects.filter(
                        question__in=responses, option=option
                    ).count()
                    option_counts.append({
                        "option": option.text,
                        "count": count
                    })
                question_data["responses"] = {
                    "type": question.type,
                    "options": option_counts
                }

            elif question.type == Question.QuestionType.RATING:
                scales = responses.exclude(scale__isnull=True).values_list("scale", flat=True)
                ratings = list(scales)
                ratings_count = len(ratings)
                avg_rating = sum(ratings) / ratings_count if ratings_count > 0 else 0
                question_data["responses"] = {
                    "type": question.type,
                    "scale": question.scale or 10,
                    "averageRating": avg_rating,
                    "ratingsCount": ratings_count
                }

            survey_data["questions"].append(question_data)

        return Response(survey_data)


class ToggleSurveyStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):

        user = request.user
        if user.role != User.Roles.CREATOR:
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

        survey = get_object_or_404(Survey, id=pk)

        if user != survey.creator:
            return Response({'detail': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

        survey.is_closed = not survey.is_closed
        survey.save()

        return Response({
            'id': survey.id,
            'isClosed': survey.is_closed
        }, status=status.HTTP_200_OK)


class SurveyDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk)
        user = request.user

        if user.role != User.Roles.CREATOR or user != survey.creator:
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

        if survey.image_url:
            old_file_path = os.path.join(
                settings.MEDIA_ROOT, 'uploads', survey.image_url)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

        survey.delete()
        return Response({'detail': 'Опрос удален'}, status=status.HTTP_204_NO_CONTENT)