import os

import pandas as pd
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, NotFound

from api_project_04_05 import settings
from polls.tasks import send_poll_report_email

from weasyprint import HTML

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


class QuestionExcelReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            raise NotFound('Poll not found.')

        data = []
        for choice in question.choices.all():
            data.append({'Choice': choice.choice_text, 'Votes': choice.votes})

        df = pd.DataFrame(data)

        from io import BytesIO
        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            sheet_name = 'Poll Report'
            df.to_excel(writer, sheet_name=sheet_name, startrow=3, index=False)
            worksheet = writer.sheets[sheet_name]

            worksheet.cell(row=1, column=1).value = "Question:"
            worksheet.cell(row=1, column=2).value = question.question_text

            worksheet.cell(row=2, column=1).value = "Deadline:"
            worksheet.cell(row=2, column=2).value = question.deadline.strftime('%Y-%m-%d %H:%M:%S')

        output.seek(0)

        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f'poll_report_{question.id}.xlsx'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class PollPDFReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            raise NotFound('Poll not found.')

        choices = question.choices.all()

        html_string = render_to_string('polls/poll_report.html', {
            'question': question,
            'choices': choices,
        })

        # Generate PDF
        html = HTML(string=html_string)
        pdf_file = html.write_pdf()

        # Create response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        filename = f"poll_{question.id}_report.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class SendPollReportEmailView(APIView):

    def post(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            raise NotFound("Poll not found.")

        output_dir = os.path.join(settings.BASE_DIR, 'media')
        os.makedirs(output_dir, exist_ok=True)

        excel_path = os.path.join(output_dir, f'poll_{pk}_report.xlsx')
        data = [{'Choices': c.choice_text, 'Votes': c.votes} for c in question.choices.all()]
        df = pd.DataFrame(data)
        df.to_excel(excel_path, index=False, engine='openpyxl', startrow=1)
        df.columns = ['Choices', 'Votes']  # Force columns again just in case

        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            sheet = writer.sheets['Sheet1']
            sheet.cell(row=1, column=1).value = f"Question: {question.question_text}"
            sheet.cell(row=2, column=1).value = f"Deadline: {question.deadline.strftime('%Y-%m-%d')}"

        subject = "Poll Report"
        message = "Attached is the poll report."
        to_email = "nikko1nurse@gmail.com"

        send_poll_report_email.delay(subject, message, to_email, excel_path, os.path.basename(excel_path))

        return Response({'message': 'POST SendPollReportEmailView'})
