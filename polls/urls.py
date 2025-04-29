from django.urls import path
from polls import views

urlpatterns = [
    path('', views.QuestionListView.as_view(), name='question-list'),
    path('<int:pk>/', views.QuestionDetailView.as_view(), name='question-detail'),
    path('create/', views.QuestionCreateView.as_view(), name='question-create'),
    path('vote/', views.VoteCreateView.as_view(), name='vote'),
    path('voted/', views.VotedPollsView.as_view(), name='voted-polls'),
    path('<int:pk>/report/', views.QuestionExcelReportView.as_view(), name='poll-excel-report'),
    path('<int:pk>/report/pdf/', views.PollPDFReportView.as_view(), name='poll-pdf-report'),
    path('<int:pk>/send-email/', views.SendPollReportEmailView.as_view(), name='send-poll-report-email'),
]
