from rest_framework import serializers
from .models import Survey, Question, Option


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text']
        extra_kwargs = {'id': {'read_only': True}}


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = [
            'id',
            'type',
            'question_text',
            'required',
            'scale',
            'options',
        ]
        extra_kwargs = {'id': {'read_only': True}}

    def validate(self, attrs):
        question_type = attrs.get('type')

        if question_type in ['single_choice', 'multiple_choice']:
            if 'options' not in attrs or not attrs['options']:
                raise serializers.ValidationError('Options are required for choice questions.')

        if question_type == 'rating' and 'scale' not in attrs:
            raise serializers.ValidationError('Scale is required for rating questions.')

        return attrs

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        question = Question.objects.create(**validated_data)

        for option_data in options_data:
            Option.objects.create(question=question, **option_data)

        return question


class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Survey
        fields = [
            'id',
            'title',
            'description',
            'is_anonymous',
            'user_contact',
            'is_closed',
            'image_url',
            'questions',
        ]
        extra_kwargs = {'id': {'read_only': True}}
    
    def validate(self, attrs):
        questions = attrs.get('questions', [])
        if not attrs.get('is_anonymous') and not attrs.get('user_contact'):
            raise serializers.ValidationError('В неанонимных опросах нужно указать требуемый контакт')
        if not any(question.get('required') for question in questions):
            raise serializers.ValidationError('Опрос должен содержать хотя бы один обязательный вопрос')
        return attrs

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        creator = validated_data.pop('creator')
        survey = Survey.objects.create(creator=creator, **validated_data)

        for idx, question_data in enumerate(questions_data):
            options_data = question_data.pop('options', [])
            question = Question.objects.create(
                survey=survey,
                position=idx,
                **question_data
            )
            for option_data in options_data:
                Option.objects.create(question=question, **option_data)

        return survey
