from rest_framework import generics
from django.db.models import Q
from creators.models import Survey
from creators.serializers import SurveySerializer
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from respondents.models import SurveyResponse


class SurveyListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SurveySerializer

    def get_queryset(self):
        user = self.request.user
        search = self.request.query_params.get('search')
        status = self.request.query_params.get('status')
        sort = self.request.query_params.get('sort')
        print(search, status, sort)

        base_filter = Q()
        if user.is_authenticated and user.role == User.Roles.CREATOR:
            base_filter &= Q(creator=user)

        if user.is_authenticated and user.role == User.Roles.RESPONDENT:
            base_filter &= Q(is_closed=False)

        if status and user.is_authenticated and user.role == User.Roles.CREATOR:
            if status == 'open':
                base_filter &= Q(is_closed=False)
            elif status == 'closed':
                base_filter &= Q(is_closed=True)
        elif user.role == User.Roles.RESPONDENT:
            answered_survey_ids = SurveyResponse.objects.filter(user=user).values_list('survey_id', flat=True)
            base_filter &= ~Q(id__in=answered_survey_ids)

        if search:
            search_filter = Q(title__icontains=search) | Q(description__icontains=search)
            base_filter &= search_filter

        queryset = Survey.objects.filter(base_filter)

        if sort == 'desc':
            queryset = queryset.order_by('title')
        elif sort == 'asc':
            queryset = queryset.order_by('-created_at')

        return queryset
