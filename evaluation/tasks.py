import logging

from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from webproject.celery import app
from .models import AnswerData
from .calculate import Calculate


@app.task
def start_calculation(question, model_answer, answer, marks):
    calculate = Calculate()
    answer_data = AnswerData()
    answer_data.question = question
    answer_data.modelAnswer = model_answer
    answer_data.marks = marks
    answer_data.answer = answer
    answer_data.score = float("{0:.5f}".format(
        calculate.similarity(answer_data.modelAnswer, answer_data.answer, True) * answer_data.marks))
    answer_data.save()


# def send_verification_email(user_id):
#     UserModel = get_user_model()
#     try:
#         user = UserModel.objects.get(pk=user_id)
#         send_mail(
#             'Verify your QuickPublisher account',
#             'Follow this link to verify your account: '
#             'http://localhost:8000%s' % reverse('verify', kwargs={'uuid': str(user.verification_uuid)}),
#             'from@quickpublisher.dev',
#             [user.email],
#             fail_silently=False,
#         )
#     except UserModel.DoesNotExist:
#         logging.warning("Tried to send verification email to non-existing user '%s'" % user_id)
