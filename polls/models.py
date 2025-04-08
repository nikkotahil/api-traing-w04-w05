from django.db import models

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    created_by = models.ForeignKey('app_auth.AuthUser', on_delete=models.CASCADE)

    @property
    def is_valid(self):
        from django.utils import timezone
        return timezone.now() <= self.deadline

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Vote(models.Model):
    user = models.ForeignKey('app_auth.AuthUser', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f"{self.user.username} voted for {self.choice.choice_text} in '{self.question.question_text}'"
