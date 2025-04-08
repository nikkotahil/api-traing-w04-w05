from django.contrib import admin
from .models import Question, Choice, Vote
from django.utils import timezone

class IsValidPollFilter(admin.SimpleListFilter):
    title = 'Poll Validity'
    parameter_name = 'valid'

    def lookups(self, request, model_admin):
        return (
            ('valid', 'Valid'),
            ('expired', 'Expired'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'valid':
            return queryset.filter(deadline__gte=now)
        if self.value() == 'expired':
            return queryset.filter(deadline__lt=now)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'deadline', 'is_valid')
    list_filter = (IsValidPollFilter,)


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'question', 'votes']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'choice']

