from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from polls.models import Question
from polls.serializers import (
    QuestionListSerializer,
    QuestionDetailSerializer,
    QuestionCreateSerializer,
    VoteSerializer
)


class QuestionListView(generics.ListAPIView):
    serializer_class = QuestionListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Question.objects.all()

    def get_serializer(self, *args, **kwargs):
        kwargs['user'] = self.request.user
        return super().get_serializer(*args, **kwargs)


class QuestionDetailView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


class QuestionCreateView(generics.CreateAPIView):
    serializer_class = QuestionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.user_type != 'admin':
            raise PermissionDenied("Only admins can create questions.")
        serializer.save()


class VoteCreateView(generics.CreateAPIView):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class VotedPollsView(generics.ListAPIView):
    serializer_class = QuestionListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Question.objects.filter(vote__user=self.request.user).distinct()

    def get_serializer_context(self):
        return {'user': self.request.user}
