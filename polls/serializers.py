from rest_framework import serializers
from polls.models import Question, Choice, Vote
from django.utils import timezone


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'votes']

    def validate_choice_text(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Choice text cannot be empty.")
        return value


class QuestionListSerializer(serializers.ModelSerializer):
    is_valid = serializers.ReadOnlyField()
    has_voted = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'pub_date', 'deadline', 'is_valid', 'has_voted']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def get_has_voted(self, obj):
        if self.user and self.user.is_authenticated:
            return obj.vote_set.filter(user=self.user).exists()
        return False


class QuestionDetailSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'pub_date', 'deadline', 'choices']


class QuestionCreateSerializer(serializers.ModelSerializer):
    choices = serializers.ListField(
        child=serializers.CharField(min_length=1), write_only=True
    )

    class Meta:
        model = Question
        fields = ['question_text', 'deadline', 'choices']

    def validate(self, data):
        if len(data.get('choices', [])) < 1:
            raise serializers.ValidationError('At least one choice is required.')
        return data

    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        question = Question.objects.create(created_by=self.context['request'].user, **validated_data)
        for choice_text in choices_data:
            Choice.objects.create(question=question, choice_text=choice_text)
        return question


class VoteSerializer(serializers.ModelSerializer):
    choice_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Vote
        fields = ['question', 'choice_id']

    def validate(self, data):
        user = self.context['request'].user
        question = data['question']

        if question.deadline < timezone.now():
            raise serializers.ValidationError('Voting deadline has passed.')

        if Vote.objects.filter(user=user, question=question).exists():
            raise serializers.ValidationError('You have already voted for this question.')

        return data


    def create(self, validated_data):
        user = self.context['request'].user
        question = validated_data['question']
        choice = Choice.objects.get(id=validated_data['choice_id'], question=question)

        vote = Vote.objects.create(user=user, question=question, choice=choice)
        choice.votes += 1
        choice.save()
        return vote
